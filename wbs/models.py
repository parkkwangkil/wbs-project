from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def _contrast_text_color(hex_color: str) -> str:
    """#RRGGBB 배경색에 대해 가독성 좋은 전경색 반환(#111 또는 #fff)."""
    try:
        c = hex_color.lstrip('#')
        r = int(c[0:2], 16)
        g = int(c[2:4], 16)
        b = int(c[4:6], 16)
        brightness = (299 * r + 587 * g + 114 * b) / 1000
        return '#111111' if brightness > 186 else '#ffffff'
    except Exception:
        return '#ffffff'

class UserProfile(models.Model):
    """사용자 프로필 모델"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='자기소개')
    phone = models.CharField(max_length=20, blank=True, verbose_name='전화번호')
    department = models.CharField(max_length=100, blank=True, verbose_name='부서')
    position = models.CharField(max_length=100, blank=True, verbose_name='직책')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='프로필 이미지')
    birth_date = models.DateField(blank=True, null=True, verbose_name='생년월일')
    location = models.CharField(max_length=100, blank=True, verbose_name='위치')
    website = models.URLField(blank=True, verbose_name='웹사이트')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필'

    def __str__(self):
        return f"{self.user.username}의 프로필"

    @property
    def full_name(self):
        first_name = self.user.first_name or ""
        last_name = self.user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name if full_name else self.user.username

class Project(models.Model):
    """프로젝트 모델"""
    STATUS_CHOICES = [
        ('planning', '기획'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('on_hold', '보류'),
        ('cancelled', '취소'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '낮음'),
        ('medium', '보통'),
        ('high', '높음'),
        ('urgent', '긴급'),
    ]
    
    COLOR_THEMES = [
        ('blue', '파란색'),
        ('green', '초록색'),
        ('purple', '보라색'),
        ('red', '빨간색'),
        ('orange', '주황색'),
        ('teal', '청록색'),
        ('pink', '분홍색'),
        ('indigo', '남색'),
        ('yellow', '노란색'),
        ('gray', '회색'),
        ('cyan', '시안색'),
        ('lime', '라임색'),
    ]

    title = models.CharField(max_length=200, verbose_name='프로젝트명')
    description = models.TextField(verbose_name='설명')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects', verbose_name='매니저')
    tl = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lead_projects', verbose_name='기술 리드')
    team_members = models.ManyToManyField(User, blank=True, related_name='participating_projects', verbose_name='팀원')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name='상태')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='우선순위')
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='예산')
    color_theme = models.CharField(max_length=20, choices=COLOR_THEMES, default='blue', verbose_name='색상 테마')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='진행률')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def theme_color(self):
        """프로젝트 색상 테마를 hex 색상으로 반환"""
        theme_to_hex = {
            'blue': '#3B82F6',
            'green': '#10B981',
            'purple': '#8B5CF6',
            'red': '#EF4444',
            'orange': '#F59E0B',
            'teal': '#14B8A6',
            'pink': '#EC4899',
            'indigo': '#6366F1',
            'yellow': '#EAB308',
            'gray': '#6B7280',
            'cyan': '#06B6D4',
            'lime': '#84CC16',
        }
        return theme_to_hex.get(self.color_theme, '#3B82F6')

    @property
    def contrast_text_color(self):
        return _contrast_text_color(self.theme_color)

    class Meta:
        verbose_name = '프로젝트'
        verbose_name_plural = '프로젝트'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ProjectPhase(models.Model):
    """프로젝트 단계 모델"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases', verbose_name='프로젝트')
    title = models.CharField(max_length=200, verbose_name='단계명')
    description = models.TextField(verbose_name='설명')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    order = models.PositiveIntegerField(default=0, verbose_name='순서')
    is_completed = models.BooleanField(default=False, verbose_name='완료여부')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '프로젝트 단계'
        verbose_name_plural = '프로젝트 단계'
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class ApprovalLine(models.Model):
    """승인 라인 모델"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('in_review', '검토중'),
        ('approved', '승인'),
        ('rejected', '거부'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='approval_lines', verbose_name='프로젝트')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals', verbose_name='승인자')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    comment = models.TextField(blank=True, verbose_name='승인 의견')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='승인일시')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '승인 라인'
        verbose_name_plural = '승인 라인'

    def __str__(self):
        return f"{self.project.title} - {self.approver.username}"

class Comment(models.Model):
    """댓글 모델"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments', verbose_name='프로젝트')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.title} - {self.author.username}"

class ProjectDocument(models.Model):
    """프로젝트 문서 모델"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents', verbose_name='프로젝트')
    title = models.CharField(max_length=200, verbose_name='문서명')
    file = models.FileField(upload_to='project_documents/', verbose_name='파일')
    description = models.TextField(blank=True, verbose_name='설명')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents', verbose_name='업로드자')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '프로젝트 문서'
        verbose_name_plural = '프로젝트 문서'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class DailyProgress(models.Model):
    """일별 진행상황 모델"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='daily_progress', verbose_name='프로젝트')
    date = models.DateField(verbose_name='날짜')
    progress = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='진행률')
    notes = models.TextField(blank=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '일별 진행상황'
        verbose_name_plural = '일별 진행상황'
        unique_together = ['project', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.project.title} - {self.date}"

class TaskChecklistItem(models.Model):
    """작업 체크리스트 항목 모델"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='checklist_items', verbose_name='프로젝트')
    title = models.CharField(max_length=200, verbose_name='작업명')
    description = models.TextField(blank=True, verbose_name='설명')
    is_completed = models.BooleanField(default=False, verbose_name='완료여부')
    order = models.PositiveIntegerField(default=0, verbose_name='순서')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '작업 체크리스트'
        verbose_name_plural = '작업 체크리스트'
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - {self.title}"


class Notification(models.Model):
    """알림 모델"""
    NOTIFICATION_TYPE_CHOICES = [
        ('project_update', '프로젝트 업데이트'),
        ('approval_request', '승인 요청'),
        ('approval_approved', '승인 완료'),
        ('approval_rejected', '승인 거부'),
        ('comment_added', '댓글 추가'),
        ('deadline_approaching', '마감일 임박'),
        ('task_assigned', '작업 할당'),
        ('system', '시스템 알림'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='사용자')
    title = models.CharField(max_length=200, verbose_name='제목')
    message = models.TextField(verbose_name='메시지')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES, default='system', verbose_name='알림 유형')
    is_read = models.BooleanField(default=False, verbose_name='읽음 여부')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='관련 프로젝트')
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='관련 단계')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='읽은 시간')

    class Meta:
        verbose_name = '알림'
        verbose_name_plural = '알림'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """알림을 읽음으로 표시"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class SubscriptionPlan(models.Model):
    """구독 플랜 모델"""
    PLAN_CHOICES = [
        ('free', '무료'),
        ('basic', '베이직'),
        ('premium', '프리미엄'),
        ('enterprise', '엔터프라이즈'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True, verbose_name='플랜명')
    display_name = models.CharField(max_length=100, verbose_name='표시명')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='가격')
    currency = models.CharField(max_length=3, default='KRW', verbose_name='통화')
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', '월간'),
        ('yearly', '연간'),
    ], default='monthly', verbose_name='결제 주기')
    
    # 기능 제한
    max_projects = models.IntegerField(default=3, verbose_name='최대 프로젝트 수')
    max_team_members = models.IntegerField(default=5, verbose_name='최대 팀원 수')
    max_storage_gb = models.IntegerField(default=1, verbose_name='최대 저장공간(GB)')
    has_priority_support = models.BooleanField(default=False, verbose_name='우선 지원')
    has_advanced_analytics = models.BooleanField(default=False, verbose_name='고급 분석')
    has_api_access = models.BooleanField(default=False, verbose_name='API 접근')
    has_custom_branding = models.BooleanField(default=False, verbose_name='커스텀 브랜딩')
    
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '구독 플랜'
        verbose_name_plural = '구독 플랜'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.display_name} - {self.price} {self.currency}"

class UserSubscription(models.Model):
    """사용자 구독 모델"""
    STATUS_CHOICES = [
        ('active', '활성'),
        ('cancelled', '취소됨'),
        ('expired', '만료됨'),
        ('pending', '대기중'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription', verbose_name='사용자')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, verbose_name='플랜')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='상태')
    
    # 결제 정보
    payment_method = models.CharField(max_length=50, blank=True, verbose_name='결제 방법')
    payment_id = models.CharField(max_length=100, blank=True, verbose_name='결제 ID')
    
    # 구독 기간
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='시작일')
    end_date = models.DateTimeField(verbose_name='종료일')
    auto_renew = models.BooleanField(default=True, verbose_name='자동 갱신')
    
    # 사용량 추적
    projects_created = models.IntegerField(default=0, verbose_name='생성된 프로젝트 수')
    team_members_added = models.IntegerField(default=0, verbose_name='추가된 팀원 수')
    storage_used_mb = models.IntegerField(default=0, verbose_name='사용된 저장공간(MB)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '사용자 구독'
        verbose_name_plural = '사용자 구독'
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.display_name}"
    
    def is_active(self):
        """구독이 활성 상태인지 확인"""
        return self.status == 'active' and timezone.now() < self.end_date
    
    def can_create_project(self):
        """프로젝트 생성 가능 여부 확인 (관리자는 무제한)."""
        if self.user.is_staff or self.user.is_superuser:
            return True
        # 엔터프라이즈 플랜은 무제한
        if getattr(self.plan, 'name', '') == 'enterprise' or self.plan.max_projects < 0:
            return True
        return self.projects_created < self.plan.max_projects
    
    def can_add_team_member(self):
        """팀원 추가 가능 여부 확인"""
        return self.team_members_added < self.plan.max_team_members
    
    def get_storage_usage_percentage(self):
        """저장공간 사용률 계산"""
        max_storage_mb = self.plan.max_storage_gb * 1024
        return (self.storage_used_mb / max_storage_mb) * 100 if max_storage_mb > 0 else 0

class AdCampaign(models.Model):
    """광고 캠페인 모델"""
    STATUS_CHOICES = [
        ('active', '활성'),
        ('paused', '일시정지'),
        ('completed', '완료'),
        ('draft', '초안'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(verbose_name='설명')
    image_url = models.URLField(blank=True, verbose_name='이미지 URL')
    target_url = models.URLField(verbose_name='타겟 URL')
    
    # 타겟팅
    target_plans = models.ManyToManyField(SubscriptionPlan, blank=True, verbose_name='타겟 플랜')
    target_pages = models.JSONField(default=list, verbose_name='타겟 페이지')
    
    # 노출 설정
    position = models.CharField(max_length=50, choices=[
        ('header', '헤더'),
        ('sidebar', '사이드바'),
        ('footer', '푸터'),
        ('modal', '모달'),
        ('banner', '배너'),
    ], default='sidebar', verbose_name='위치')
    
    # 노출 제한
    max_impressions = models.IntegerField(default=1000, verbose_name='최대 노출수')
    current_impressions = models.IntegerField(default=0, verbose_name='현재 노출수')
    max_clicks = models.IntegerField(default=100, verbose_name='최대 클릭수')
    current_clicks = models.IntegerField(default=0, verbose_name='현재 클릭수')
    
    # 기간
    start_date = models.DateTimeField(verbose_name='시작일')
    end_date = models.DateTimeField(verbose_name='종료일')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='상태')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '광고 캠페인'
        verbose_name_plural = '광고 캠페인'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_running(self):
        """광고가 실행 중인지 확인"""
        now = timezone.now()
        return (self.status == 'active' and 
                self.is_active and 
                self.start_date <= now <= self.end_date and
                self.current_impressions < self.max_impressions)
    
    def record_impression(self):
        """노출 기록"""
        if self.is_running():
            self.current_impressions += 1
            self.save()
    
    def record_click(self):
        """클릭 기록"""
        if self.is_running() and self.current_clicks < self.max_clicks:
            self.current_clicks += 1
            self.save()


class Event(models.Model):
    """개인 일정/이벤트 모델"""
    EVENT_TYPES = [
        ('meeting', '회의'),
        ('personal', '개인 일정'),
        ('deadline', '마감일'),
        ('reminder', '알림'),
        ('holiday', '휴일'),
        ('other', '기타'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', '낮음'),
        ('medium', '보통'),
        ('high', '높음'),
        ('urgent', '긴급'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(blank=True, verbose_name='설명')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='personal', verbose_name='일정 유형')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name='우선순위')
    
    # 날짜/시간
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    start_time = models.TimeField(blank=True, null=True, verbose_name='시작 시간')
    end_time = models.TimeField(blank=True, null=True, verbose_name='종료 시간')
    is_all_day = models.BooleanField(default=False, verbose_name='하루 종일')
    
    # 관련 프로젝트 (선택사항)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='관련 프로젝트')
    
    # 참석자/담당자
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', verbose_name='생성자')
    attendees = models.ManyToManyField(User, blank=True, related_name='attending_events', verbose_name='참석자')
    
    # 위치/링크
    location = models.CharField(max_length=200, blank=True, verbose_name='장소')
    meeting_link = models.URLField(blank=True, verbose_name='회의 링크')
    
    # 알림 설정
    reminder_minutes = models.IntegerField(default=15, verbose_name='알림 시간(분)')
    is_recurring = models.BooleanField(default=False, verbose_name='반복 일정')
    
    # 상태
    is_completed = models.BooleanField(default=False, verbose_name='완료됨')
    is_private = models.BooleanField(default=False, verbose_name='비공개')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '일정'
        verbose_name_plural = '일정'
        ordering = ['start_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} ({self.start_date})"
    
    def clean(self):
        """유효성 검사"""
        if self.end_date < self.start_date:
            raise ValidationError('종료일은 시작일보다 늦어야 합니다.')
        
        if self.start_time and self.end_time and self.start_date == self.end_date:
            if self.end_time <= self.start_time:
                raise ValidationError('종료 시간은 시작 시간보다 늦어야 합니다.')
    
    @property
    def duration(self):
        """일정 지속 시간"""
        if self.is_all_day:
            return "하루 종일"
        
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta
            start_dt = datetime.combine(self.start_date, self.start_time)
            end_dt = datetime.combine(self.end_date, self.end_time)
            duration = end_dt - start_dt
            return str(duration)
        
        return "시간 미정"
    
    @property
    def priority_color(self):
        """우선순위별 색상"""
        colors = {
            'low': '#10B981',      # 초록
            'medium': '#3B82F6',   # 파랑
            'high': '#F59E0B',     # 주황
            'urgent': '#EF4444',   # 빨강
        }
        return colors.get(self.priority, '#6B7280')
    
    @property
    def type_icon(self):
        """일정 유형별 아이콘"""
        icons = {
            'meeting': 'fas fa-users',
            'personal': 'fas fa-user',
            'deadline': 'fas fa-clock',
            'reminder': 'fas fa-bell',
            'holiday': 'fas fa-calendar-check',
            'other': 'fas fa-calendar',
        }
        return icons.get(self.event_type, 'fas fa-calendar')