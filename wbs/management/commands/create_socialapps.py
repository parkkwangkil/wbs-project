import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = '소셜 로그인 앱들을 자동으로 생성합니다'

    def handle(self, *args, **options):
        try:
            # Site 객체 가져오기 또는 생성
            site, created = Site.objects.get_or_create(
                pk=1,
                defaults={
                    'domain': 'web-production-be50.up.railway.app',
                    'name': 'WBS 프로젝트'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Site 생성됨: {site.domain}'))
            else:
                # 기존 Site 업데이트
                site.domain = 'web-production-be50.up.railway.app'
                site.name = 'WBS 프로젝트'
                site.save()
                self.stdout.write(self.style.SUCCESS(f'Site 업데이트됨: {site.domain}'))

            # Google SocialApp 생성
            google_client_id = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
            google_client_secret = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
            
            if google_client_id and google_client_secret:
                google_app, created = SocialApp.objects.get_or_create(
                    provider='google',
                    defaults={
                        'name': 'Google',
                        'client_id': google_client_id,
                        'secret': google_client_secret,
                    }
                )
                
                if not created:
                    # 기존 앱 업데이트
                    google_app.client_id = google_client_id
                    google_app.secret = google_client_secret
                    google_app.save()
                
                # Site에 연결
                google_app.sites.add(site)
                
                action = '생성됨' if created else '업데이트됨'
                self.stdout.write(self.style.SUCCESS(f'Google SocialApp {action}'))
            else:
                self.stdout.write(self.style.WARNING('Google OAuth 환경변수가 설정되지 않았습니다'))

            # Naver SocialApp 생성
            naver_client_id = os.environ.get('NAVER_OAUTH2_CLIENT_ID')
            naver_client_secret = os.environ.get('NAVER_OAUTH2_CLIENT_SECRET')
            
            if naver_client_id and naver_client_secret:
                naver_app, created = SocialApp.objects.get_or_create(
                    provider='naver',
                    defaults={
                        'name': 'Naver',
                        'client_id': naver_client_id,
                        'secret': naver_client_secret,
                    }
                )
                
                if not created:
                    naver_app.client_id = naver_client_id
                    naver_app.secret = naver_client_secret
                    naver_app.save()
                
                naver_app.sites.add(site)
                
                action = '생성됨' if created else '업데이트됨'
                self.stdout.write(self.style.SUCCESS(f'Naver SocialApp {action}'))
            else:
                self.stdout.write(self.style.WARNING('Naver OAuth 환경변수가 설정되지 않았습니다'))

            # Kakao SocialApp 생성
            kakao_client_id = os.environ.get('KAKAO_OAUTH2_CLIENT_ID')
            kakao_client_secret = os.environ.get('KAKAO_OAUTH2_CLIENT_SECRET')
            
            if kakao_client_id and kakao_client_secret:
                kakao_app, created = SocialApp.objects.get_or_create(
                    provider='kakao',
                    defaults={
                        'name': 'Kakao',
                        'client_id': kakao_client_id,
                        'secret': kakao_client_secret,
                    }
                )
                
                if not created:
                    kakao_app.client_id = kakao_client_id
                    kakao_app.secret = kakao_client_secret
                    kakao_app.save()
                
                kakao_app.sites.add(site)
                
                action = '생성됨' if created else '업데이트됨'
                self.stdout.write(self.style.SUCCESS(f'Kakao SocialApp {action}'))
            else:
                self.stdout.write(self.style.WARNING('Kakao OAuth 환경변수가 설정되지 않았습니다'))

            self.stdout.write(self.style.SUCCESS('소셜 앱 설정이 완료되었습니다!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'오류 발생: {str(e)}'))

