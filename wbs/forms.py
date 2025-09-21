from django import forms
from django.contrib.auth.models import User
from .models import Project, ProjectPhase, Comment, ApprovalLine, ProjectDocument, DailyProgress, TaskChecklistItem

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'status', 'priority', 'budget', 'color_theme'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '프로젝트 제목을 입력하세요'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '프로젝트 설명을 입력하세요'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '예산을 입력하세요'
            }),
            'color_theme': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
        }
        labels = {
            'title': '프로젝트 제목',
            'description': '프로젝트 설명',
            'start_date': '시작일',
            'end_date': '종료일',
            'status': '상태',
            'priority': '우선순위',
            'budget': '예산',
            'color_theme': '색상 테마',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('시작일은 종료일보다 앞서야 합니다.')
        
        return cleaned_data

class ProjectPhaseForm(forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = [
            'phase_name', 'description', 'start_date', 'end_date',
            'assignee', 'estimated_hours', 'requires_approval'
        ]
        widgets = {
            'phase_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '단계명을 입력하세요'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '단계 설명을 입력하세요'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'assignee': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '예상 작업 시간(시간)'
            }),
            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'phase_name': '단계명',
            'description': '단계 설명',
            'start_date': '시작일',
            'end_date': '종료일',
            'assignee': '담당자',
            'estimated_hours': '예상 작업시간',
            'requires_approval': '승인 필요',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 담당자 선택을 위한 사용자 목록
        self.fields['assignee'].queryset = User.objects.filter(is_active=True)
        self.fields['assignee'].empty_label = "담당자를 선택하세요"
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('시작일은 종료일보다 앞서야 합니다.')
        
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'comment_type', 'is_important']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '댓글을 입력하세요...'
            }),
            'comment_type': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'content': '댓글 내용',
            'comment_type': '댓글 유형',
            'is_important': '중요 표시',
        }

class ApprovalLineForm(forms.ModelForm):
    class Meta:
        model = ApprovalLine
        fields = ['approver', 'order', 'is_final_approver']
        widgets = {
            'approver': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'is_final_approver': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'approver': '승인자',
            'order': '승인 순서',
            'is_final_approver': '최종 승인자',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 승인자 선택을 위한 사용자 목록 (스태프 사용자만)
        self.fields['approver'].queryset = User.objects.filter(
            is_active=True, 
            is_staff=True
        )
        self.fields['approver'].empty_label = "승인자를 선택하세요"

class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ['title', 'document_type', 'content', 'version']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '문서 제목을 입력하세요'
            }),
            'document_type': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '문서 내용을 입력하세요'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex) 1.0, 1.1, 2.0'
            }),
        }
        labels = {
            'title': '문서 제목',
            'document_type': '문서 유형',
            'content': '문서 내용',
            'version': '버전',
        }

class ProjectSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '프로젝트 제목 또는 설명으로 검색...'
        }),
        label='검색'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', '전체 상태')] + Project.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        label='상태'
    )
    
    priority = forms.ChoiceField(
        required=False,
        choices=[('', '전체 우선순위')] + Project.PRIORITY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        label='우선순위'
    )
    
    color_theme = forms.ChoiceField(
        required=False,
        choices=[('', '전체 테마')] + Project.GRADIENT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control form-select'
        }),
        label='색상 테마'
    )


class DailyProgressForm(forms.ModelForm):
    class Meta:
        model = DailyProgress
        fields = ['status', 'is_checked', 'progress_percentage', 'worked_hours', 'memo', 'issues', 'phase']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'is_checked': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'progress_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'worked_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 0.5,
                'min': 0
            }),
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '오늘 작업한 내용을 간단히 기록하세요...'
            }),
            'issues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '발생한 이슈나 문제점을 기록하세요...'
            }),
            'phase': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
        }
        labels = {
            'status': '진행 상태',
            'is_checked': '완료 체크',
            'progress_percentage': '진행률 (%)',
            'worked_hours': '작업 시간',
            'memo': '작업 메모',
            'issues': '이슈사항',
            'phase': '연관 단계',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.project:
            self.fields['phase'].queryset = self.instance.project.phases.all()
            self.fields['phase'].empty_label = "단계 선택 (선택사항)"


class TaskChecklistItemForm(forms.ModelForm):
    class Meta:
        model = TaskChecklistItem
        fields = ['task_name', 'priority', 'estimated_time']
        widgets = {
            'task_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '작업할 내용을 입력하세요'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
            'estimated_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '예상 소요시간(분)'
            }),
        }
        labels = {
            'task_name': '작업명',
            'priority': '우선순위 (1-5)',
            'estimated_time': '예상 소요시간 (분)',
        }
