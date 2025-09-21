from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Project, ProjectPhase, ApprovalLine, Comment, ProjectDocument, DailyProgress, TaskChecklistItem
from .forms import ProjectForm, ProjectPhaseForm, CommentForm, DailyProgressForm

def home(request):
    """홈페이지 뷰"""
    # 통계 데이터
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    
    # 최근 프로젝트들 (각 그라데이션 테마별로)
    recent_projects = Project.objects.select_related('manager').order_by('-created_at')[:8]
    
    # 승인 대기 중인 항목들
    pending_approvals = ApprovalLine.objects.filter(
        status='pending'
    ).select_related('project', 'phase', 'approver').order_by('created_at')[:5]
    
    # 이번 달 진행 상황
    today = timezone.now().date()
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    monthly_projects = Project.objects.filter(
        Q(start_date__lte=month_end) & Q(end_date__gte=month_start)
    ).order_by('start_date')
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'recent_projects': recent_projects,
        'pending_approvals': pending_approvals,
        'monthly_projects': monthly_projects,
        'current_month': today.strftime('%Y년 %m월'),
    }
    
    return render(request, 'wbs/home.html', context)

def project_list(request):
    """프로젝트 목록 뷰"""
    projects = Project.objects.select_related('manager').prefetch_related('phases').order_by('-created_at')
    
    # 필터링
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search')
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # 상태 및 우선순위 선택지
    status_choices = Project.STATUS_CHOICES
    priority_choices = Project.PRIORITY_CHOICES
    
    context = {
        'projects': projects,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search_query,
    }
    
    return render(request, 'wbs/project_list.html', context)

def project_detail(request, pk):
    """프로젝트 상세 뷰"""
    project = get_object_or_404(Project, pk=pk)
    phases = project.phases.order_by('order')
    approval_lines = project.approval_lines.select_related('approver').order_by('order')
    comments = project.comments.select_related('author').order_by('-created_at')
    documents = project.documents.select_related('author').order_by('-updated_at')
    
    # 댓글 폼 처리
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.project = project
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 추가되었습니다.')
            return redirect('wbs:project_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    # 프로젝트 진행률 계산
    if phases.exists():
        avg_progress = phases.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0
        project.progress = int(avg_progress)
        project.save()
    
    context = {
        'project': project,
        'phases': phases,
        'approval_lines': approval_lines,
        'comments': comments,
        'documents': documents,
        'comment_form': comment_form,
    }
    
    return render(request, 'wbs/project_detail.html', context)

@login_required
def project_create(request):
    """프로젝트 생성 뷰"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            messages.success(request, f'프로젝트 "{project.title}"가 생성되었습니다.')
            return redirect('wbs:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': '새 프로젝트 생성',
    }
    
    return render(request, 'wbs/project_form.html', context)

@login_required
def project_edit(request, pk):
    """프로젝트 수정 뷰"""
    project = get_object_or_404(Project, pk=pk)
    
    # 권한 확인
    if project.manager != request.user and not request.user.is_staff:
        messages.error(request, '프로젝트를 수정할 권한이 없습니다.')
        return redirect('wbs:project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'프로젝트 "{project.title}"가 수정되었습니다.')
            return redirect('wbs:project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': f'프로젝트 수정: {project.title}',
    }
    
    return render(request, 'wbs/project_form.html', context)

@login_required
def phase_create(request, project_pk):
    """프로젝트 단계 생성 뷰"""
    project = get_object_or_404(Project, pk=project_pk)
    
    # 권한 확인
    if project.manager != request.user and not request.user.is_staff:
        messages.error(request, '단계를 생성할 권한이 없습니다.')
        return redirect('wbs:project_detail', pk=project_pk)
    
    if request.method == 'POST':
        form = ProjectPhaseForm(request.POST)
        if form.is_valid():
            phase = form.save(commit=False)
            phase.project = project
            # 자동으로 순서 설정
            last_order = project.phases.aggregate(
                max_order=Count('order')
            )['max_order'] or 0
            phase.order = last_order + 1
            phase.save()
            messages.success(request, f'단계 "{phase.phase_name}"가 추가되었습니다.')
            return redirect('wbs:project_detail', pk=project_pk)
    else:
        form = ProjectPhaseForm()
    
    context = {
        'form': form,
        'project': project,
        'title': f'새 단계 추가: {project.title}',
    }
    
    return render(request, 'wbs/phase_form.html', context)

@login_required
def approve_request(request, approval_pk):
    """승인 요청 처리 뷰"""
    approval = get_object_or_404(ApprovalLine, pk=approval_pk)
    
    # 권한 확인
    if approval.approver != request.user:
        messages.error(request, '승인할 권한이 없습니다.')
        return redirect('wbs:home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve':
            approval.status = 'approved'
            approval.approved_at = timezone.now()
            approval.comments = comments
            approval.save()
            messages.success(request, '승인이 완료되었습니다.')
        elif action == 'reject':
            approval.status = 'rejected'
            approval.comments = comments
            approval.save()
            messages.success(request, '반려 처리되었습니다.')
    
    target = approval.phase if approval.phase else approval.project
    return redirect('wbs:project_detail', pk=approval.project.pk)

def calendar_view(request):
    """월별 캘린더 뷰"""
    # 현재 월 또는 요청된 월
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # 해당 월의 프로젝트들
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    projects = Project.objects.filter(
        Q(start_date__lte=month_end) & Q(end_date__gte=month_start)
    ).select_related('manager')
    
    phases = ProjectPhase.objects.filter(
        Q(start_date__lte=month_end) & Q(end_date__gte=month_start)
    ).select_related('project')
    
    # 캘린더 데이터 구성
    calendar_data = {}
    for project in projects:
        start_in_month = max(project.start_date, month_start)
        end_in_month = min(project.end_date, month_end)
        
        current_date = start_in_month
        while current_date <= end_in_month:
            if current_date not in calendar_data:
                calendar_data[current_date] = []
            calendar_data[current_date].append({
                'type': 'project',
                'title': project.title,
                'color_theme': project.color_theme,
                'pk': project.pk,
            })
            current_date += timedelta(days=1)
    
    for phase in phases:
        start_in_month = max(phase.start_date, month_start)
        end_in_month = min(phase.end_date, month_end)
        
        current_date = start_in_month
        while current_date <= end_in_month:
            if current_date not in calendar_data:
                calendar_data[current_date] = []
            calendar_data[current_date].append({
                'type': 'phase',
                'title': f"{phase.project.title} - {phase.phase_name}",
                'color_theme': phase.project.color_theme,
                'pk': phase.project.pk,
            })
            current_date += timedelta(days=1)
    
    context = {
        'calendar_data': calendar_data,
        'current_year': year,
        'current_month': month,
        'month_name': month_start.strftime('%Y년 %m월'),
        'prev_month': (month_start - timedelta(days=1)).replace(day=1),
        'next_month': month_end + timedelta(days=1),
    }
    
    return render(request, 'wbs/calendar.html', context)


def progress_calendar(request, project_pk):
    """프로젝트 진행사항 캘린더 뷰 (1-31일 체크 형태)"""
    project = get_object_or_404(Project, pk=project_pk)
    
    # 현재 월 또는 요청된 월
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # 해당 월의 첫날과 마지막날
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # 해당 월의 모든 일별 진행사항
    daily_progress_data = {}
    progress_items = DailyProgress.objects.filter(
        project=project,
        date__range=[month_start, month_end]
    ).select_related('phase', 'assignee').prefetch_related('checklist_items')
    
    for item in progress_items:
        if item.date not in daily_progress_data:
            daily_progress_data[item.date] = []
        daily_progress_data[item.date].append(item)
    
    # 캘린더 그리드 생성 (1-31일)
    calendar_grid = []
    current_date = month_start
    week = []
    
    # 월 시작 전 빈 칸 추가
    start_weekday = month_start.weekday()  # 0=월요일, 6=일요일
    for _ in range(start_weekday):
        week.append(None)
    
    while current_date <= month_end:
        # 해당 날짜의 진행사항 데이터
        day_data = {
            'date': current_date,
            'day_number': current_date.day,
            'is_weekend': current_date.weekday() >= 5,
            'is_today': current_date == timezone.now().date(),
            'progress_items': daily_progress_data.get(current_date, []),
            'overall_progress': 0,
            'status_counts': {
                'completed': 0,
                'in_progress': 0,
                'not_started': 0,
                'blocked': 0,
                'delayed': 0,
            }
        }
        
        # 해당 날짜의 전체 진행률 계산
        if day_data['progress_items']:
            total_progress = sum(item.progress_percentage for item in day_data['progress_items'])
            day_data['overall_progress'] = total_progress // len(day_data['progress_items'])
            
            # 상태별 카운트
            for item in day_data['progress_items']:
                if item.status in day_data['status_counts']:
                    day_data['status_counts'][item.status] += 1
        
        week.append(day_data)
        
        # 일주일이 완성되면 그리드에 추가
        if len(week) == 7:
            calendar_grid.append(week)
            week = []
        
        current_date += timedelta(days=1)
    
    # 마지막 주의 빈 칸 채우기
    while len(week) < 7:
        week.append(None)
    if week:
        calendar_grid.append(week)
    
    # 프로젝트 단계들
    phases = project.phases.order_by('order')
    
    context = {
        'project': project,
        'calendar_grid': calendar_grid,
        'current_year': year,
        'current_month': month,
        'month_name': month_start.strftime('%Y년 %m월'),
        'prev_month': (month_start - timedelta(days=1)).replace(day=1),
        'next_month': month_end + timedelta(days=1),
        'phases': phases,
        'weekdays': ['월', '화', '수', '목', '금', '토', '일'],
    }
    
    return render(request, 'wbs/progress_calendar.html', context)


@login_required
def daily_progress_update(request, project_pk, date_str):
    """일별 진행사항 업데이트"""
    project = get_object_or_404(Project, pk=project_pk)
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, '잘못된 날짜 형식입니다.')
        return redirect('wbs:progress_calendar', project_pk=project_pk)
    
    # 해당 날짜의 진행사항 가져오기 또는 생성
    daily_progress, created = DailyProgress.objects.get_or_create(
        project=project,
        date=date_obj,
        assignee=request.user,
        defaults={
            'status': 'not_started',
            'progress_percentage': 0,
        }
    )
    
    if request.method == 'POST':
        form = DailyProgressForm(request.POST, instance=daily_progress)
        if form.is_valid():
            form.save()
            messages.success(request, f'{date_obj} 진행사항이 업데이트되었습니다.')
            return redirect('wbs:progress_calendar', project_pk=project_pk)
    else:
        form = DailyProgressForm(instance=daily_progress)
    
    # 해당 날짜의 체크리스트 항목들
    checklist_items = daily_progress.checklist_items.all()
    
    context = {
        'project': project,
        'daily_progress': daily_progress,
        'form': form,
        'date_obj': date_obj,
        'checklist_items': checklist_items,
    }
    
    return render(request, 'wbs/daily_progress_form.html', context)


@login_required
def checklist_toggle(request, item_pk):
    """체크리스트 항목 완료/미완료 토글"""
    item = get_object_or_404(TaskChecklistItem, pk=item_pk)
    
    # 권한 확인
    if item.daily_progress.assignee != request.user and not request.user.is_staff:
        messages.error(request, '권한이 없습니다.')
        return redirect('wbs:progress_calendar', project_pk=item.daily_progress.project.pk)
    
    item.is_completed = not item.is_completed
    if item.is_completed:
        item.completed_at = timezone.now()
    else:
        item.completed_at = None
    item.save()
    
    return redirect('wbs:daily_progress_update', 
                   project_pk=item.daily_progress.project.pk,
                   date_str=item.daily_progress.date.strftime('%Y-%m-%d'))