from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Project, ProjectPhase, Comment, DailyProgress, TaskChecklistItem, UserProfile, SubscriptionPlan, UserSubscription, AdCampaign, Event

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date', 'status', 'priority', 'budget', 'color_theme', 'tl', 'team_members']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'color_theme': forms.Select(attrs={'class': 'form-control'}),
            'tl': forms.Select(attrs={'class': 'form-control'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ProjectPhaseForm(forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = ['title', 'description', 'start_date', 'end_date', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # project 필드는 뷰에서 설정하므로 폼에서 제외
        if 'project' in self.fields:
            del self.fields['project']

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'display_name', 'price', 'currency', 'billing_cycle', 
                 'max_projects', 'max_team_members', 'max_storage_gb',
                 'has_priority_support', 'has_advanced_analytics', 'has_api_access', 'has_custom_branding']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-control'}),
            'max_projects': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_team_members': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_storage_gb': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_priority_support': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_advanced_analytics': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_api_access': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_custom_branding': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserSubscriptionForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
        fields = ['plan', 'auto_renew']
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-control'}),
            'auto_renew': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AdCampaignForm(forms.ModelForm):
    class Meta:
        model = AdCampaign
        fields = ['title', 'description', 'image_url', 'target_url', 'position', 
                 'max_impressions', 'max_clicks', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'target_url': forms.URLInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'max_impressions': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_clicks': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '댓글을 입력하세요...'}),
        }

class DailyProgressForm(forms.ModelForm):
    class Meta:
        model = DailyProgress
        fields = ['date', 'progress', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TaskChecklistItemForm(forms.ModelForm):
    class Meta:
        model = TaskChecklistItem
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    """사용자 프로필 폼"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'department', 'position', 'avatar', 'birth_date', 'location', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '자기소개를 입력하세요...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '010-1234-5678'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '개발팀'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '팀장'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '서울, 대한민국'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }

class UserForm(forms.ModelForm):
    """사용자 기본 정보 폼"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class EventForm(forms.ModelForm):
    """일정 생성/편집 폼"""
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'priority',
            'start_date', 'end_date', 'start_time', 'end_time', 'is_all_day',
            'related_project', 'location', 'meeting_link',
            'reminder_minutes', 'is_recurring', 'is_private'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '일정 제목을 입력하세요'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '일정에 대한 설명을 입력하세요'
            }),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'is_all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'related_project': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '장소를 입력하세요'
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': '회의 링크를 입력하세요'
            }),
            'reminder_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '1440'
            }),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 관련 프로젝트 필터링 (사용자가 참여한 프로젝트만)
        if user:
            from django.db.models import Q
            self.fields['related_project'].queryset = Project.objects.filter(
                Q(manager=user) | Q(team_members=user)
            ).distinct()
        
        # 시간 필드 조건부 표시
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        is_all_day = cleaned_data.get('is_all_day')
        
        # 종료일 검증
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('종료일은 시작일보다 늦어야 합니다.')
        
        # 시간 검증 (하루 종일이 아닌 경우)
        if not is_all_day and start_time and end_time:
            if start_date == end_date and end_time <= start_time:
                raise forms.ValidationError('종료 시간은 시작 시간보다 늦어야 합니다.')
        
        return cleaned_data


class EventAttendeesForm(forms.Form):
    """일정 참석자 선택 폼"""
    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='참석자 선택'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 현재 사용자 제외
        if user:
            self.fields['attendees'].queryset = User.objects.exclude(id=user.id)