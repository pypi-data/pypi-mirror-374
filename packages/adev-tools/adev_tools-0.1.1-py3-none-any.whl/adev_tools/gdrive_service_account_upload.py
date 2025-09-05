#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Service Account 파일 업로드 도구
Service Account를 이용해서 Google Drive 특정 폴더에 파일을 업로드합니다.
"""

import os
import sys
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# 설정 상수
SERVICE_ACCOUNT_FILE = '/dskim/dev/service-account-key.json'
GDRIVE_FOLDER_ID = '1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf'
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]

# 업로드 방법 설정
UPLOAD_METHOD = 'shared_drive'  # 'shared_drive' 또는 'domain_delegation'
DOMAIN_ADMIN_EMAIL = None  # domain_delegation 사용시 설정

def create_service():
    """
    Google Drive API 서비스 객체를 생성합니다.
    Service Account 인증을 사용합니다.
    """
    try:
        # Service Account 파일 존재 확인
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"오류: Service Account 파일을 찾을 수 없습니다: {SERVICE_ACCOUNT_FILE}")
            return None
        
        # Service Account 인증 정보 로드
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        
        # Domain-wide delegation 사용시 사용자 impersonation
        if UPLOAD_METHOD == 'domain_delegation' and DOMAIN_ADMIN_EMAIL:
            credentials = credentials.with_subject(DOMAIN_ADMIN_EMAIL)
            print(f"✅ Domain-wide delegation 사용: {DOMAIN_ADMIN_EMAIL}")
        
        # Drive API 서비스 생성
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Google Drive API 서비스가 성공적으로 생성되었습니다.")
        return service
        
    except Exception as e:
        print(f"❌ Google Drive API 서비스 생성 실패: {str(e)}")
        return None

def create_hello_world_file():
    """
    테스트용 Hello World 파일을 생성합니다.
    """
    try:
        file_path = "hello_world.txt"
        content = "Hello World!\n안녕하세요!\nThis is a test file uploaded via Google Service Account."
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 테스트 파일이 생성되었습니다: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"❌ 테스트 파일 생성 실패: {str(e)}")
        return None

def check_folder_access(service, folder_id):
    """
    폴더 접근 권한을 확인하고 폴더 정보를 반환합니다.
    """
    try:
        # 폴더 정보 가져오기
        folder_info = service.files().get(
            fileId=folder_id,
            fields='id, name, parents, driveId, permissions',
            supportsAllDrives=True
        ).execute()
        
        folder_name = folder_info.get('name', '알 수 없음')
        drive_id = folder_info.get('driveId')
        
        print(f"✅ 폴더 접근 성공: {folder_name}")
        
        if drive_id:
            print(f"📁 Shared Drive 폴더: {drive_id}")
            return {'accessible': True, 'is_shared_drive': True, 'drive_id': drive_id, 'name': folder_name}
        else:
            print("📁 개인 Google Drive 폴더")
            return {'accessible': True, 'is_shared_drive': False, 'drive_id': None, 'name': folder_name}
            
    except HttpError as e:
        error_details = e.content.decode('utf-8') if e.content else str(e)
        
        if e.resp.status == 404:
            print(f"❌ 폴더를 찾을 수 없습니다: {folder_id}")
            print("🔧 가능한 원인:")
            print("   1. 폴더 ID가 올바르지 않습니다")
            print("   2. Service Account가 폴더에 접근할 권한이 없습니다")
            print("   3. 폴더가 삭제되었거나 존재하지 않습니다")
        elif e.resp.status == 403:
            print(f"❌ 폴더 접근 권한이 없습니다: {folder_id}")
            print("🔧 해결 방법:")
            print("   1. 폴더를 Service Account와 공유해주세요")
            print("   2. 편집 권한을 부여해주세요")
        else:
            print(f"❌ 폴더 정보 확인 실패: {e}")
        
        return {'accessible': False, 'is_shared_drive': False, 'drive_id': None, 'name': None}

def get_service_account_email(service_account_file):
    """
    Service Account 이메일 주소를 반환합니다.
    """
    try:
        with open(service_account_file, 'r') as f:
            service_account_info = json.load(f)
        return service_account_info.get('client_email', '알 수 없음')
    except Exception as e:
        return '알 수 없음'

def create_test_folder(service, parent_folder_id, folder_name="Test Upload Folder"):
    """
    테스트용 폴더를 생성합니다.
    """
    try:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id, name, parents',
            supportsAllDrives=True
        ).execute()
        
        folder_id = folder.get('id')
        folder_name = folder.get('name')
        
        print(f"✅ 테스트 폴더 생성 성공: {folder_name}")
        print(f"   폴더 ID: {folder_id}")
        
        return folder_id
        
    except HttpError as e:
        print(f"❌ 테스트 폴더 생성 실패: {e}")
        return None
    except Exception as e:
        print(f"❌ 테스트 폴더 생성 오류: {str(e)}")
        return None

def list_shared_drives(service):
    """
    접근 가능한 공유 드라이브 목록을 반환합니다.
    """
    try:
        drives_result = service.drives().list().execute()
        drives = drives_result.get('drives', [])
        
        if drives:
            print("📁 접근 가능한 공유 드라이브:")
            for drive in drives:
                print(f"   - {drive['name']} (ID: {drive['id']})")
        else:
            print("📁 접근 가능한 공유 드라이브가 없습니다.")
            
        return drives
        
    except HttpError as e:
        print(f"❌ 공유 드라이브 목록 조회 실패: {e}")
        return []
    except Exception as e:
        print(f"❌ 공유 드라이브 목록 조회 오류: {str(e)}")
        return []

def upload_file_to_drive(service, file_path, folder_id=GDRIVE_FOLDER_ID):
    """
    Google Drive의 특정 폴더에 파일을 업로드합니다.
    
    Args:
        service: Google Drive API 서비스 객체
        file_path: 업로드할 파일 경로
        folder_id: 업로드할 Google Drive 폴더 ID
    
    Returns:
        업로드된 파일의 ID (성공시) 또는 None (실패시)
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return None
        
        # 폴더 접근 권한 확인
        folder_info = check_folder_access(service, folder_id)
        if not folder_info['accessible']:
            return None
        
        # 파일 메타데이터 설정
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        
        # 미디어 업로드 객체 생성
        media = MediaFileUpload(file_path)
        
        print(f"📤 파일 업로드 시작: {file_path}")
        print(f"   업로드 방법: {UPLOAD_METHOD}")
        
        # 파일 업로드 실행 (Shared Drive 지원 포함)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, parents',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        file_name = file.get('name')
        
        print(f"✅ 파일 업로드 성공!")
        print(f"   파일명: {file_name}")
        print(f"   파일 ID: {file_id}")
        print(f"   폴더 ID: {folder_id}")
        
        return file_id
        
    except HttpError as e:
        error_details = e.content.decode('utf-8') if e.content else str(e)
        print(f"❌ Google Drive API 오류: {e}")
        
        # 스토리지 할당량 오류 처리
        if "storageQuotaExceeded" in error_details:
            print("\n🔧 해결 방법:")
            print("1. Shared Drive (공유 드라이브) 사용:")
            print("   - Google Drive에서 공유 드라이브 생성")
            print("   - Service Account를 공유 드라이브에 추가")
            print("   - 공유 드라이브 내 폴더 ID 사용")
            print("\n2. Domain-wide delegation 사용:")
            print("   - Google Workspace 관리자 권한 필요")
            print("   - DOMAIN_ADMIN_EMAIL 설정 후 domain_delegation 방법 사용")
            
        return None
    except Exception as e:
        print(f"❌ 파일 업로드 실패: {str(e)}")
        return None

def verify_service_account_file():
    """
    Service Account 파일의 유효성을 확인합니다.
    """
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"❌ Service Account 파일이 존재하지 않습니다: {SERVICE_ACCOUNT_FILE}")
            return False
        
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            service_account_info = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in service_account_info:
                print(f"❌ Service Account 파일에 필수 필드가 없습니다: {field}")
                return False
        
        if service_account_info['type'] != 'service_account':
            print("❌ 올바른 Service Account 파일이 아닙니다.")
            return False
        
        print("✅ Service Account 파일이 유효합니다.")
        print(f"   프로젝트 ID: {service_account_info['project_id']}")
        print(f"   클라이언트 이메일: {service_account_info['client_email']}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Service Account 파일이 유효한 JSON 형식이 아닙니다.")
        return False
    except Exception as e:
        print(f"❌ Service Account 파일 확인 실패: {str(e)}")
        return False

def setup_domain_delegation():
    """
    Domain-wide delegation 설정을 위한 도움말을 제공합니다.
    """
    print("\n🔧 Domain-wide delegation 설정 방법:")
    print("1. Google Cloud Console에서 Service Account 설정:")
    print("   - IAM 및 관리자 > 서비스 계정에서 서비스 계정 선택")
    print("   - '고급 설정' > 'G Suite 도메인 전체 위임 사용 설정' 체크")
    print("   - 클라이언트 ID 복사")
    print("\n2. Google Workspace 관리 콘솔에서 설정:")
    print("   - 보안 > API 컨트롤 > 도메인 전체 위임에서 클라이언트 ID 추가")
    print("   - 범위: https://www.googleapis.com/auth/drive.file")
    print("\n3. 코드에서 DOMAIN_ADMIN_EMAIL 설정:")
    print("   - 관리자 이메일 주소로 설정")
    print("   - UPLOAD_METHOD = 'domain_delegation' 설정")

def setup_shared_drive_guide():
    """
    Shared Drive 설정 가이드를 제공합니다.
    """
    service_account_email = get_service_account_email(SERVICE_ACCOUNT_FILE)
    
    print("\n🔧 Shared Drive 설정 방법:")
    print("1. Google Drive에서 공유 드라이브 생성:")
    print("   - Google Drive 접속 > 왼쪽 메뉴 > '공유 드라이브' > '새로 만들기'")
    print("   - 공유 드라이브 이름 설정")
    print("\n2. Service Account를 공유 드라이브에 추가:")
    print("   - 공유 드라이브 > 설정 > 구성원 > '구성원 추가'")
    print(f"   - 이메일 주소: {service_account_email}")
    print("   - 권한: '편집자' 또는 '관리자' 선택")
    print("\n3. 공유 드라이브 내 폴더 생성:")
    print("   - 공유 드라이브 내에서 폴더 생성")
    print("   - 폴더 URL에서 ID 추출: https://drive.google.com/drive/folders/FOLDER_ID")
    print("   - 코드의 GDRIVE_FOLDER_ID를 새 폴더 ID로 변경")

def setup_folder_sharing_guide():
    """
    개인 Google Drive 폴더 공유 가이드를 제공합니다.
    """
    service_account_email = get_service_account_email(SERVICE_ACCOUNT_FILE)
    
    print("\n🔧 개인 Google Drive 폴더 공유 방법:")
    print("1. Google Drive에서 폴더 찾기:")
    print(f"   - 폴더 ID: {GDRIVE_FOLDER_ID}")
    print("   - URL: https://drive.google.com/drive/folders/" + GDRIVE_FOLDER_ID)
    print("\n2. 폴더 공유:")
    print("   - 폴더 우클릭 > '공유' 선택")
    print(f"   - 이메일 주소: {service_account_email}")
    print("   - 권한: '편집자' 선택")
    print("   - '전송' 클릭")
    print("\n⚠️  주의: 개인 Drive 사용시 Service Account 스토리지 할당량 오류가 발생할 수 있습니다.")
    print("   권장: Shared Drive 사용 또는 Domain-wide delegation 사용")

def main():
    """
    메인 실행 함수
    """
    print("=" * 50)
    print("🚀 Google Drive Service Account 파일 업로드 도구")
    print("=" * 50)
    
    # 업로드 방법 안내
    print(f"📋 현재 업로드 방법: {UPLOAD_METHOD}")
    if UPLOAD_METHOD == 'domain_delegation':
        print(f"📧 Domain Admin Email: {DOMAIN_ADMIN_EMAIL}")
        if not DOMAIN_ADMIN_EMAIL:
            print("⚠️  Domain-wide delegation 사용시 DOMAIN_ADMIN_EMAIL 설정이 필요합니다.")
            setup_domain_delegation()
            sys.exit(1)
    
    # Service Account 파일 확인
    if not verify_service_account_file():
        print("\n❌ Service Account 설정을 확인해주세요.")
        sys.exit(1)
    
    # Google Drive API 서비스 생성
    service = create_service()
    if not service:
        print("\n❌ Google Drive API 서비스 생성에 실패했습니다.")
        sys.exit(1)
    
    # 공유 드라이브 목록 조회 (참고용)
    print("\n📋 환경 정보:")
    shared_drives = list_shared_drives(service)
    
    # 테스트 파일 생성
    test_file = create_hello_world_file()
    if not test_file:
        print("\n❌ 테스트 파일 생성에 실패했습니다.")
        sys.exit(1)
    
    # 파일 업로드
    file_id = upload_file_to_drive(service, test_file)
    if file_id:
        print(f"\n✅ 파일 업로드가 완료되었습니다!")
        print(f"Google Drive 링크: https://drive.google.com/file/d/{file_id}/view")
    else:
        print("\n❌ 파일 업로드에 실패했습니다.")
        print("\n💡 해결 방법 선택:")
        print("1️⃣  Shared Drive 사용 (권장)")
        print("2️⃣  개인 Google Drive 폴더 공유")
        print("3️⃣  Domain-wide delegation 사용")
        
        # 상세 가이드 제공
        setup_shared_drive_guide()
        setup_folder_sharing_guide()
        setup_domain_delegation()
        sys.exit(1)
    
    # 임시 파일 삭제
    try:
        os.remove(test_file)
        print(f"🗑️  임시 파일이 삭제되었습니다: {test_file}")
    except Exception as e:
        print(f"⚠️  임시 파일 삭제 실패: {str(e)}")
    
    print("\n🎉 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main() 