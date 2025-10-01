from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'wbs'

def redirect_to_accounts_login(request):
    return redirect('/accounts/login/')

urlpatterns = [
    # 인증 관련 - 기존 /login/을 /accounts/login/으로 리다이렉트
    path('login/', redirect_to_accounts_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    
    # 홈페이지
    path('', views.home, name='home'),
    
    # 프로젝트 관련
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/team/', views.team_projects, name='team_projects'),
    path('projects/personal/', views.personal_projects, name='personal_projects'),
    
    # 프로젝트 단계 관련
    path('projects/<int:project_pk>/phases/create/', views.phase_create, name='phase_create'),
    path('projects/<int:project_pk>/phases/<int:phase_pk>/edit/', views.phase_edit, name='phase_edit'),
    path('projects/<int:project_pk>/personal-tasks/add/', views.personal_task_add, name='personal_task_add'),
    
    # 승인 관련
    path('approvals/<int:approval_pk>/approve/', views.approve_request, name='approve_request'),
    
    # 캘린더
    path('calendar/', views.calendar, name='calendar'),
    # 개인 플래너
    path('personal/', views.personal_planner, name='personal_planner'),
    # 개인 프로젝트 상세(신규 화면)
    path('projects/<int:pk>/personal/', views.personal_project_detail, name='personal_project_detail'),
    # 프로젝트별 플래너
    path('projects/<int:pk>/planner/', views.project_planner, name='project_planner'),
    
    # 진행사항 캘린더
    path('projects/<int:project_pk>/progress-calendar/', views.progress_calendar, name='progress_calendar'),
    path('projects/<int:project_pk>/progress/update/', views.daily_progress_update, name='daily_progress_update'),
    path('projects/<int:project_pk>/progress/update/<str:date_str>/', views.daily_progress_update, name='daily_progress_update_with_date'),
    path('projects/<int:project_pk>/checklist/toggle/', views.checklist_toggle, name='checklist_toggle'),
    
        # 사용자 프로필 관련
        path('profile/', views.profile_view, name='profile'),
        path('profile/edit/', views.profile_edit, name='profile_edit'),
        path('users/', views.user_list, name='user_list'),
        path('users/<int:user_id>/', views.user_detail, name='user_detail'),
        
        # 알림 관련
        path('notifications/', views.notifications, name='notifications'),
        path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
        path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
        path('api/notifications/count/', views.get_notifications_count, name='get_notifications_count'),
        
        # 구독 관련
        path('subscription/plans/', views.subscription_plans, name='subscription_plans'),
        path('subscription/plans/<int:plan_id>/', views.subscription_detail, name='subscription_detail'),
        path('subscription/plans/<int:plan_id>/subscribe/', views.subscribe, name='subscribe'),
        path('subscription/my/', views.my_subscription, name='my_subscription'),
        path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
        
        # 광고 관련
        path('ads/<int:ad_id>/click/', views.ad_click, name='ad_click'),
        
    # 검색
    path('search/', views.search, name='search'),

    # 일정 관련 (복구)
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/range-selector/', views.event_range_selector, name='event_range_selector'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:pk>/toggle-complete/', views.event_toggle_complete, name='event_toggle_complete'),
    path('events/quick-create/', views.event_quick_create, name='event_quick_create'),
]
