from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, F
from .models import Project, ProjectPhase, ApprovalLine, Comment, ProjectDocument, DailyProgress, TaskChecklistItem, UserProfile, Notification, SubscriptionPlan, UserSubscription, AdCampaign, Event
from .forms import ProjectForm, ProjectPhaseForm, CommentForm, DailyProgressForm, TaskChecklistItemForm, UserProfileForm, UserForm, SubscriptionPlanForm, UserSubscriptionForm, AdCampaignForm, EventForm, EventAttendeesForm
from datetime import datetime, timedelta, date
import json

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
    
    context = {
        'project': project,
        'phases': phases,
        'comments': comments,
        'documents': documents,
        'form': form,
    }
    
    return render(request, 'wbs/project_detail.html', context)

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
    """캘린더 뷰 (프로젝트 + 일정 통합)"""
    import calendar as cal_module
    from datetime import datetime, date
    
    today = timezone.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    # 간결 모드: 토글 제거, 항상 프로젝트/일정 표시, 주간바 숨김
    show_projects = True
    show_events = True
    show_bars = False
    exclude_keyword = ''
    
    # 월별 프로젝트들 (시작일 또는 종료일이 해당 월에 포함되는 프로젝트들)
    projects = Project.objects.filter(
        Q(start_date__year=year, start_date__month=month) |
        Q(end_date__year=year, end_date__month=month) |
        Q(start_date__lte=date(year, month, 1), end_date__gte=date(year, month, cal_module.monthrange(year, month)[1]))
    ).order_by('start_date')
    if exclude_keyword:
        projects = projects.exclude(title__icontains=exclude_keyword)
    
    # 사용자가 참여한 모든 프로젝트 (일정 생성 시 선택용)
    user_projects = Project.objects.filter(
        Q(manager=request.user) | Q(team_members=request.user)
    ).distinct().order_by('title')
    
    # 월별 일정들 (사용자가 생성했거나 참석하는 일정)
    events = Event.objects.filter(
        Q(creator=request.user) | Q(attendees=request.user)
    ).filter(
        Q(start_date__year=year, start_date__month=month) |
        Q(end_date__year=year, end_date__month=month) |
        Q(start_date__lte=date(year, month, 1), end_date__gte=date(year, month, cal_module.monthrange(year, month)[1]))
    ).distinct().order_by('start_date', 'start_time')
    if exclude_keyword:
        events = events.exclude(title__icontains=exclude_keyword)
    
    # 해당 월의 일별 프로젝트 매핑
    daily_projects = {}
    for project in projects:
        # 프로젝트가 해당 월에 걸쳐있는 모든 날짜
        start_date = max(project.start_date, date(year, month, 1))
        end_date = min(project.end_date, date(year, month, cal_module.monthrange(year, month)[1]))
        
        current_date = start_date
        while current_date <= end_date:
            if current_date not in daily_projects:
                daily_projects[current_date] = []
            daily_projects[current_date].append(project)
            current_date += timedelta(days=1)
    
    # 해당 월의 일별 일정 매핑
    daily_events = {}
    for event in events:
        # 일정이 해당 월에 걸쳐있는 모든 날짜
        start_date = max(event.start_date, date(year, month, 1))
        end_date = min(event.end_date, date(year, month, cal_module.monthrange(year, month)[1]))
        
        current_date = start_date
        while current_date <= end_date:
            if current_date not in daily_events:
                daily_events[current_date] = []
            daily_events[current_date].append(event)
            current_date += timedelta(days=1)
    
    # 템플릿에서 사용할 수 있도록 날짜별 리스트 생성
    daily_projects_list = []
    for project in projects:
        daily_projects_list.append(project)
    
    daily_events_list = []
    for event in events:
        daily_events_list.append(event)
    
    # 캘린더 데이터 생성
    cal = cal_module.monthcalendar(year, month)
    month_name = cal_module.month_name[month]

    calendar_weeks = []
    today_date = today.date()
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                current_date = date(year, month, day)
                week_data.append({
                    'day': day,
                    'date': current_date,
                    'is_today': current_date == today_date,
                    'projects': daily_projects.get(current_date, []),
                    'events': daily_events.get(current_date, []),
                })
        calendar_weeks.append(week_data)

    # 주간 바(멀티데이 바) 계산 유틸
    def build_week_bars(week_days, items, get_start, get_end, get_color, get_url, get_label):
        # week_days: [date or None] length 7
        # items: iterable of objects
        # returns lanes -> each lane is list of segments [{type:'empty', colspan:int} | {type:'span', colspan:int, label, url, color}]
        # 주의: week_days 내 None은 주의 시작/끝 바깥 날짜
        # week_days 요소는 {'day': int, 'date': date, ...} 또는 None
        valid_days = [d['date'] for d in week_days if d is not None]
        if not valid_days:
            return []
        week_start = valid_days[0]
        week_end = valid_days[-1]

        # 스팬 수집
        spans = []
        for it in items:
            start = get_start(it)
            end = get_end(it)
            # 교집합 확인
            if start > week_end or end < week_start:
                continue
            # 주 내 시작/끝 컬럼 계산
            span_start_date = max(start, week_start)
            span_end_date = min(end, week_end)
            # 컬럼 인덱스 (0..6) 계산 (None 칸은 건너뛰기)
            start_col = None
            end_col = None
            for idx, d in enumerate(week_days):
                if d is None:
                    continue
                current = d['date']
                if start_col is None and current >= span_start_date:
                    start_col = idx
                if current <= span_end_date:
                    end_col = idx
            if start_col is None or end_col is None:
                continue
            colspan = (end_col - start_col + 1)
            spans.append({
                'start_col': start_col,
                'end_col': end_col,
                'colspan': colspan,
                'label': get_label(it),
                'url': get_url(it),
                'color': get_color(it),
            })

        # 그리디 레인 배치
        lanes = []  # each lane: list of spans with start_col/end_col
        for sp in sorted(spans, key=lambda x: (x['start_col'], -x['colspan'])):
            placed = False
            for lane in lanes:
                # overlap 확인
                if any(not (sp['end_col'] < lp['start_col'] or sp['start_col'] > lp['end_col']) for lp in lane):
                    continue
                lane.append(sp)
                placed = True
                break
            if not placed:
                lanes.append([sp])

        # 레인을 세그먼트로 변환
        lane_segments = []
        for lane in lanes:
            segments = []
            cursor = 0
            for sp in sorted(lane, key=lambda x: x['start_col']):
                if sp['start_col'] > cursor:
                    segments.append({'type': 'empty', 'colspan': sp['start_col'] - cursor})
                segments.append({'type': 'span', 'colspan': sp['colspan'], 'label': sp['label'], 'url': sp['url'], 'color': sp['color']})
                cursor = sp['end_col'] + 1
            if cursor < 7:
                segments.append({'type': 'empty', 'colspan': 7 - cursor})
            lane_segments.append(segments)
        return lane_segments

    week_bars = []
    for week_days in calendar_weeks:
        # 프로젝트 바 계산
        project_lanes = build_week_bars(
            week_days,
            projects,
            lambda p: p.start_date,
            lambda p: p.end_date,
            lambda p: getattr(p, 'theme_color', '#3B82F6'),
            lambda p: request.build_absolute_uri(
                request.path.replace('calendar/', f"projects/{p.pk}/")
            ),
            lambda p: p.title,
        )
        # 이벤트 바 계산
        event_lanes = build_week_bars(
            week_days,
            events,
            lambda e: e.start_date,
            lambda e: e.end_date,
            lambda e: e.priority_color,
            lambda e: request.build_absolute_uri(
                request.path.replace('calendar/', f"events/{e.pk}/")
            ),
            lambda e: e.title,
        )
        week_bars.append({
            'project_lanes': project_lanes,
            'event_lanes': event_lanes,
        })
    
    # 템플릿에서 주와 바를 함께 순회할 수 있도록 결합 구조 생성
    weeks = []
    for i in range(len(calendar_weeks)):
        weeks.append({
            'days': calendar_weeks[i],
            'bars': week_bars[i] if i < len(week_bars) else {'project_lanes': [], 'event_lanes': []},
        })
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'projects': projects,
        'show_projects': show_projects,
        'show_events': show_events,
        'exclude_keyword': exclude_keyword,
        'user_projects': user_projects,  # 일정 생성 시 프로젝트 선택용
        'events': events,
        'daily_projects': daily_projects,
        'daily_events': daily_events,
        'daily_projects_list': daily_projects_list,
        'daily_events_list': daily_events_list,
        'calendar': cal,
        'calendar_weeks': calendar_weeks,
        'week_bars': week_bars,
        'show_bars': show_bars,
        'weeks': weeks,
        'today': today,
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
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
    
    context = {
        'user_subscription': user_subscription,
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


# ==================== Event 관련 뷰 ====================

@login_required
def event_list(request):
    """일정 목록"""
    events = Event.objects.filter(
        Q(creator=request.user) | Q(attendees=request.user)
    ).distinct().order_by('start_date', 'start_time')
    
    # 필터링
    event_type = request.GET.get('type')
    priority = request.GET.get('priority')
    date_filter = request.GET.get('date')
    
    if event_type:
        events = events.filter(event_type=event_type)
    if priority:
        events = events.filter(priority=priority)
    if date_filter:
        if date_filter == 'today':
            events = events.filter(start_date=timezone.now().date())
        elif date_filter == 'week':
            week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
            week_end = week_start + timedelta(days=6)
            events = events.filter(start_date__range=[week_start, week_end])
        elif date_filter == 'month':
            today = timezone.now().date()
            events = events.filter(
                start_date__year=today.year,
                start_date__month=today.month
            )
    
    context = {
        'events': events,
        'event_types': Event.EVENT_TYPES,
        'priority_levels': Event.PRIORITY_LEVELS,
        'current_filters': {
            'type': event_type,
            'priority': priority,
            'date': date_filter,
        }
    }
    
    return render(request, 'wbs/event_list.html', context)


@login_required
def event_create(request):
    """일정 생성"""
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        attendees_form = EventAttendeesForm(request.POST, user=request.user)
        
        if form.is_valid() and attendees_form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            
            # 참석자 추가
            attendees = attendees_form.cleaned_data.get('attendees', [])
            event.attendees.set(attendees)
            
            # AJAX 요청인지 확인
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'event_id': event.id,
                    'title': event.title,
                    'type': event.get_event_type_display(),
                    'priority_color': event.priority_color
                })
            
            messages.success(request, '일정이 성공적으로 생성되었습니다.')
            return redirect('wbs:event_detail', event.pk)
        else:
            # AJAX 요청인지 확인
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                if form.errors:
                    errors.update(form.errors)
                if attendees_form.errors:
                    errors.update(attendees_form.errors)
                return JsonResponse({
                    'success': False,
                    'error': '폼 검증 오류',
                    'errors': errors
                })
    else:
        form = EventForm(user=request.user)
        attendees_form = EventAttendeesForm(user=request.user)
    
    context = {
        'form': form,
        'attendees_form': attendees_form,
        'title': '새 일정 생성'
    }
    
    return render(request, 'wbs/event_form.html', context)


@login_required
def event_detail(request, pk):
    """일정 상세"""
    event = get_object_or_404(Event, pk=pk)
    
    # 권한 확인 (생성자이거나 참석자)
    if event.creator != request.user and request.user not in event.attendees.all():
        messages.error(request, '이 일정에 접근할 권한이 없습니다.')
        return redirect('wbs:event_list')
    
    context = {
        'event': event,
        'can_edit': event.creator == request.user,
    }
    
    return render(request, 'wbs/event_detail.html', context)


@login_required
def event_edit(request, pk):
    """일정 편집"""
    event = get_object_or_404(Event, pk=pk)
    
    # 권한 확인 (생성자만 편집 가능)
    if event.creator != request.user:
        messages.error(request, '이 일정을 편집할 권한이 없습니다.')
        return redirect('wbs:event_detail', pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        attendees_form = EventAttendeesForm(request.POST, user=request.user)
        
        if form.is_valid() and attendees_form.is_valid():
            event = form.save()
            
            # 참석자 업데이트
            attendees = attendees_form.cleaned_data.get('attendees', [])
            event.attendees.set(attendees)
            
            messages.success(request, '일정이 성공적으로 수정되었습니다.')
            return redirect('wbs:event_detail', event.pk)
    else:
        form = EventForm(instance=event, user=request.user)
        attendees_form = EventAttendeesForm(
            initial={'attendees': event.attendees.all()},
            user=request.user
        )
    
    context = {
        'form': form,
        'attendees_form': attendees_form,
        'event': event,
        'title': '일정 편집'
    }
    
    return render(request, 'wbs/event_form.html', context)


@login_required
def event_delete(request, pk):
    """일정 삭제"""
    event = get_object_or_404(Event, pk=pk)
    
    # 권한 확인 (생성자만 삭제 가능)
    if event.creator != request.user:
        messages.error(request, '이 일정을 삭제할 권한이 없습니다.')
        return redirect('wbs:event_detail', pk)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, '일정이 성공적으로 삭제되었습니다.')
        return redirect('wbs:event_list')
    
    context = {'event': event}
    return render(request, 'wbs/event_confirm_delete.html', context)


@login_required
def event_toggle_complete(request, pk):
    """일정 완료 토글"""
    event = get_object_or_404(Event, pk=pk)
    
    # 권한 확인
    if event.creator != request.user and request.user not in event.attendees.all():
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)
    
    event.is_completed = not event.is_completed
    event.save()
    
    return JsonResponse({
        'success': True,
        'is_completed': event.is_completed
    })


@login_required
def event_quick_create(request):
    """빠른 일정 생성 (캘린더에서)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        event_type = request.POST.get('event_type', 'personal')
        
        print(f"Debug - title: {title}, start_date: {start_date}, event_type: {event_type}")  # 디버깅용
        
        if title and start_date:
            try:
                event = Event.objects.create(
                    title=title,
                    start_date=start_date,
                    end_date=start_date,
                    event_type=event_type,
                    creator=request.user
                )
                
                return JsonResponse({
                    'success': True,
                    'event_id': event.id,
                    'title': event.title,
                    'type': event.get_event_type_display(),
                    'priority_color': event.priority_color
                })
            except Exception as e:
                print(f"Debug - Error creating event: {e}")  # 디버깅용
                return JsonResponse({'error': f'일정 생성 중 오류가 발생했습니다: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': f'필수 정보가 누락되었습니다. title: {title}, start_date: {start_date}'}, status=400)
    
    return JsonResponse({'error': 'POST 요청이 아닙니다.'}, status=405)


@login_required
def event_range_selector(request):
    """일정 범위 선택기"""
    return render(request, 'wbs/event_range_selector.html')