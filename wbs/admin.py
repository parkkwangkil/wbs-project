from django.contrib import admin
from .models import Project, ProjectPhase, ApprovalLine, Comment, ProjectDocument, DailyProgress, TaskChecklistItem

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'manager', 'status', 'priority', 'progress', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'priority', 'color_theme', 'created_at']
    search_fields = ['title', 'description', 'manager__username']
    list_editable = ['status', 'priority', 'progress']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'manager', 'color_theme')
        }),
        ('일정', {
            'fields': ('start_date', 'end_date')
        }),
        ('상태', {
            'fields': ('status', 'priority', 'progress')
        }),
        ('예산', {
            'fields': ('budget',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ['phase_name', 'project', 'order', 'status', 'progress', 'assignee', 'start_date', 'end_date']
    list_filter = ['status', 'requires_approval', 'project']
    search_fields = ['phase_name', 'description', 'project__title']
    list_editable = ['status', 'progress', 'order']
    ordering = ['project', 'order']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'phase_name', 'description', 'order')
        }),
        ('일정', {
            'fields': ('start_date', 'end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('담당자 & 상태', {
            'fields': ('assignee', 'status', 'progress')
        }),
        ('작업 시간', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('승인', {
            'fields': ('requires_approval',)
        }),
    )


@admin.register(ApprovalLine)
class ApprovalLineAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'approver', 'order', 'status', 'is_final_approver', 'approved_at']
    list_filter = ['status', 'is_final_approver', 'project']
    search_fields = ['project__title', 'phase__phase_name', 'approver__username']
    list_editable = ['status', 'order', 'is_final_approver']
    
    fieldsets = (
        ('승인 대상', {
            'fields': ('project', 'phase')
        }),
        ('승인자 정보', {
            'fields': ('approver', 'order', 'is_final_approver')
        }),
        ('승인 상태', {
            'fields': ('status', 'approved_at', 'comments')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'project', 'phase', 'comment_type', 'is_important', 'created_at']
    list_filter = ['comment_type', 'is_important', 'created_at', 'project']
    search_fields = ['content', 'author__username', 'project__title']
    list_editable = ['comment_type', 'is_important']
    
    fieldsets = (
        ('댓글 대상', {
            'fields': ('project', 'phase', 'parent')
        }),
        ('댓글 내용', {
            'fields': ('author', 'content', 'comment_type', 'is_important')
        }),
    )


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'phase', 'document_type', 'author', 'version', 'updated_at']
    list_filter = ['document_type', 'project', 'created_at']
    search_fields = ['title', 'content', 'project__title']
    
    fieldsets = (
        ('문서 정보', {
            'fields': ('title', 'document_type', 'version')
        }),
        ('연결 정보', {
            'fields': ('project', 'phase', 'author')
        }),
        ('문서 내용', {
            'fields': ('content',)
        }),
    )


class TaskChecklistItemInline(admin.TabularInline):
    model = TaskChecklistItem
    extra = 1
    fields = ['task_name', 'is_completed', 'priority', 'estimated_time', 'actual_time']


@admin.register(DailyProgress)
class DailyProgressAdmin(admin.ModelAdmin):
    list_display = ['date', 'project', 'phase', 'assignee', 'status', 'is_checked', 'progress_percentage', 'worked_hours']
    list_filter = ['status', 'is_checked', 'date', 'project']
    search_fields = ['project__title', 'phase__phase_name', 'assignee__username', 'memo']
    list_editable = ['status', 'is_checked', 'progress_percentage', 'worked_hours']
    date_hierarchy = 'date'
    inlines = [TaskChecklistItemInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'phase', 'date', 'assignee')
        }),
        ('진행 상태', {
            'fields': ('status', 'is_checked', 'progress_percentage', 'worked_hours')
        }),
        ('메모 및 이슈', {
            'fields': ('memo', 'issues')
        }),
    )


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'daily_progress', 'is_completed', 'priority', 'estimated_time', 'actual_time']
    list_filter = ['is_completed', 'priority', 'daily_progress__date']
    search_fields = ['task_name', 'daily_progress__project__title']
    list_editable = ['is_completed', 'priority', 'actual_time']
    
    fieldsets = (
        ('작업 정보', {
            'fields': ('daily_progress', 'task_name', 'priority')
        }),
        ('완료 상태', {
            'fields': ('is_completed', 'completed_at')
        }),
        ('시간 관리', {
            'fields': ('estimated_time', 'actual_time')
        }),
    )