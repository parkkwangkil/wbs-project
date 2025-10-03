from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = '관리자 계정을 생성합니다'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin1234'
            )
            self.stdout.write(
                self.style.SUCCESS('관리자 계정이 성공적으로 생성되었습니다!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('관리자 계정이 이미 존재합니다.')
            )

