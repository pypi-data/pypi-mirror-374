# Google Drive Service Account 파일 업로드 도구

Google Service Account를 이용해서 Google Drive 특정 폴더에 파일을 업로드하는 독립된 Python 도구입니다.

## 🚀 주요 기능

- Google Service Account 인증을 통한 Google Drive API 접근
- 특정 Google Drive 폴더에 파일 업로드
- Service Account 파일 유효성 검증
- 상세한 오류 처리 및 로깅
- 한국어 지원

## 📋 사전 요구사항

1. **Python 3.6 이상**
2. **Google Cloud Project 및 Service Account 설정**
3. **Google Drive API 활성화**
4. **Service Account 키 파일** (`/dskim/dev/service-account-key.json`)

## 📦 설치

1. 필요한 라이브러리 설치:
```powershell
pip install -r requirements_gdrive.txt
```

## 🔧 설정

### 1. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > 라이브러리**에서 "Google Drive API" 검색 및 활성화
4. **API 및 서비스 > 사용자 인증 정보**에서 "사용자 인증 정보 만들기" > "서비스 계정" 선택
5. 서비스 계정 생성 후 키 파일 다운로드 (JSON 형식)

### 2. Service Account 키 파일 설정

다운로드한 키 파일을 `/dskim/dev/service-account-key.json` 경로에 저장합니다.

### 3. Google Drive 폴더 권한 설정

1. 업로드할 Google Drive 폴더 (`1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf`)를 Service Account 이메일과 공유
2. 편집 권한 부여

## 🎯 사용법

### 기본 실행
```powershell
python gdrive_service_account_upload.py
```

### 실행 결과
- `hello_world.txt` 파일이 생성됩니다
- 해당 파일이 Google Drive 폴더에 업로드됩니다
- 업로드 완료 후 임시 파일이 삭제됩니다
- Google Drive 링크가 출력됩니다

## 📁 파일 구조

```
.
├── gdrive_service_account_upload.py  # 메인 실행 파일
├── requirements_gdrive.txt           # 필요한 라이브러리 목록
├── README_gdrive.md                  # 사용법 설명
└── /dskim/dev/service-account-key.json  # Service Account 키 파일
```

## 🔍 주요 함수

- `create_service()`: Google Drive API 서비스 객체 생성
- `create_hello_world_file()`: 테스트용 Hello World 파일 생성
- `upload_file_to_drive()`: Google Drive에 파일 업로드
- `verify_service_account_file()`: Service Account 파일 유효성 검증

## ⚠️ 주의사항

1. **Service Account 키 파일 보안**: 키 파일을 안전하게 보관하고 버전 관리에 포함시키지 마세요
2. **폴더 권한**: Service Account가 업로드할 폴더에 대한 편집 권한이 있어야 합니다
3. **API 할당량**: Google Drive API 할당량을 확인하고 적절히 사용하세요

## 🛠️ 커스터마이징

### 다른 파일 업로드
`create_hello_world_file()` 함수를 수정하거나 `upload_file_to_drive()` 함수에 직접 파일 경로를 전달할 수 있습니다.

### 다른 폴더에 업로드
`GDRIVE_FOLDER_ID` 상수를 수정하여 다른 Google Drive 폴더에 업로드할 수 있습니다.

## 📊 실행 예시

```
==================================================
🚀 Google Drive Service Account 파일 업로드 도구
==================================================
✅ Service Account 파일이 유효합니다.
   프로젝트 ID: your-project-id
   클라이언트 이메일: your-service-account@your-project.iam.gserviceaccount.com
✅ Google Drive API 서비스가 성공적으로 생성되었습니다.
✅ 테스트 파일이 생성되었습니다: hello_world.txt
📤 파일 업로드 시작: hello_world.txt
✅ 파일 업로드 성공!
   파일명: hello_world.txt
   파일 ID: 1ABC123DEF456GHI789JKL
   폴더 ID: 1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf

✅ 파일 업로드가 완료되었습니다!
Google Drive 링크: https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view
🗑️  임시 파일이 삭제되었습니다: hello_world.txt

🎉 모든 작업이 완료되었습니다!
```

## 🔧 문제 해결

### ⚠️ 중요: Service Account 스토리지 할당량 오류

**오류 메시지**: `Service Accounts do not have storage quota`

이 오류는 Service Account가 개인 Google Drive에 직접 파일을 업로드할 수 없기 때문에 발생합니다. 다음 두 가지 방법으로 해결할 수 있습니다:

#### 방법 1: Shared Drive 사용 (권장)

1. **Google Drive에서 공유 드라이브 생성**:
   - Google Drive 접속 > 왼쪽 메뉴 > "공유 드라이브" > "새로 만들기"
   - 공유 드라이브 이름 설정

2. **Service Account를 공유 드라이브에 추가**:
   - 공유 드라이브 > 설정 > 구성원 > "구성원 추가"
   - Service Account 이메일 주소 입력 (예: `your-service-account@your-project.iam.gserviceaccount.com`)
   - 권한을 "편집자" 또는 "관리자"로 설정

3. **공유 드라이브 내 폴더 ID 사용**:
   - 공유 드라이브 내에서 폴더 생성
   - 폴더 URL에서 ID 추출: `https://drive.google.com/drive/folders/FOLDER_ID`
   - 코드의 `GDRIVE_FOLDER_ID` 변수를 새 폴더 ID로 변경

#### 방법 2: Domain-wide Delegation 사용

**Google Workspace 관리자 권한이 필요합니다.**

1. **Google Cloud Console 설정**:
   - IAM 및 관리자 > 서비스 계정 > 서비스 계정 선택
   - "고급 설정" > "G Suite 도메인 전체 위임 사용 설정" 체크
   - 클라이언트 ID 복사

2. **Google Workspace 관리 콘솔 설정**:
   - admin.google.com 접속
   - 보안 > API 컨트롤 > 도메인 전체 위임
   - "새로 추가" > 클라이언트 ID 입력
   - 범위: `https://www.googleapis.com/auth/drive.file`

3. **코드 수정**:
   ```python
   UPLOAD_METHOD = 'domain_delegation'
   DOMAIN_ADMIN_EMAIL = 'admin@your-domain.com'  # 관리자 이메일
   ```

### 일반적인 오류

1. **Service Account 파일을 찾을 수 없습니다**
   - `/dskim/dev/service-account-key.json` 경로에 키 파일이 있는지 확인

2. **403 Forbidden 오류**
   - Service Account가 업로드할 폴더에 대한 편집 권한이 있는지 확인
   - Shared Drive 사용시 Service Account가 구성원으로 추가되었는지 확인

3. **400 Bad Request 오류**
   - 폴더 ID가 올바른지 확인
   - Service Account 키 파일이 유효한지 확인

## 📝 라이센스

이 도구는 개인 및 상업적 용도로 자유롭게 사용할 수 있습니다. 