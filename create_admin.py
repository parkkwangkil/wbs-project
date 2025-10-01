
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    print('관리자 계정 생성 완료!')
else:
    print('관리자 계정이 이미 존재합니다.')

