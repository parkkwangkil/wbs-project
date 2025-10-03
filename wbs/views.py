from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.db.models import Q, F
from .models import Project, ProjectPhase, ApprovalLine, Comment, ProjectDocument, DailyProgress, TaskChecklistItem, UserProfile, Notification, SubscriptionPlan, UserSubscription, AdCampaign, Event
from .forms import ProjectForm, ProjectPhaseForm, CommentForm, DailyProgressForm, TaskChecklistItemForm, UserProfileForm, UserForm, SubscriptionPlanForm, UserSubscriptionForm, AdCampaignForm, EventForm, EventAttendeesForm, PersonalTaskForm
from datetime import datetime, timedelta, date
import json

# Flutter 앱용 JSON API 엔드포인트들
@csrf_exempt
def api_projects(request):
    """프로젝트 목록 JSON API"""
    if request.method == 'GET':
        projects = Project.objects.all()
        data = []
        for project in projects:
            data.append({
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'status': project.status,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'manager': project.manager.username if project.manager else None,
            })
        return JsonResponse({'projects': data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_events(request):
    """이벤트 목록 JSON API"""
    if request.method == 'GET':
        events = Event.objects.all()
        data = []
        for event in events:
            data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_time': event.start_time.isoformat() if event.start_time else None,
                'end_time': event.end_time.isoformat() if event.end_time else None,
                'location': event.location,
                'created_at': event.created_at.isoformat(),
            })
        return JsonResponse({'events': data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_users(request):
    """사용자 목록 JSON API"""
    if request.method == 'GET':
        users = User.objects.all()
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined.isoformat(),
            })
        return JsonResponse({'users': data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def custom_login(request):
    """커스텀 로그인 페이지"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '로그인에 성공했습니다!')
                return redirect('wbs:home')
            else:
                messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
        else:
            messages.error(request, '아이디와 비밀번호를 입력해주세요.')
    
    return render(request, 'wbs/custom_login.html')

def custom_logout(request):
    """커스텀 로그아웃 페이지"""
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'wbs/logout_success.html')
    else:
        return redirect('wbs:custom_login')

@login_required
def home(request):
    """홈페이지 뷰"""
    # 통계 데이터
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    total_comments = Comment.objects.count()
    
    # 최근 프로젝트 (최대 5개)
    recent_projects = Project.objects.order_by('-created_at')[:5]
    
    # 승인 대기 중인 프로젝트
    pending_approvals = Project.objects.filter(
        Q(approval_lines__status='pending') | Q(approval_lines__status='in_review')
    ).distinct()[:5]
    
    # 월별 프로젝트 통계
    today = timezone.now()
    monthly_projects = Project.objects.filter(
        start_date__year=today.year,
        start_date__month=today.month
    )
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_comments': total_comments,
        'recent_projects': recent_projects,
        'pending_approvals': pending_approvals,
        'monthly_projects': monthly_projects,
        'current_month': today.strftime('%Y년 %m월'),
    }
    
    return render(request, 'wbs/home.html', context)

def project_list(request):
    """프로젝트 목록"""
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'wbs/project_list.html', {'projects': projects})

@login_required
def team_projects(request):
    """내가 관리하거나 참여 중인 팀 프로젝트 목록"""
    # 팀 프로젝트: 기본은 팀 프로젝트(True) + 내가 관리/참여한 것
    # 단, 내가 팀원으로 포함된 프로젝트는 is_team_project 여부와 상관없이 표시(참여 관점)
    projects = Project.objects.filter(
        Q(manager=request.user) |
        Q(team_members=request.user) |
        Q(tl=request.user) |
        Q(phases__assignees=request.user)
    ).filter(
        Q(is_team_project=True) |
        Q(team_members=request.user) |
        Q(tl=request.user) |
        Q(phases__assignees=request.user)
    ).distinct().order_by('-updated_at', '-created_at')

    # id 쿼리 파라미터가 오면 해당 프로젝트 상세로 이동 (권한 확인)
    target_id = request.GET.get('id')
    if target_id:
        try:
            target = projects.get(pk=target_id)
            return redirect('wbs:project_detail', pk=target.pk)
        except Project.DoesNotExist:
            pass

    # 항상 목록을 보여주어 참여 중인 프로젝트를 한눈에 볼 수 있게 한다
    return render(request, 'wbs/team_projects.html', {'projects': projects})

@login_required
def personal_projects(request):
    """내가 관리하는 개인 프로젝트 목록 (팀과 별개)"""
    projects = Project.objects.filter(manager=request.user, is_personal_project=True).order_by('-updated_at', '-created_at')

    target_id = request.GET.get('id')
    if target_id:
        try:
            target = projects.get(pk=target_id)
            return redirect('wbs:project_detail', pk=target.pk)
        except Project.DoesNotExist:
            pass

    first_project = projects.first()
    if first_project:
        return redirect('wbs:project_detail', pk=first_project.pk)

    return render(request, 'wbs/personal_projects.html', {'projects': projects})

def project_detail(request, pk):
    """프로젝트 상세"""
    project = get_object_or_404(Project, pk=pk)
    phases = project.phases.all().order_by('order')
    comments = project.comments.all().order_by('-created_at')
    documents = project.documents.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 추가되었습니다.')
            return redirect('wbs:project_detail', pk=pk)
    else:
        form = CommentForm()
    
    # 타임라인 바 위치(좌표) 사전 계산
    # 주간 전용: 기준 주(월~일) 계산 (쿼리스트링 week=YYYY-MM-DD 지원)
    base_str = request.GET.get('week')
    try:
        base_date = datetime.strptime(base_str, '%Y-%m-%d').date() if base_str else timezone.localdate()
    except Exception:
        base_date = timezone.localdate()
    week_start = base_date - timedelta(days=base_date.weekday())
    week_end = week_start + timedelta(days=6)
    px_per_day = 100
    phase_rows = []
    for ph in phases:
        # 주간과 겹치지 않으면 표시하지 않음
        if ph.end_date < week_start or ph.start_date > week_end:
            continue
        start = max(ph.start_date, week_start)
        end = min(ph.end_date, week_end)
        left = (start - week_start).days * px_per_day
        width = ((end - start).days + 1) * px_per_day
        owners = ", ".join(u.username for u in getattr(ph, 'assignees', []).all()) if hasattr(ph, 'assignees') else project.manager.username
        phase_rows.append({
            'id': ph.id,
            'title': ph.title,
            'description': getattr(ph, 'description', ''),
            'team': getattr(ph, 'team_name', ''),
            'daily_hours': getattr(ph, 'daily_hours', 8),
            'status': getattr(ph, 'status', 'planned'),
            'progress': getattr(ph, 'progress', 0),
            'start_date': ph.start_date,
            'end_date': ph.end_date,
            'owner': owners or project.manager.username,
            'part': getattr(ph, 'team_name', ''),
            'left': left,
            'width': width,
        })

    # 개인 작업은 주간 WBS에서 제외

    context = {
        'project': project,
        'phases': phases,
        'phase_rows': phase_rows,
        'comments': comments,
        'documents': documents,
        'form': form,
        'px_per_day': px_per_day,
        'week_start': week_start,
        'week_end': week_end,
        'prev_week': (week_start - timedelta(days=7)).strftime('%Y-%m-%d'),
        'next_week': (week_start + timedelta(days=7)).strftime('%Y-%m-%d'),
        'week_days': [(week_start + timedelta(days=i)) for i in range(7)],
    }
    
    return render(request, 'wbs/project_detail.html', context)

@login_required
def personal_task_add(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = PersonalTaskForm(request.POST)
        if form.is_valid():
            pt = form.save(commit=False)
            pt.project = project
            pt.save()
            form.save_m2m()
            messages.success(request, '작업 항목이 추가되었습니다.')
            return redirect('wbs:project_detail', pk=project_pk)
    else:
        form = PersonalTaskForm()
    return render(request, 'wbs/personal_task_form.html', { 'form': form, 'project': project })

def project_create(request):
    """프로젝트 생성"""
    # 구독 플랜 확인
    user_subscription = getattr(request.user, 'subscription', None)
    if user_subscription and not user_subscription.can_create_project():
        messages.error(request, f'프로젝트 생성 한도에 도달했습니다. 현재 플랜에서는 최대 {user_subscription.plan.max_projects}개의 프로젝트만 생성할 수 있습니다.')
        return redirect('wbs:subscription_plans')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            
            # 프로젝트 생성 수 증가
            if user_subscription:
                user_subscription.projects_created += 1
                user_subscription.save()
            
            messages.success(request, '프로젝트가 생성되었습니다.')
            return redirect('wbs:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'user_subscription': user_subscription,
    }
    return render(request, 'wbs/project_form.html', context)

def project_edit(request, pk):
    """프로젝트 편집"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, '프로젝트가 수정되었습니다.')
            return redirect('wbs:project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'wbs/project_form.html', {'form': form})

@login_required
def project_delete(request, pk):
    """프로젝트 삭제 확인 및 처리"""
    project = get_object_or_404(Project, pk=pk)
    # 권한 체크: 관리자 또는 프로젝트 매니저만 삭제 가능
    if not (request.user.is_staff or request.user == project.manager):
        messages.error(request, '삭제 권한이 없습니다.')
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('wbs:project_detail', args=[pk])
        return redirect(next_url)
    if request.method == 'POST' or request.GET.get('confirm') == '1':
        title = project.title
        project.delete()
        messages.success(request, f'프로젝트 "{title}" 가 삭제되었습니다.')
        # AJAX 요청 대응
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': str(request.build_absolute_uri(reverse('wbs:project_list')))})
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        # 기본: 간단한 완료 페이지로 안내 후 메인으로 이동
        return render(request, 'wbs/deleted_success.html', {
            'message': '프로젝트가 삭제되었습니다. 메인 페이지로 이동합니다.',
            'redirect_url': reverse('wbs:home')
        })
    return render(request, 'wbs/project_confirm_delete.html', { 'project': project })

def phase_create(request, project_pk):
    """프로젝트 단계 생성"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.method == 'POST':
        form = ProjectPhaseForm(request.POST)
        if form.is_valid():
            phase = form.save(commit=False)
            phase.project = project
            phase.save()
            messages.success(request, '프로젝트 단계가 추가되었습니다.')
            return redirect('wbs:project_detail', pk=project_pk)
        else:
            messages.error(request, '폼에 오류가 있습니다. 다시 확인해주세요.')
    else:
        form = ProjectPhaseForm()
    
    return render(request, 'wbs/phase_form.html', {'form': form, 'project': project})

def phase_edit(request, project_pk, phase_pk):
    """프로젝트 단계 편집"""
    project = get_object_or_404(Project, pk=project_pk)
    phase = get_object_or_404(ProjectPhase, pk=phase_pk, project=project)
    
    if request.method == 'POST':
        form = ProjectPhaseForm(request.POST, instance=phase)
        if form.is_valid():
            form.save()
            messages.success(request, '프로젝트 단계가 수정되었습니다.')
            return redirect('wbs:project_detail', pk=project_pk)
        else:
            messages.error(request, '폼에 오류가 있습니다. 다시 확인해주세요.')
    else:
        form = ProjectPhaseForm(instance=phase)
    
    return render(request, 'wbs/phase_form.html', {'form': form, 'project': project})

def calendar(request):
    """캘린더 뷰 - 달력 셀과 일자별 프로젝트/이벤트를 렌더링하기 위한 컨텍스트 복구"""
    import calendar as cal_module
    from datetime import date as date_cls

    today_dt = timezone.localdate()
    year = int(request.GET.get('year', today_dt.year))
    month = int(request.GET.get('month', today_dt.month))

    first_day = date_cls(year, month, 1)
    last_day = date_cls(year, month, cal_module.monthrange(year, month)[1])

    # 월 범위에 걸치는 프로젝트/이벤트 조회
    projects = Project.objects.filter(
        Q(start_date__lte=last_day) & Q(end_date__gte=first_day)
    ).order_by('start_date')

    events = Event.objects.filter(
        Q(start_date__lte=last_day) & Q(end_date__gte=first_day)
    ).order_by('start_date')

    # 사용자 프로젝트 (고급 추가 모달용)
    user_projects = Project.objects.all()
    if request.user.is_authenticated:
        user_projects = Project.objects.filter(Q(manager=request.user) | Q(team_members=request.user)).distinct()

    # 주 단위 달력 데이터 구성 (해당 월 외 날짜는 None 처리)
    weeks = []
    for week_dates in cal_module.Calendar().monthdatescalendar(year, month):
        week = []
        for d in week_dates:
            if d.month != month:
                week.append(None)
            else:
                day_projects = [p for p in projects if p.start_date <= d <= p.end_date]
                day_events = [e for e in events if e.start_date <= d <= e.end_date]
                week.append({
                    'date': d,
                    'day': d.day,
                    'is_today': (d == today_dt),
                    'projects': day_projects,
                    'events': day_events,
                })
        weeks.append(week)

    month_name = cal_module.month_name[month]

    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'projects': projects,
        'calendar_weeks': weeks,
        'week_bars': [],  # 기본 비활성
        'show_projects': True,
        'show_events': False,
        'show_bars': False,
        'today': today_dt,
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
        'user_projects': user_projects,
    }

    return render(request, 'wbs/calendar.html', context)

def progress_calendar(request, project_pk):
    """프로젝트 진행상황 캘린더 (1-31일)"""
    project = get_object_or_404(Project, pk=project_pk)
    
    # 해당 프로젝트의 일별 진행상황
    daily_progress = DailyProgress.objects.filter(project=project).order_by('date')
    
    # 체크리스트 항목들
    checklist_items = TaskChecklistItem.objects.filter(project=project).order_by('order')
    
    context = {
        'project': project,
        'daily_progress': daily_progress,
        'checklist_items': checklist_items,
    }
    
    return render(request, 'wbs/progress_calendar.html', context)

def daily_progress_update(request, project_pk, date_str=None):
    """일별 진행상황 업데이트"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.method == 'POST':
        # POST 요청: 데이터 저장
        if not date_str:
            date_str = request.POST.get('date')
        
        progress = request.POST.get('progress', 0)
        notes = request.POST.get('notes', '')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            daily_progress, created = DailyProgress.objects.get_or_create(
                project=project,
                date=date,
                defaults={'progress': int(progress), 'notes': notes}
            )
            
            if not created:
                daily_progress.progress = int(progress)
                daily_progress.notes = notes
                daily_progress.save()
            
            return JsonResponse({'success': True, 'message': '진행상황이 저장되었습니다.'})
        except ValueError:
            return JsonResponse({'success': False, 'message': '잘못된 날짜 형식입니다.'})
    
    else:
        # GET 요청: 폼 표시
        if not date_str:
            return redirect('wbs:progress_calendar', project_pk=project_pk)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            daily_progress = DailyProgress.objects.filter(project=project, date=date).first()
            
            context = {
                'project': project,
                'date': date,
                'date_str': date_str,
                'daily_progress': daily_progress,
            }
            return render(request, 'wbs/daily_progress_form.html', context)
        except ValueError:
            return redirect('wbs:progress_calendar', project_pk=project_pk)

@require_POST
def checklist_toggle(request, project_pk):
    """체크리스트 항목 토글"""
    project = get_object_or_404(Project, pk=project_pk)
    item_id = request.POST.get('item_id')
    is_completed = request.POST.get('is_completed') == 'true'
    
    try:
        item = TaskChecklistItem.objects.get(id=item_id, project=project)
        item.is_completed = is_completed
        item.save()
        
        return JsonResponse({'success': True, 'message': '체크리스트가 업데이트되었습니다.'})
    except TaskChecklistItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': '항목을 찾을 수 없습니다.'})

def approve_request(request, approval_pk):
    """승인 요청 처리"""
    approval = get_object_or_404(ApprovalLine, pk=approval_pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            approval.status = 'approved'
            approval.approved_by = request.user
            approval.approved_at = timezone.now()
            approval.save()
            messages.success(request, '승인되었습니다.')
        elif action == 'reject':
            approval.status = 'rejected'
            approval.approved_by = request.user
            approval.approved_at = timezone.now()
            approval.save()
            messages.success(request, '거부되었습니다.')
        
        return redirect('wbs:project_detail', pk=approval.project.pk)
    
    return render(request, 'wbs/approval_form.html', {'approval': approval})

def profile_view(request):
    """사용자 프로필 보기"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'wbs/profile.html', context)

def profile_edit(request):
    """사용자 프로필 편집"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('wbs:profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'wbs/profile_edit.html', context)

def user_list(request):
    """사용자 목록"""
    users = User.objects.all().order_by('username')
    context = {
        'users': users,
    }
    return render(request, 'wbs/user_list.html', context)

def user_detail(request, user_id):
    """사용자 상세 정보"""
    user = get_object_or_404(User, id=user_id)
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None
    
    # 사용자가 관리하는 프로젝트들
    managed_projects = Project.objects.filter(manager=user).order_by('-created_at')[:5]
    
    # 사용자가 작성한 댓글들
    recent_comments = Comment.objects.filter(author=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'profile': profile,
        'managed_projects': managed_projects,
        'recent_comments': recent_comments,
    }
    return render(request, 'wbs/user_detail.html', context)

@login_required
def notifications(request):
    """알림 목록"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'wbs/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """알림을 읽음으로 표시"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': '알림을 찾을 수 없습니다.'})

@login_required
@require_POST
def mark_all_notifications_read(request):
    """모든 알림을 읽음으로 표시"""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, 
        read_at=timezone.now()
    )
    return JsonResponse({'success': True})

@login_required
def get_notifications_count(request):
    """읽지 않은 알림 개수 조회 (AJAX)"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

# 구독 관련 뷰들
@login_required
def subscription_plans(request):
    """구독 플랜 목록"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    user_subscription = getattr(request.user, 'subscription', None)
    
    context = {
        'plans': plans,
        'user_subscription': user_subscription,
    }
    return render(request, 'wbs/subscription_plans.html', context)

@login_required
def subscription_detail(request, plan_id):
    """구독 플랜 상세"""
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    user_subscription = getattr(request.user, 'subscription', None)
    
    context = {
        'plan': plan,
        'user_subscription': user_subscription,
    }
    return render(request, 'wbs/subscription_detail.html', context)

@login_required
def subscribe(request, plan_id):
    """구독 신청"""
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    
    if request.method == 'POST':
        # 결제 처리 (실제로는 결제 API 연동 필요)
        payment_method = request.POST.get('payment_method', 'card')
        
        # 기존 구독이 있으면 업데이트, 없으면 생성
        user_subscription, created = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'status': 'active',
                'payment_method': payment_method,
                'end_date': timezone.now() + timedelta(days=30 if plan.billing_cycle == 'monthly' else 365),
            }
        )
        
        if not created:
            user_subscription.plan = plan
            user_subscription.status = 'active'
            user_subscription.payment_method = payment_method
            user_subscription.end_date = timezone.now() + timedelta(days=30 if plan.billing_cycle == 'monthly' else 365)
            user_subscription.save()
        
        messages.success(request, f'{plan.display_name} 플랜으로 구독되었습니다!')
        return redirect('wbs:subscription_plans')
    
    context = {
        'plan': plan,
    }
    return render(request, 'wbs/subscribe.html', context)

@login_required
def my_subscription(request):
    """내 구독 정보"""
    user_subscription = getattr(request.user, 'subscription', None)
    
    if not user_subscription:
        messages.info(request, '구독 정보가 없습니다. 플랜을 선택해주세요.')
        return redirect('wbs:subscription_plans')
    
    # 가짜 결제 이력 (데모용)
    # 실제 결제 연동 시에는 Payment 모델/웹훅 기반으로 대체
    now = timezone.now()
    amount = user_subscription.plan.price
    currency = user_subscription.plan.currency
    payments = [
        {
            'paid_at': (now - timedelta(days=60)).strftime('%Y-%m-%d %H:%M'),
            'amount': amount,
            'currency': currency,
            'method': user_subscription.payment_method or 'card',
            'payment_id': f'DEMO-{user_subscription.user_id}-001',
            'status': 'paid',
        },
        {
            'paid_at': (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M'),
            'amount': amount,
            'currency': currency,
            'method': user_subscription.payment_method or 'card',
            'payment_id': f'DEMO-{user_subscription.user_id}-002',
            'status': 'paid',
        },
        {
            'paid_at': now.strftime('%Y-%m-%d %H:%M'),
            'amount': amount,
            'currency': currency,
            'method': user_subscription.payment_method or 'card',
            'payment_id': f'DEMO-{user_subscription.user_id}-003',
            'status': 'paid',
        },
    ]

    context = {
        'user_subscription': user_subscription,
        'payments': payments,
    }
    return render(request, 'wbs/my_subscription.html', context)

@login_required
def cancel_subscription(request):
    """구독 취소"""
    user_subscription = getattr(request.user, 'subscription', None)
    
    if not user_subscription:
        messages.error(request, '구독 정보가 없습니다.')
        return redirect('wbs:subscription_plans')
    
    if request.method == 'POST':
        user_subscription.status = 'cancelled'
        user_subscription.auto_renew = False
        user_subscription.save()
        
        messages.success(request, '구독이 취소되었습니다.')
        return redirect('wbs:my_subscription')
    
    context = {
        'user_subscription': user_subscription,
    }
    return render(request, 'wbs/cancel_subscription.html', context)

# 광고 관련 뷰들
def get_ads_for_user(request, position='sidebar'):
    """사용자에게 표시할 광고 조회"""
    user_subscription = getattr(request.user, 'subscription', None) if request.user.is_authenticated else None
    
    # 무료 플랜 사용자에게만 광고 표시
    if user_subscription and user_subscription.plan.name != 'free':
        return []
    
    # 현재 페이지 경로
    current_path = request.path
    
    # 실행 중인 광고 캠페인 조회
    ads = AdCampaign.objects.filter(
        position=position,
        status='active',
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        current_impressions__lt=F('max_impressions')
    ).order_by('?')[:3]  # 랜덤으로 최대 3개
    
    # 노출 기록
    for ad in ads:
        ad.record_impression()
    
    return ads

@login_required
def ad_click(request, ad_id):
    """광고 클릭 처리"""
    ad = get_object_or_404(AdCampaign, pk=ad_id)
    ad.record_click()
    
    return redirect(ad.target_url)

@login_required
def search(request):
    """통합 검색 기능"""
    query = request.GET.get('q', '').strip()
    results = {}
    
    if query:
        # 프로젝트 검색
        projects = Project.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        ).select_related('manager')[:10]
        
        # 사용자 검색 (관리자만)
        users = []
        if request.user.is_staff:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )[:10]
        
        # 알림 검색
        notifications = Notification.objects.filter(
            user=request.user,
            message__icontains=query
        ).order_by('-created_at')[:10]
        
        results = {
            'projects': projects,
            'users': users,
            'notifications': notifications,
            'query': query,
            'total_count': len(projects) + len(users) + len(notifications)
        }
    
    return render(request, 'wbs/search_results.html', results)

# ----- 일정(Event) 뷰 최소 복구 -----
from django.views.decorators.http import require_http_methods

@login_required
def event_list(request):
    events = Event.objects.filter(creator=request.user).order_by('-start_date')[:100]
    return render(request, 'wbs/event_list.html', {'events': events})

@login_required
@require_http_methods(["GET", "POST"])
def event_create(request):
    attendees_form = None
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        attendees_form = EventAttendeesForm(request.POST, user=request.user)
        if form.is_valid() and attendees_form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.end_date = event.end_date or event.start_date
            event.save()
            form.save_m2m()
            event.attendees.set(attendees_form.cleaned_data.get('attendees'))
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'id': event.id})
            messages.success(request, '일정이 생성되었습니다.')
            return redirect('wbs:event_detail', pk=event.pk)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': {**form.errors, **attendees_form.errors}}, status=400)
    else:
        form = EventForm(user=request.user)
        attendees_form = EventAttendeesForm(user=request.user)
    return render(request, 'wbs/event_form.html', {'form': form, 'attendees_form': attendees_form, 'title': '새 일정 생성'})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'wbs/event_detail.html', {'event': event})

@login_required
@require_http_methods(["GET", "POST"])
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    attendees_form = None
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        attendees_form = EventAttendeesForm(request.POST, user=request.user)
        if form.is_valid() and attendees_form.is_valid():
            form.save()
            event.attendees.set(attendees_form.cleaned_data.get('attendees'))
            messages.success(request, '일정이 수정되었습니다.')
            return redirect('wbs:event_detail', pk=pk)
    else:
        form = EventForm(instance=event, user=request.user)
        attendees_form = EventAttendeesForm(user=request.user, initial={'attendees': event.attendees.all()})
    return render(request, 'wbs/event_form.html', {'form': form, 'attendees_form': attendees_form, 'event': event, 'title': '일정 수정'})

@login_required
@require_http_methods(["GET", "POST"])
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # 권한: 생성자 또는 스태프만 삭제 허용
    if not (request.user.is_staff or event.creator_id == request.user.id):
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('wbs:event_detail', pk=pk)
    title = event.title
    event.delete()
    messages.success(request, f'일정 "{title}" 이(가) 삭제되었습니다.')
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('wbs:event_list')

@login_required
@require_http_methods(["POST"])
def event_toggle_complete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.is_completed = not event.is_completed
    event.save()
    return JsonResponse({'success': True, 'is_completed': event.is_completed})

@login_required
@require_http_methods(["POST"])
def event_quick_create(request):
    title = request.POST.get('title', '').strip()
    start_date = request.POST.get('start_date')
    if not title or not start_date:
        return JsonResponse({'success': False, 'error': '제목과 날짜가 필요합니다.'}, status=400)
    try:
        sd = datetime.strptime(start_date, '%Y-%m-%d').date()
        event = Event.objects.create(
            title=title,
            start_date=sd,
            end_date=sd,
            creator=request.user,
        )
        return JsonResponse({'success': True, 'id': event.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def event_range_selector(request):
    # 간단한 선택 템플릿 렌더링 (이미 템플릿 존재)
    return render(request, 'wbs/event_range_selector.html')

# ----- 개인 플래너 / 프로젝트 플래너 -----
@login_required
def personal_planner(request):
    # 주간 전용
    mode = 'week'
    try:
        start_str = request.GET.get('start')
        base_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else timezone.localdate()
    except Exception:
        base_date = timezone.localdate()

    # week only
    start_date = base_date - timedelta(days=base_date.weekday())
    end_date = start_date + timedelta(days=6)
    px_per_day = 100

    days = []
    current = start_date
    left_px = 0
    while current <= end_date:
        days.append((current, left_px))
        left_px += px_per_day
        current += timedelta(days=1)

    # 사용자의 이벤트를 표 형태로 간단히 구성
    events = Event.objects.filter(creator=request.user, start_date__lte=end_date, end_date__gte=start_date).order_by('start_date')
    rows = []
    for ev in events:
        # 주간과 겹치지 않으면 스킵
        if ev.end_date < start_date or ev.start_date > end_date:
            continue
        start = max(ev.start_date, start_date)
        end = min(ev.end_date, end_date)
        left = (start - start_date).days * px_per_day
        width = ((end - start).days + 1) * px_per_day
        color = ev.priority_color
        rows.append({
            'category': ev.get_event_type_display(),
            'title': ev.title,
            'part': '-',
            'owner': request.user.username,
            'start': ev.start_date,
            'end': ev.end_date,
            'days': (ev.end_date - ev.start_date).days + 1,
            'progress': 0,
            'left': left,
            'width': width,
            'color': color,
        })

    context = {
        'mode': mode,
        'start_date': start_date,
        'end_date': end_date,
        'days_with_pos': days,
        'px_per_day': px_per_day,
        'rows': rows,
        'prev_start': (start_date - timedelta(days=7)).strftime('%Y-%m-%d') if mode == 'week' else (start_date - timedelta(days=30)).strftime('%Y-%m-%d'),
        'next_start': (start_date + timedelta(days=7)).strftime('%Y-%m-%d') if mode == 'week' else (start_date + timedelta(days=30)).strftime('%Y-%m-%d'),
    }
    return render(request, 'wbs/personal_planner.html', context)

@login_required
def project_planner(request, pk):
    project = get_object_or_404(Project, pk=pk)
    mode = request.GET.get('mode', 'week')
    start_date = project.start_date
    end_date = project.end_date
    px_per_day = 24 if mode == 'month' else 40

    days = []
    current = start_date
    left_px = 0
    while current <= end_date:
        days.append((current, left_px))
        left_px += px_per_day
        current += timedelta(days=1)

    # 프로젝트 단계 기반의 바 구성
    rows = []
    for ph in project.phases.all().order_by('order'):
        start = max(ph.start_date, start_date)
        end = max(start, min(ph.end_date, end_date))
        left = (start - start_date).days * px_per_day
        width = ((end - start).days + 1) * px_per_day
        rows.append({
            'category': 'Phase',
            'title': ph.title,
            'part': '-',
            'owner': project.manager.username,
            'start': ph.start_date,
            'end': ph.end_date,
            'days': (ph.end_date - ph.start_date).days + 1,
            'progress': 0,
            'left': left,
            'width': width,
            'color': project.theme_color,
        })

    context = {
        'project': project,
        'mode': mode,
        'start_date': start_date,
        'end_date': end_date,
        'days_with_pos': days,
        'px_per_day': px_per_day,
        'rows': rows,
        'prev_start': start_date.strftime('%Y-%m-%d'),
        'next_start': start_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'wbs/personal_planner.html', context)

@login_required
def personal_project_detail(request, pk):
    """개인 플래너 디자인의 신규 상세 화면 (주/월 토글, 작업 항목 표시)"""
    project = get_object_or_404(Project, pk=pk)
    mode = request.GET.get('mode', 'week')
    try:
        start_str = request.GET.get('start')
        base_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else timezone.localdate()
    except Exception:
        base_date = timezone.localdate()

    if mode == 'month':
        start_date = base_date.replace(day=1)
        from calendar import monthrange
        end_date = start_date.replace(day=monthrange(start_date.year, start_date.month)[1])
        px_per_day = 24
    else:
        start_date = base_date - timedelta(days=base_date.weekday())
        end_date = start_date + timedelta(days=6)
        px_per_day = 100

    # 타임라인 헤더 좌표
    days_with_pos = []
    current = start_date
    left_px = 0
    while current <= end_date:
        days_with_pos.append((current, left_px))
        left_px += px_per_day
        current += timedelta(days=1)

    # 월간 모드에서 상단 주 단위 셀(1주, 2주, ...) 표시용 데이터
    week_cells = []
    if mode == 'month':
        week_index = 1
        week_start = start_date
        while week_start <= end_date:
            week_cells.append({'label': f"{week_index}주"})
            week_start += timedelta(days=7)
            week_index += 1

    # 개인 작업과 프로젝트 단계 모두 보여주기
    rows = []
    # PersonalTask rows
    for t in project.personal_tasks.all().order_by('start_date'):
        s = max(t.start_date, start_date)
        e = max(s, min(t.end_date, end_date))
        left = (s - start_date).days * px_per_day
        width = ((e - s).days + 1) * px_per_day
        assignees = ", ".join([u.username for u in t.assignees.all()])
        row = {
            'category': t.team_name,
            'title': t.content,
            'part': t.team_name,
            'owner': assignees or '-',
            'start': t.start_date,
            'end': t.end_date,
            'days': (t.end_date - t.start_date).days + 1,
            'progress': t.get_progress_display(),
            'left': left,
            'width': width,
            'color': project.theme_color,
        }
        if mode == 'week':
            start_offset = (s - start_date).days
            span_days = (e - s).days + 1
            row['grid_col_start'] = start_offset + 1
            row['grid_span'] = span_days
        rows.append(row)

    # 단계도 함께 (선택)
    for ph in project.phases.all().order_by('order'):
        s = max(ph.start_date, start_date)
        e = max(s, min(ph.end_date, end_date))
        left = (s - start_date).days * px_per_day
        width = ((e - s).days + 1) * px_per_day
        row = {
            'category': 'Phase',
            'title': ph.title,
            'part': '-',
            'owner': project.manager.username,
            'start': ph.start_date,
            'end': ph.end_date,
            'days': (ph.end_date - ph.start_date).days + 1,
            'progress': '—',
            'left': left,
            'width': width,
            'color': project.theme_color,
        }
        if mode == 'week':
            start_offset = (s - start_date).days
            span_days = (e - s).days + 1
            row['grid_col_start'] = start_offset + 1
            row['grid_span'] = span_days
        rows.append(row)

    context = {
        'project': project,
        'mode': mode,
        'start_date': start_date,
        'end_date': end_date,
        'days_with_pos': days_with_pos,
        'week_cells': week_cells,
        'num_weeks': len(week_cells) if mode == 'month' else 0,
        'px_per_day': px_per_day,
        'week_px': 7 * px_per_day,
        'day_count': len(days_with_pos),
        'rows': rows,
        'prev_start': (start_date - timedelta(days=7)).strftime('%Y-%m-%d') if mode == 'week' else (start_date - timedelta(days=30)).strftime('%Y-%m-%d'),
        'next_start': (start_date + timedelta(days=7)).strftime('%Y-%m-%d') if mode == 'week' else (start_date + timedelta(days=30)).strftime('%Y-%m-%d'),
    }
    return render(request, 'wbs/personal_project_detail.html', context)