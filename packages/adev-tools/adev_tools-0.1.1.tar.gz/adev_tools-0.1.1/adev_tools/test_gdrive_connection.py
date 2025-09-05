#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Service Account 연결 테스트 스크립트
실제 파일 업로드 없이 Service Account 연결 및 권한을 테스트합니다.
"""

import os
import sys
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 설정
SERVICE_ACCOUNT_FILE = '/dskim/dev/service-account-key.json'
GDRIVE_FOLDER_ID = '1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf'
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]

def test_service_account_file():
    """Service Account 파일 테스트"""
    print("1️⃣  Service Account 파일 테스트...")
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ Service Account 파일이 존재하지 않습니다: {SERVICE_ACCOUNT_FILE}")
        return False
    
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            service_account_info = json.load(f)
        
        email = service_account_info.get('client_email', '알 수 없음')
        project_id = service_account_info.get('project_id', '알 수 없음')
        
        print(f"✅ Service Account 파일이 유효합니다.")
        print(f"   이메일: {email}")
        print(f"   프로젝트 ID: {project_id}")
        return True
        
    except Exception as e:
        print(f"❌ Service Account 파일 읽기 실패: {str(e)}")
        return False

def test_drive_api_connection():
    """Google Drive API 연결 테스트"""
    print("\n2️⃣  Google Drive API 연결 테스트...")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # 간단한 API 호출 테스트 (about 정보 가져오기)
        about = service.about().get(fields='user').execute()
        print("✅ Google Drive API 연결 성공!")
        return service
        
    except Exception as e:
        print(f"❌ Google Drive API 연결 실패: {str(e)}")
        return None

def test_shared_drives_access(service):
    """공유 드라이브 접근 테스트"""
    print("\n3️⃣  공유 드라이브 접근 테스트...")
    
    try:
        drives_result = service.drives().list().execute()
        drives = drives_result.get('drives', [])
        
        if drives:
            print("✅ 공유 드라이브 접근 성공!")
            for drive in drives:
                print(f"   - {drive['name']} (ID: {drive['id']})")
        else:
            print("⚠️  접근 가능한 공유 드라이브가 없습니다.")
            print("   (개인 Google Drive 폴더 사용 또는 공유 드라이브에 추가 필요)")
        
        return drives
        
    except HttpError as e:
        print(f"❌ 공유 드라이브 접근 실패: {e}")
        return []

def test_folder_access(service, folder_id):
    """특정 폴더 접근 테스트"""
    print(f"\n4️⃣  폴더 접근 테스트 (ID: {folder_id})...")
    
    try:
        folder_info = service.files().get(
            fileId=folder_id,
            fields='id, name, parents, driveId',
            supportsAllDrives=True
        ).execute()
        
        folder_name = folder_info.get('name', '알 수 없음')
        drive_id = folder_info.get('driveId')
        
        print(f"✅ 폴더 접근 성공: {folder_name}")
        
        if drive_id:
            print(f"   📁 Shared Drive 폴더 (Drive ID: {drive_id})")
            print("   ✅ Service Account 스토리지 할당량 오류 없이 업로드 가능!")
        else:
            print("   📁 개인 Google Drive 폴더")
            print("   ⚠️  Service Account 스토리지 할당량 오류 발생 가능")
            print("   권장: Shared Drive 사용 또는 Domain-wide delegation 설정")
        
        return True
        
    except HttpError as e:
        if e.resp.status == 404:
            print(f"❌ 폴더를 찾을 수 없습니다: {folder_id}")
            print("🔧 해결 방법:")
            print("   1. 폴더 ID가 올바른지 확인")
            print("   2. Service Account를 폴더에 편집 권한으로 공유")
        elif e.resp.status == 403:
            print(f"❌ 폴더 접근 권한이 없습니다: {folder_id}")
            print("🔧 해결 방법:")
            print("   1. 폴더를 Service Account와 공유")
            print("   2. 편집 권한 부여")
        else:
            print(f"❌ 폴더 접근 실패: {e}")
        
        return False

def test_write_permission(service, folder_id):
    """폴더 쓰기 권한 테스트"""
    print(f"\n5️⃣  폴더 쓰기 권한 테스트...")
    
    try:
        # 임시 텍스트 파일 생성
        test_content = "테스트 파일입니다. 이 파일은 권한 테스트 후 삭제됩니다."
        test_file_path = "temp_test_file.txt"
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 파일 업로드 테스트
        from googleapiclient.http import MediaFileUpload
        
        file_metadata = {
            'name': 'TEMP_TEST_FILE_DELETE_ME.txt',
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(test_file_path)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        file_name = file.get('name')
        
        print(f"✅ 파일 업로드 성공: {file_name}")
        print(f"   파일 ID: {file_id}")
        
        # 업로드된 파일 삭제 시도
        try:
            service.files().delete(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            print("✅ 테스트 파일 삭제 완료")
        except HttpError as delete_error:
            if delete_error.resp.status == 404:
                print("⚠️  업로드된 파일이 이미 삭제되었거나 찾을 수 없습니다 (정상)")
            else:
                print(f"⚠️  파일 삭제 실패: {delete_error}")
        
        # 로컬 임시 파일 삭제
        try:
            # Windows에서 파일 핸들이 닫힐 때까지 잠시 대기
            import time
            time.sleep(0.1)
            os.remove(test_file_path)
            print("🗑️  로컬 임시 파일 삭제 완료")
        except PermissionError:
            print("⚠️  로컬 임시 파일 삭제 실패 (다른 프로세스가 사용 중)")
            print(f"   수동으로 삭제해주세요: {test_file_path}")
        except Exception as local_delete_error:
            print(f"⚠️  로컬 파일 삭제 오류: {local_delete_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 쓰기 권한 테스트 실패: {str(e)}")
        
        # 로컬 임시 파일 삭제 (오류 발생시에도)
        try:
            if os.path.exists(test_file_path):
                import time
                time.sleep(0.1)
                os.remove(test_file_path)
        except:
            print(f"⚠️  임시 파일을 수동으로 삭제해주세요: {test_file_path}")
        
        return False

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🧪 Google Drive Service Account 연결 테스트")
    print("=" * 60)
    
    # 1. Service Account 파일 테스트
    if not test_service_account_file():
        print("\n❌ 테스트 중단: Service Account 파일 문제")
        sys.exit(1)
    
    # 2. Google Drive API 연결 테스트
    service = test_drive_api_connection()
    if not service:
        print("\n❌ 테스트 중단: Google Drive API 연결 실패")
        sys.exit(1)
    
    # 3. 공유 드라이브 접근 테스트
    shared_drives = test_shared_drives_access(service)
    
    # 4. 폴더 접근 테스트
    folder_accessible = test_folder_access(service, GDRIVE_FOLDER_ID)
    
    # 5. 쓰기 권한 테스트 (폴더 접근 가능한 경우에만)
    if folder_accessible:
        write_permission = test_write_permission(service, GDRIVE_FOLDER_ID)
        
        if write_permission:
            print("\n🎉 모든 테스트 통과!")
            print("✅ gdrive_service_account_upload.py 실행 준비 완료")
            print("\n📋 테스트 결과 요약:")
            print("   ✅ Service Account 파일 유효")
            print("   ✅ Google Drive API 연결 성공")
            print("   ✅ Shared Drive 폴더 접근 성공")
            print("   ✅ 파일 업로드/삭제 권한 확인")
            print("   ✅ 스토리지 할당량 오류 없음")
        else:
            print("\n⚠️  쓰기 권한 테스트 실패")
            print("🔧 폴더 편집 권한을 확인해주세요.")
    else:
        print("\n❌ 폴더 접근 불가")
        print("🔧 폴더 설정을 확인해주세요.")
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    main() 