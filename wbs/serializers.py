from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Project, ProjectPhase, ApprovalLine, Comment, 
    ProjectDocument, DailyProgress, TaskChecklistItem, 
    UserProfile, Notification, SubscriptionPlan, 
    UserSubscription, AdCampaign
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff']
        read_only_fields = ['id', 'is_staff']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    manager_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ProjectPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPhase
        fields = '__all__'
        read_only_fields = ['created_at']

class ApprovalLineSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = ApprovalLine
        fields = '__all__'
        read_only_fields = ['created_at', 'approved_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ProjectDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = ProjectDocument
        fields = '__all__'
        read_only_fields = ['created_at']

class DailyProgressSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = DailyProgress
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class TaskChecklistItemSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = TaskChecklistItem
        fields = '__all__'
        read_only_fields = ['created_at']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'read_at']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AdCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdCampaign
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

# 대시보드 통계용 시리얼라이저
class DashboardStatsSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    recent_projects = ProjectSerializer(many=True)
    pending_approvals = ApprovalLineSerializer(many=True)
    monthly_projects = ProjectSerializer(many=True)
    current_month = serializers.CharField()
