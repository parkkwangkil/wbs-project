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

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path("health/", health_check, name='health'),  # 헬스체크 엔드포인트
    path("admin/", admin.site.urls),
    # Django 기본 로그인/로그아웃 사용
    path("accounts/login/", auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name='logout'),
    # path("accounts/", include("allauth.urls")),  # allauth 비활성화
    path("", include("wbs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
