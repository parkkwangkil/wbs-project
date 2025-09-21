from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Project(models.Model):
    """프로젝트 모델"""
    STATUS_CHOICES = [
        ('planning', '기획중'),
        ('in_progress', '진행중'),
        ('review', '검토중'),
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
    
    title = models.CharField(max_length=200, verbose_name='프로젝트명')
    description = models.TextField(verbose_name='프로젝트 설명')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects', verbose_name='프로젝트 매니저')
    
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name='상태')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='우선순위')
    
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='예산')
    progress = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='진행률(%)'
    )
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    # 12가지 그라데이션 색상 중 하나 선택
    GRADIENT_CHOICES = [
        ('gradient-1', '파란-보라 그라데이션'),
        ('gradient-2', '초록-청록 그라데이션'),
        ('gradient-3', '핑크-빨강 그라데이션'),
        ('gradient-4', '파란-하늘 그라데이션'),
        ('gradient-5', '초록-민트 그라데이션'),
        ('gradient-6', '핑크-노랑 그라데이션'),
        ('gradient-7', '민트-핑크 그라데이션'),
        ('gradient-8', '핑크-보라 그라데이션'),
        ('gradient-9', '노랑-주황 그라데이션'),
        ('gradient-10', '보라-핑크 그라데이션'),
        ('gradient-11', '주황-핑크 그라데이션'),
        ('gradient-12', '회색-파랑 그라데이션'),
    ]
    
    color_theme = models.CharField(
        max_length=20, 
        choices=GRADIENT_CHOICES, 
        default='gradient-1',
        verbose_name='색상 테마'
    )
    
    class Meta:
        verbose_name = '프로젝트'
        verbose_name_plural = '프로젝트들'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def duration_days(self):
        """프로젝트 기간(일수) 계산"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_overdue(self):
        """프로젝트 지연 여부"""
        from datetime import date
        return self.end_date < date.today() and self.status != 'completed'


class ProjectPhase(models.Model):
    """프로젝트 단계 모델"""
    PHASE_STATUS_CHOICES = [
        ('not_started', '시작 전'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('blocked', '차단됨'),
        ('cancelled', '취소'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='phases', verbose_name='프로젝트')
    phase_name = models.CharField(max_length=100, verbose_name='단계명')
    description = models.TextField(verbose_name='단계 설명')
    order = models.PositiveIntegerField(verbose_name='순서')
    
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    actual_start_date = models.DateField(null=True, blank=True, verbose_name='실제 시작일')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='실제 종료일')
    
    status = models.CharField(max_length=20, choices=PHASE_STATUS_CHOICES, default='not_started', verbose_name='상태')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='진행률(%)'
    )
    
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='담당자')
    estimated_hours = models.IntegerField(default=0, verbose_name='예상 작업시간(시간)')
    actual_hours = models.IntegerField(default=0, verbose_name='실제 작업시간(시간)')
    
    # 단계별 승인 필요 여부
    requires_approval = models.BooleanField(default=False, verbose_name='승인 필요')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '프로젝트 단계'
        verbose_name_plural = '프로젝트 단계들'
        ordering = ['project', 'order']
        unique_together = ['project', 'order']
    
    def __str__(self):
        return f"{self.project.title} - {self.phase_name}"
    
    @property
    def is_overdue(self):
        """단계 지연 여부"""
        from datetime import date
        return self.end_date < date.today() and self.status != 'completed'


class ApprovalLine(models.Model):
    """승인 라인 모델"""
    APPROVAL_STATUS_CHOICES = [
        ('pending', '대기중'),
        ('approved', '승인'),
        ('rejected', '반려'),
        ('cancelled', '취소'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='approval_lines', verbose_name='프로젝트')
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, null=True, blank=True, related_name='approval_lines', verbose_name='단계')
    
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals', verbose_name='승인자')
    order = models.PositiveIntegerField(verbose_name='승인 순서')
    
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending', verbose_name='승인 상태')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='승인일시')
    comments = models.TextField(blank=True, verbose_name='승인 의견')
    
    # 결재 라인 관련
    is_final_approver = models.BooleanField(default=False, verbose_name='최종 승인자')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '승인 라인'
        verbose_name_plural = '승인 라인들'
        ordering = ['project', 'phase', 'order']
        unique_together = ['project', 'phase', 'order']
    
    def __str__(self):
        target = self.phase.phase_name if self.phase else self.project.title
        return f"{target} - {self.approver.username} ({self.get_status_display()})"


class Comment(models.Model):
    """댓글 모델"""
    COMMENT_TYPE_CHOICES = [
        ('general', '일반'),
        ('question', '질문'),
        ('issue', '이슈'),
        ('suggestion', '제안'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments', verbose_name='프로젝트')
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, null=True, blank=True, related_name='comments', verbose_name='단계')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    content = models.TextField(verbose_name='댓글 내용')
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPE_CHOICES, default='general', verbose_name='댓글 유형')
    
    # 대댓글 기능
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='상위 댓글')
    
    # 중요 표시
    is_important = models.BooleanField(default=False, verbose_name='중요 표시')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글들'
        ordering = ['-created_at']
    
    def __str__(self):
        target = self.phase.phase_name if self.phase else self.project.title
        return f"{target} - {self.author.username}: {self.content[:50]}..."


class ProjectDocument(models.Model):
    """프로젝트 문서 모델"""
    DOCUMENT_TYPE_CHOICES = [
        ('proposal', '기획서'),
        ('specification', '명세서'),
        ('design', '설계서'),
        ('manual', '매뉴얼'),
        ('report', '보고서'),
        ('other', '기타'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents', verbose_name='프로젝트')
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, null=True, blank=True, related_name='documents', verbose_name='단계')
    
    title = models.CharField(max_length=200, verbose_name='문서 제목')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other', verbose_name='문서 유형')
    content = models.TextField(verbose_name='문서 내용')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    version = models.CharField(max_length=10, default='1.0', verbose_name='버전')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '프로젝트 문서'
        verbose_name_plural = '프로젝트 문서들'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.project.title} - {self.title} (v{self.version})"


class DailyProgress(models.Model):
    """일별 진행사항 체크 모델"""
    CHECK_STATUS_CHOICES = [
        ('not_started', '시작 전'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('blocked', '차단됨'),
        ('delayed', '지연'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='daily_progress', verbose_name='프로젝트')
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, null=True, blank=True, related_name='daily_progress', verbose_name='단계')
    
    date = models.DateField(verbose_name='날짜')
    status = models.CharField(max_length=20, choices=CHECK_STATUS_CHOICES, default='not_started', verbose_name='진행 상태')
    
    # 체크 항목들
    is_checked = models.BooleanField(default=False, verbose_name='체크 완료')
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='당일 진행률(%)'
    )
    
    # 메모 및 이슈
    memo = models.TextField(blank=True, verbose_name='메모')
    issues = models.TextField(blank=True, verbose_name='이슈사항')
    
    # 작업 시간
    worked_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='작업 시간')
    
    # 담당자
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='담당자')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '일별 진행사항'
        verbose_name_plural = '일별 진행사항들'
        unique_together = ['project', 'phase', 'date', 'assignee']
        ordering = ['-date']
    
    def __str__(self):
        target = self.phase.phase_name if self.phase else self.project.title
        return f"{target} - {self.date} ({self.get_status_display()})"
    
    @property
    def is_today(self):
        """오늘 날짜인지 확인"""
        from datetime import date
        return self.date == date.today()
    
    @property
    def is_weekend(self):
        """주말인지 확인"""
        return self.date.weekday() >= 5  # 5=토요일, 6=일요일


class TaskChecklistItem(models.Model):
    """작업 체크리스트 항목 모델"""
    daily_progress = models.ForeignKey(DailyProgress, on_delete=models.CASCADE, related_name='checklist_items', verbose_name='일별 진행사항')
    
    task_name = models.CharField(max_length=200, verbose_name='작업명')
    is_completed = models.BooleanField(default=False, verbose_name='완료 여부')
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='우선순위')
    
    estimated_time = models.IntegerField(default=60, verbose_name='예상 소요시간(분)')
    actual_time = models.IntegerField(default=0, verbose_name='실제 소요시간(분)')
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='생성일')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='완료일시')
    
    class Meta:
        verbose_name = '작업 체크리스트'
        verbose_name_plural = '작업 체크리스트들'
        ordering = ['priority', 'created_at']
    
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.task_name}"