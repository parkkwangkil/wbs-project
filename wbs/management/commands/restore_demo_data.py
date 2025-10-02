from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from wbs.models import Project, ProjectPhase, Event, SubscriptionPlan, UserSubscription, UserProfile

class Command(BaseCommand):
    help = '데모 데이터를 복원합니다'

    def handle(self, *args, **options):
        try:
            # 기본 사용자들 생성
            users_data = [
                {'username': 'devops', 'email': 'devops@test.com', 'password': 'devops123'},
                {'username': 'developer', 'email': 'dev@test.com', 'password': 'dev123'},
                {'username': 'designer', 'email': 'design@test.com', 'password': 'design123'},
                {'username': 'system', 'email': 'system@test.com', 'password': 'system123'},
                {'username': 'manager', 'email': 'manager@test.com', 'password': 'manager123'},
            ]
            
            created_users = []
            for user_data in users_data:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data['username'].title(),
                    }
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    self.stdout.write(f'사용자 생성: {user.username}')
                else:
                    # 비밀번호 업데이트
                    user.set_password(user_data['password'])
                    user.email = user_data['email']
                    user.save()
                    self.stdout.write(f'사용자 업데이트: {user.username}')
                
                created_users.append(user)
                
                # UserProfile 생성
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone': f'010-1234-567{len(created_users)}',
                        'department': '개발팀' if 'dev' in user.username else '기획팀',
                        'position': '개발자' if 'dev' in user.username else '기획자',
                    }
                )

            # EmailAddress 레코드 생성 (allauth용)
            try:
                from allauth.account.models import EmailAddress
                for user in created_users:
                    email_addr, created = EmailAddress.objects.get_or_create(
                        user=user,
                        email=user.email,
                        defaults={
                            'verified': True,
                            'primary': True,
                        }
                    )
                    if created:
                        self.stdout.write(f'EmailAddress 생성: {user.email}')
            except ImportError:
                self.stdout.write('Allauth가 설치되지 않음 - EmailAddress 건너뜀')

            # 구독 플랜 생성
            plans_data = [
                {
                    'name': 'basic',
                    'display_name': '베이직 플랜',
                    'price': 9900,
                    'billing_cycle': 'monthly',
                    'max_projects': 5,
                    'max_team_members': 3,
                    'is_active': True,
                },
                {
                    'name': 'premium',
                    'display_name': '프리미엄 플랜',
                    'price': 19900,
                    'billing_cycle': 'monthly',
                    'max_projects': 20,
                    'max_team_members': 10,
                    'is_active': True,
                },
                {
                    'name': 'enterprise',
                    'display_name': '엔터프라이즈 플랜',
                    'price': 49900,
                    'billing_cycle': 'monthly',
                    'max_projects': 999,  # 무제한 대신 큰 수
                    'max_team_members': 999,  # 무제한 대신 큰 수
                    'is_active': True,
                }
            ]
            
            for plan_data in plans_data:
                plan, created = SubscriptionPlan.objects.get_or_create(
                    name=plan_data['name'],
                    defaults=plan_data
                )
                if created:
                    self.stdout.write(f'구독 플랜 생성: {plan.display_name}')

            # 데모 프로젝트 생성
            if created_users:
                manager = created_users[0]  # devops를 매니저로
                
                # 팀 프로젝트
                team_project, created = Project.objects.get_or_create(
                    title='WBS 시스템 개발',
                    defaults={
                        'description': '웹 기반 업무 분해 구조 시스템 개발 프로젝트',
                        'manager': manager,
                        'start_date': timezone.now().date(),
                        'end_date': timezone.now().date() + timedelta(days=90),
                        'status': 'in_progress',
                        'is_team_project': True,
                    }
                )
                if created:
                    team_project.team_members.set(created_users[:3])
                    self.stdout.write(f'팀 프로젝트 생성: {team_project.title}')
                
                # 개인 프로젝트
                personal_project, created = Project.objects.get_or_create(
                    title='개인 업무 관리',
                    defaults={
                        'description': '개인 일정 및 업무 관리 프로젝트',
                        'manager': manager,
                        'start_date': timezone.now().date(),
                        'end_date': timezone.now().date() + timedelta(days=30),
                        'status': 'in_progress',
                        'is_personal_project': True,
                    }
                )
                if created:
                    self.stdout.write(f'개인 프로젝트 생성: {personal_project.title}')

                # 프로젝트 단계 생성
                phases_data = [
                    {'name': '요구사항 분석', 'description': '시스템 요구사항 정의 및 분석'},
                    {'name': '시스템 설계', 'description': '아키텍처 및 데이터베이스 설계'},
                    {'name': '개발', 'description': '프론트엔드 및 백엔드 개발'},
                    {'name': '테스트', 'description': '단위 테스트 및 통합 테스트'},
                    {'name': '배포', 'description': '운영 환경 배포 및 모니터링'},
                ]
                
                for i, phase_data in enumerate(phases_data):
                    phase, created = ProjectPhase.objects.get_or_create(
                        project=team_project,
                        title=phase_data['name'],
                        defaults={
                            'description': phase_data['description'],
                            'start_date': team_project.start_date + timedelta(days=i*18),
                            'end_date': team_project.start_date + timedelta(days=(i+1)*18),
                            'assignee': created_users[i % len(created_users)],
                            'status': 'completed' if i < 2 else 'in_progress' if i == 2 else 'pending',
                            'progress': 100 if i < 2 else 60 if i == 2 else 0,
                        }
                    )
                    if created:
                        self.stdout.write(f'프로젝트 단계 생성: {phase.title}')

                # 이벤트 생성
                events_data = [
                    {
                        'title': '프로젝트 킥오프 미팅',
                        'description': '프로젝트 시작 회의',
                        'start_time': timezone.now() + timedelta(days=1, hours=10),
                        'end_time': timezone.now() + timedelta(days=1, hours=12),
                    },
                    {
                        'title': '중간 점검 회의',
                        'description': '프로젝트 진행 상황 점검',
                        'start_time': timezone.now() + timedelta(days=7, hours=14),
                        'end_time': timezone.now() + timedelta(days=7, hours=16),
                    },
                    {
                        'title': '최종 발표',
                        'description': '프로젝트 결과 발표',
                        'start_time': timezone.now() + timedelta(days=30, hours=15),
                        'end_time': timezone.now() + timedelta(days=30, hours=17),
                    }
                ]
                
                for event_data in events_data:
                    event, created = Event.objects.get_or_create(
                        title=event_data['title'],
                        creator=manager,
                        defaults=event_data
                    )
                    if created:
                        event.attendees.set([manager])
                        self.stdout.write(f'이벤트 생성: {event.title}')

            self.stdout.write(self.style.SUCCESS('데모 데이터 복원이 완료되었습니다!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'오류 발생: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
