# Google Drive API credentials.json 파일 생성 가이드

Google Drive API를 사용하기 위한 `credentials.json` 파일을 생성하는 방법을 단계별로 설명합니다.

## 1. Google Cloud Console 설정

### 1) Google Cloud Console 접속
- [Google Cloud Console](https://console.cloud.google.com/)에 접속
- Google 계정으로 로그인

### 2) 프로젝트 생성 또는 선택
- 새 프로젝트를 만들거나 기존 프로젝트 선택
- 프로젝트 이름: 예) "Drive Upload Project"

### 3) Google Drive API 활성화
- 좌측 메뉴에서 "API 및 서비스" > "라이브러리" 클릭
- "Google Drive API" 검색
- "Google Drive API" 클릭 후 "사용" 버튼 클릭

## 2. OAuth 2.0 클라이언트 ID 생성

### 1) 사용자 인증 정보 만들기
- 좌측 메뉴에서 "API 및 서비스" > "사용자 인증 정보" 클릭
- 상단의 "+ 사용자 인증 정보 만들기" > "OAuth 클라이언트 ID" 클릭

### 2) OAuth 동의 화면 구성 (처음 설정하는 경우)
- "OAuth 동의 화면" 탭 클릭
- 사용자 유형: "외부" 선택 (개인 사용)
- 앱 정보 입력:
  - 앱 이름: 예) "Drive File Uploader"
  - 사용자 지원 이메일: 본인 이메일
  - 개발자 연락처 정보: 본인 이메일
- "저장 후 계속" 클릭

### 3) 범위 추가 (선택사항)
- "범위 추가 또는 삭제" 클릭
- Google Drive API 범위 추가
- "업데이트" 클릭

### 4) 클라이언트 ID 생성
- "사용자 인증 정보" 탭으로 돌아가기
- "+ 사용자 인증 정보 만들기" > "OAuth 클라이언트 ID"
- 애플리케이션 유형: "데스크톱 애플리케이션" 선택
- 이름: 예) "Drive Uploader Client"
- "만들기" 클릭

## 3. credentials.json 다운로드

### 1) 파일 다운로드
- 생성된 OAuth 클라이언트 ID 옆의 다운로드 아이콘 클릭
- JSON 파일이 다운로드됨 (파일명: `client_secret_xxxxx.json`)

### 2) 파일명 변경 및 위치 이동
```bash
# 다운로드된 파일을 credentials.json으로 이름 변경
mv ~/Downloads/client_secret_xxxxx.json /your/dev/folder/credentials.json
```

## 4. credentials.json 파일 구조 예시

```json
{
  "installed": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-xxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

## 5. 추가 설정 (테스트 환경인 경우)

개발/테스트 목적이라면:
- OAuth 동의 화면에서 "테스트 사용자" 탭
- 본인 이메일 주소를 테스트 사용자로 추가

## 6. 첫 실행 시 주의사항

코드를 처음 실행하면:
1. 웹 브라우저가 자동으로 열림
2. Google 계정 로그인 요청
3. 앱 권한 허용 화면에서 "허용" 클릭
4. `token_file.pickle` 파일이 자동 생성됨 (이후 재인증 불필요)

## 7. 필요한 Python 패키지

코드 실행 전에 다음 패키지들을 설치해야 합니다:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 8. 보안 주의사항

- `credentials.json` 파일은 민감한 정보이므로 Git 등 버전 관리 시스템에 커밋하지 마세요
- `.gitignore` 파일에 `credentials.json`과 `token_file.pickle`을 추가하세요

```gitignore
# Google Drive API 인증 파일
credentials.json
token_file.pickle
```

이제 Google Drive API를 사용하여 파일을 업로드할 수 있습니다!