from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.utils import filter_users_by_email

User = get_user_model()

class CustomLoginForm(AllauthLoginForm):
    """커스텀 로그인 폼 - 이메일 검증 문제 해결"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # login 필드를 CharField로 변경하여 더 유연하게 처리
        self.fields['login'] = forms.CharField(
            label="이메일 주소",
            widget=forms.TextInput(attrs={
                'placeholder': '이메일 주소를 입력하세요',
                'class': 'form-control login-input'
            })
        )
    
    def clean_login(self):
        login = self.cleaned_data.get('login')
        if not login:
            raise forms.ValidationError("이메일 주소를 입력해주세요.")
        
        # 이메일 형식 간단 검증
        if '@' not in login or '.' not in login:
            raise forms.ValidationError("올바른 이메일 형식이 아닙니다.")
        
        return login