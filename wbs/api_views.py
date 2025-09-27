from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
import calendar as cal_module

from .models import (
    Project, ProjectPhase, ApprovalLine, Comment, 
    ProjectDocument, DailyProgress, TaskChecklistItem, 
    UserProfile, Notification, SubscriptionPlan, 
    UserSubscription, AdCampaign
)
from .serializers import (
    UserSerializer, UserProfileSerializer, ProjectSerializer, 
    ProjectPhaseSerializer, ApprovalLineSerializer, CommentSerializer,
    ProjectDocumentSerializer, DailyProgressSerializer, 
    TaskChecklistItemSerializer, NotificationSerializer,
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    AdCampaignSerializer, DashboardStatsSerializer
)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)
    
    @action(detail=True, methods=['get'])
    def phases(self, request, pk=None):
        project = self.get_object()
        phases = project.phases.all().order_by('order')
        serializer = ProjectPhaseSerializer(phases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        project = self.get_object()
        comments = project.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        project = self.get_object()
        documents = project.documents.all().order_by('-created_at')
        serializer = ProjectDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def daily_progress(self, request, pk=None):
        project = self.get_object()
        progress = project.daily_progress.all().order_by('-date')
        serializer = DailyProgressSerializer(progress, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def checklist(self, request, pk=None):
        project = self.get_object()
        checklist = project.checklist_items.all().order_by('order')
        serializer = TaskChecklistItemSerializer(checklist, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all().order_by('username')

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.all()
    
    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'success': True})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )
        return Response({'success': True})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request):
        # 통계 데이터
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status='in_progress').count()
        completed_projects = Project.objects.filter(status='completed').count()
        total_comments = Comment.objects.count()
        
        # 최근 프로젝트 (최대 5개)
        recent_projects = Project.objects.order_by('-created_at')[:5]
        
        # 승인 대기 중인 프로젝트
        pending_approvals = ApprovalLine.objects.filter(
            Q(status='pending') | Q(status='in_review')
        ).distinct()[:5]
        
        # 월별 프로젝트 통계
        today = timezone.now()
        monthly_projects = Project.objects.filter(
            start_date__year=today.year,
            start_date__month=today.month
        )
        
        data = {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_comments': total_comments,
            'recent_projects': recent_projects,
            'pending_approvals': pending_approvals,
            'monthly_projects': monthly_projects,
            'current_month': today.strftime('%Y년 %m월'),
        }
        
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)

class CalendarViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        today = timezone.now()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        
        # 월별 프로젝트들
        projects = Project.objects.filter(
            Q(start_date__year=year, start_date__month=month) |
            Q(end_date__year=year, end_date__month=month) |
            Q(start_date__lte=date(year, month, 1), 
              end_date__gte=date(year, month, cal_module.monthrange(year, month)[1]))
        ).order_by('start_date')
        
        # 해당 월의 일별 프로젝트 매핑
        daily_projects = {}
        for project in projects:
            start_date = max(project.start_date, date(year, month, 1))
            end_date = min(project.end_date, date(year, month, cal_module.monthrange(year, month)[1]))
            
            current_date = start_date
            while current_date <= end_date:
                if current_date not in daily_projects:
                    daily_projects[current_date] = []
                daily_projects[current_date].append(project)
                current_date += timedelta(days=1)
        
        # 캘린더 데이터 생성
        cal = cal_module.monthcalendar(year, month)
        month_name = cal_module.month_name[month]
        
        data = {
            'year': year,
            'month': month,
            'month_name': month_name,
            'projects': ProjectSerializer(projects, many=True).data,
            'daily_projects': {str(k): [ProjectSerializer(p).data for p in v] for k, v in daily_projects.items()},
            'calendar': cal,
            'today': today,
            'prev_month': month - 1 if month > 1 else 12,
            'prev_year': year if month > 1 else year - 1,
            'next_month': month + 1 if month < 12 else 1,
            'next_year': year if month < 12 else year + 1,
        }
        
        return Response(data)

class SearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
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
                'projects': ProjectSerializer(projects, many=True).data,
                'users': UserSerializer(users, many=True).data,
                'notifications': NotificationSerializer(notifications, many=True).data,
                'query': query,
                'total_count': len(projects) + len(users) + len(notifications)
            }
        
        return Response(results)
