"""
URL configuration for wbs_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'registration/login.html')

urlpatterns = [
    path("health/", health_check, name='health'),  # 헬스체크 엔드포인트
    path("admin/", admin.site.urls),
    # 커스텀 로그인/로그아웃 사용 (Sites Framework 없이)
    path("accounts/login/", custom_login_view, name='login'),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name='logout'),
    # path("accounts/", include("allauth.urls")),  # allauth 비활성화
    path("", include("wbs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
