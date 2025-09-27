from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProjectViewSet, UserViewSet, UserProfileViewSet, 
    CommentViewSet, NotificationViewSet, DashboardViewSet,
    CalendarViewSet, SearchViewSet
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'calendar', CalendarViewSet, basename='calendar')
router.register(r'search', SearchViewSet, basename='search')

urlpatterns = [
    path('', include(router.urls)),
]
