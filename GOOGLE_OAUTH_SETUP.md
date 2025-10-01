# 소셜 로그인 설정 가이드 (Google, 네이버, 카카오)

## 🔑 Google Cloud Console 설정

### 1. Google Cloud Console 접속
- [Google Cloud Console](https://console.cloud.google.com/) 접속
- Google 계정으로 로그인

### 2. 프로젝트 생성 또는 선택
- 새 프로젝트 생성 또는 기존 프로젝트 선택
- 프로젝트 이름: `WBS Project Management`

### 3. OAuth 동의 화면 설정
- 좌측 메뉴에서 "APIs & Services" > "OAuth consent screen" 클릭
- "External" 선택 (개인용)
- 다음 정보 입력:
  - **App name**: `WBS Project Management`
  - **User support email**: 본인 이메일
  - **Developer contact information**: 본인 이메일

### 4. OAuth 2.0 클라이언트 ID 생성
- 좌측 메뉴에서 "APIs & Services" > "Credentials" 클릭
- "Create Credentials" > "OAuth 2.0 Client IDs" 클릭
- **Application type**: "Web application"
- **Name**: `WBS Project Management Web Client`
- **Authorized redirect URIs** 추가:
  ```
  http://localhost:8000/accounts/google/login/callback/
  https://your-railway-domain.railway.app/accounts/google/login/callback/
  https://your-cloudtype-domain.cloudtype.app/accounts/google/login/callback/
  ```

### 5. 클라이언트 ID와 시크릿 복사
- 생성된 클라이언트 ID와 클라이언트 시크릿 복사
- 이 값들을 환경변수에 설정

## 🔑 네이버 개발자 센터 설정

### 1. 네이버 개발자 센터 접속
- [네이버 개발자 센터](https://developers.naver.com/) 접속
- 네이버 계정으로 로그인

### 2. 애플리케이션 등록
- "Application" > "애플리케이션 등록" 클릭
- **애플리케이션 이름**: `WBS Project Management`
- **사용 API**: `네이버 아이디로 로그인` 선택
- **서비스 환경**: `Web` 선택
- **서비스 URL**: `http://localhost:8000`
- **Callback URL**: `http://localhost:8000/accounts/naver/login/callback/`

### 3. 클라이언트 ID와 시크릿 복사
- 생성된 **Client ID**와 **Client Secret** 복사

## 🟡 카카오 개발자 센터 설정

### 1. 카카오 개발자 센터 접속
- [카카오 개발자 센터](https://developers.kakao.com/) 접속
- 카카오 계정으로 로그인

### 2. 애플리케이션 등록
- "내 애플리케이션" > "애플리케이션 추가하기" 클릭
- **앱 이름**: `WBS Project Management`
- **사업자명**: 개인 또는 회사명

### 3. 플랫폼 설정
- **Web 플랫폼** 추가
- **사이트 도메인**: `http://localhost:8000`

### 4. 제품 설정
- **카카오 로그인** 활성화
- **Redirect URI**: `http://localhost:8000/accounts/kakao/login/callback/`

### 5. 클라이언트 ID와 시크릿 복사
- **앱 키**에서 **REST API 키** (Client ID)
- **보안**에서 **Client Secret** 생성

## 🌐 환경변수 설정

### Railway 환경변수 설정
1. Railway 대시보드에서 프로젝트 선택
2. "Variables" 탭 클릭
3. 다음 환경변수 추가:
   ```
   # Google OAuth
   GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id-here
   GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret-here
   
   # 네이버 OAuth
   NAVER_OAUTH2_CLIENT_ID=your-naver-client-id-here
   NAVER_OAUTH2_CLIENT_SECRET=your-naver-client-secret-here
   
   # 카카오 OAuth
   KAKAO_OAUTH2_CLIENT_ID=your-kakao-client-id-here
   KAKAO_OAUTH2_CLIENT_SECRET=your-kakao-client-secret-here
   ```

### Cloudtype 환경변수 설정
1. Cloudtype 대시보드에서 프로젝트 선택
2. "Environment Variables" 섹션에서 추가:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id-here
   GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret-here
   ```

## 🧪 테스트

### 로컬 테스트
1. 로컬에서 Django 서버 실행
2. `http://localhost:8000/accounts/login/` 접속
3. "Google로 로그인" 버튼 클릭
4. Google 로그인 완료 후 리다이렉트 확인

### 배포 테스트
1. Railway와 Cloudtype에 환경변수 설정
2. 배포된 사이트에서 Google 로그인 테스트
3. 로그인 후 대시보드 접근 확인

## 🔧 문제 해결

### 일반적인 오류
1. **"redirect_uri_mismatch"**: Authorized redirect URIs에 정확한 URL 추가
2. **"invalid_client"**: 클라이언트 ID/시크릿 확인
3. **"access_denied"**: OAuth 동의 화면 설정 확인

### 디버깅
- Django 로그에서 OAuth 관련 오류 확인
- Google Cloud Console에서 API 사용량 확인
- 브라우저 개발자 도구에서 네트워크 탭 확인

## 📝 참고사항

- Google OAuth는 무료로 사용 가능
- 일일 API 호출 제한: 100,000회
- 보안을 위해 클라이언트 시크릿은 절대 공개하지 마세요
- 프로덕션 환경에서는 HTTPS 필수
