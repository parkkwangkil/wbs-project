from django.contrib import admin

# Admin site branding
admin.site.site_header = 'WBS 관리자'
admin.site.site_title = 'WBS 관리자'
admin.site.index_title = 'WBS 관리 대시보드'
from .models import Project, ProjectPhase, ApprovalLine, Comment, ProjectDocument, DailyProgress, TaskChecklistItem, UserProfile, Notification, SubscriptionPlan, UserSubscription, AdCampaign

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
    list_display = ['title', 'project', 'order', 'is_completed', 'start_date', 'end_date']
    list_filter = ['is_completed', 'project']
    search_fields = ['title', 'description', 'project__title']
    list_editable = ['is_completed', 'order']
    ordering = ['project', 'order']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'title', 'description', 'order')
        }),
        ('일정', {
            'fields': ('start_date', 'end_date')
        }),
        ('완료 상태', {
            'fields': ('is_completed',)
        }),
    )


@admin.register(ApprovalLine)
class ApprovalLineAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'approver', 'status', 'approved_at', 'created_at']
    list_filter = ['status', 'project']
    search_fields = ['project__title', 'approver__username']
    list_editable = ['status']
    
    fieldsets = (
        ('승인 대상', {
            'fields': ('project',)
        }),
        ('승인자 정보', {
            'fields': ('approver',)
        }),
        ('승인 상태', {
            'fields': ('status', 'comment', 'approved_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'project', 'created_at']
    list_filter = ['created_at', 'project']
    search_fields = ['content', 'author__username', 'project__title']
    
    fieldsets = (
        ('댓글 대상', {
            'fields': ('project',)
        }),
        ('댓글 내용', {
            'fields': ('author', 'content')
        }),
    )


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'uploaded_by', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['title', 'description', 'project__title']
    
    fieldsets = (
        ('문서 정보', {
            'fields': ('title', 'description')
        }),
        ('연결 정보', {
            'fields': ('project', 'uploaded_by')
        }),
        ('파일', {
            'fields': ('file',)
        }),
    )


@admin.register(DailyProgress)
class DailyProgressAdmin(admin.ModelAdmin):
    list_display = ['date', 'project', 'progress', 'created_at']
    list_filter = ['date', 'project']
    search_fields = ['project__title', 'notes']
    list_editable = ['progress']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('project', 'date')
        }),
        ('진행 상태', {
            'fields': ('progress', 'notes')
        }),
    )


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'is_completed', 'order', 'created_at']
    list_filter = ['is_completed', 'project']
    search_fields = ['title', 'description', 'project__title']
    list_editable = ['is_completed', 'order']
    
    fieldsets = (
        ('작업 정보', {
            'fields': ('project', 'title', 'description', 'order')
        }),
        ('완료 상태', {
            'fields': ('is_completed',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'position', 'phone', 'created_at']
    list_filter = ['department', 'position', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'department', 'position']
    ordering = ['user__username']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'bio', 'avatar')
        }),
        ('연락처', {
            'fields': ('phone', 'website')
        }),
        ('직장 정보', {
            'fields': ('department', 'position')
        }),
        ('개인 정보', {
            'fields': ('birth_date', 'location')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    list_editable = ['is_read']
    ordering = ['-created_at']
    
    fieldsets = (
        ('알림 정보', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('관련 객체', {
            'fields': ('project', 'phase')
        }),
        ('상태', {
            'fields': ('is_read', 'read_at')
        }),
    )
    
    readonly_fields = ['created_at', 'read_at']

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'price', 'currency', 'billing_cycle', 'max_projects', 'max_team_members', 'is_active']
    list_filter = ['name', 'billing_cycle', 'is_active', 'has_priority_support', 'has_advanced_analytics']
    search_fields = ['display_name', 'name']
    list_editable = ['price', 'is_active']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'display_name', 'price', 'currency', 'billing_cycle', 'is_active')
        }),
        ('기능 제한', {
            'fields': ('max_projects', 'max_team_members', 'max_storage_gb')
        }),
        ('고급 기능', {
            'fields': ('has_priority_support', 'has_advanced_analytics', 'has_api_access', 'has_custom_branding')
        }),
    )

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'projects_created', 'team_members_added']
    list_filter = ['status', 'plan', 'auto_renew', 'start_date']
    search_fields = ['user__username', 'user__email', 'payment_id']
    list_editable = ['status', 'auto_renew']
    
    fieldsets = (
        ('구독 정보', {
            'fields': ('user', 'plan', 'status', 'auto_renew')
        }),
        ('결제 정보', {
            'fields': ('payment_method', 'payment_id')
        }),
        ('구독 기간', {
            'fields': ('start_date', 'end_date')
        }),
        ('사용량', {
            'fields': ('projects_created', 'team_members_added', 'storage_used_mb')
        }),
    )
    
    readonly_fields = ['start_date', 'created_at', 'updated_at']

@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'status', 'start_date', 'end_date', 'current_impressions', 'current_clicks', 'is_active']
    list_filter = ['position', 'status', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'target_url']
    list_editable = ['status', 'is_active']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'image_url', 'target_url', 'status', 'is_active')
        }),
        ('노출 설정', {
            'fields': ('position', 'target_plans', 'target_pages')
        }),
        ('노출 제한', {
            'fields': ('max_impressions', 'max_clicks', 'current_impressions', 'current_clicks')
        }),
        ('기간', {
            'fields': ('start_date', 'end_date')
        }),
    )
    
    readonly_fields = ['current_impressions', 'current_clicks', 'created_at', 'updated_at']