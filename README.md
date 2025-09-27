# WBS Project Management System

Django를 사용하여 구축한 체계적인 WBS(Work Breakdown Structure) 프로젝트 관리 시스템입니다.

## 🚀 주요 기능

### 📋 프로젝트 관리
- **프로젝트 생성/수정/삭제**
- **12가지 아름다운 그라데이션 색상 테마**
- **월별 프로젝트 일정 관리**
- **실시간 진행률 추적**
- **우선순위 및 상태 관리**

### 🏗️ WBS (Work Breakdown Structure)
- **프로젝트 단계별 구조화**
- **기획서 형태의 체계적인 관리**
- **담당자 배정 및 작업시간 추적**
- **단계별 승인 시스템**

### ✅ 일별 진행사항 체크
- **1-31일 달력 형태의 진행사항 관리**
- **시각적 체크 시스템**
- **일별 완료율 및 작업시간 기록**
- **작업 체크리스트 관리**
- **메모 및 이슈사항 추적**

### 📝 승인 시스템
- **결재/승인 라인 설정**
- **단계별 승인 요청 및 처리**
- **승인자 지정 및 순서 관리**
- **최종 승인자 설정**
- **승인 의견 및 댓글**

### 💬 댓글 시스템
- **프로젝트/단계별 댓글**
- **댓글 유형 분류 (일반, 질문, 이슈, 제안)**
- **중요 댓글 표시**
- **대댓글 기능**

### 📄 문서 관리
- **프로젝트/단계별 문서 첨부**
- **문서 유형 분류 (기획서, 명세서, 설계서 등)**
- **버전 관리**

## 🎨 12가지 그라데이션 색상 테마

1. **파란-보라 그라데이션** - `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
2. **초록-청록 그라데이션** - `linear-gradient(135deg, #11998e 0%, #38ef7d 100%)`
3. **핑크-빨강 그라데이션** - `linear-gradient(135deg, #f093fb 0%, #f5576c 100%)`
4. **파란-하늘 그라데이션** - `linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)`
5. **초록-민트 그라데이션** - `linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)`
6. **핑크-노랑 그라데이션** - `linear-gradient(135deg, #fa709a 0%, #fee140 100%)`
7. **민트-핑크 그라데이션** - `linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)`
8. **핑크-보라 그라데이션** - `linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)`
9. **노랑-주황 그라데이션** - `linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)`
10. **보라-핑크 그라데이션** - `linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)`
11. **주황-핑크 그라데이션** - `linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)`
12. **회색-파랑 그라데이션** - `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

## 🛠️ 기술 스택

- **Backend**: Django 5.2.6
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (개발용), MySQL 지원
- **Styling**: CSS Grid, Flexbox, 그라데이션 디자인
- **Icons**: Font Awesome 6

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/wbs-project.git
cd wbs-project
```

### 2. 가상환경 생성 및 활성화
```bash
python3 -m venv wbs-venv
source wbs-venv/bin/activate  # Windows: wbs-venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 관리자 계정 생성
```bash
python manage.py createsuperuser
# 또는 기본 계정 사용: admin / 1111
```

### 6. 서버 실행
```bash
python manage.py runserver
```

### 7. 브라우저에서 접속
```
http://127.0.0.1:8000/
```

## 📱 주요 페이지

- **홈페이지**: `/` - 프로젝트 대시보드
- **프로젝트 목록**: `/projects/` - 전체 프로젝트 목록
- **프로젝트 생성**: `/projects/create/` - 새 프로젝트 생성
- **진행사항 캘린더**: `/projects/{id}/progress-calendar/` - 일별 진행사항 체크
- **전체 캘린더**: `/calendar/` - 월별 프로젝트 일정
- **관리자 페이지**: `/admin/` - 데이터 관리

## 👥 기본 계정 정보

- **관리자 계정**: admin
- **비밀번호**: 1111

## 🎯 사용법

### 프로젝트 생성
1. 홈페이지에서 "새 프로젝트 생성" 클릭
2. 프로젝트 정보 입력 (제목, 설명, 일정, 색상 테마 등)
3. 프로젝트 단계 추가
4. 승인 라인 설정

### 진행사항 체크
1. 프로젝트 카드에서 "진행체크" 버튼 클릭
2. 1-31일 달력에서 날짜 선택
3. 진행상태, 진행률, 작업시간 입력
4. 체크리스트 작업 관리

### 승인 처리
1. 홈페이지에서 "승인 대기" 섹션 확인
2. "승인하기" 버튼 클릭
3. 승인/반려 처리 및 의견 작성

## 📄 파일 구조

```
wbs-project/
├── wbs_project/          # Django 프로젝트 설정
├── wbs/                  # WBS 앱
│   ├── models.py        # 데이터 모델
│   ├── views.py         # 뷰 함수
│   ├── forms.py         # 폼 클래스
│   ├── urls.py          # URL 라우팅
│   └── admin.py         # 관리자 페이지
├── templates/           # HTML 템플릿
├── static/             # CSS, JavaScript
├── requirements.txt    # 의존성 목록
└── manage.py          # Django 관리 스크립트
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 연락처

프로젝트 관련 문의사항이 있으시면 Issue를 생성해주세요.

---

**WBS Project Management System** - 체계적이고 아름다운 프로젝트 관리의 새로운 표준 ✨

