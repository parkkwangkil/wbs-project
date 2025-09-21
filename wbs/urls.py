from django.urls import path
from . import views

app_name = 'wbs'

urlpatterns = [
    # 홈페이지
    path('', views.home, name='home'),
    
    # 프로젝트 관련
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    
    # 프로젝트 단계 관련
    path('projects/<int:project_pk>/phases/create/', views.phase_create, name='phase_create'),
    
    # 승인 관련
    path('approvals/<int:approval_pk>/approve/', views.approve_request, name='approve_request'),
    
    # 캘린더
    path('calendar/', views.calendar_view, name='calendar'),
    
    # 진행사항 캘린더
    path('projects/<int:project_pk>/progress-calendar/', views.progress_calendar, name='progress_calendar'),
    path('projects/<int:project_pk>/progress/<str:date_str>/', views.daily_progress_update, name='daily_progress_update'),
    path('checklist/<int:item_pk>/toggle/', views.checklist_toggle, name='checklist_toggle'),
]
