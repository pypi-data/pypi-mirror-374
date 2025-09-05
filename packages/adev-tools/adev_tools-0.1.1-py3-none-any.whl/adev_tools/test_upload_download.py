#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Service Account 업로드/다운로드 테스트 도구
파일을 업로드한 후 다시 다운로드하여 무결성을 확인합니다.
"""

import os
import sys
import json
import hashlib
import time
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io

# 설정 상수
SERVICE_ACCOUNT_FILE = '/dskim/dev/service-account-key.json'
GDRIVE_FOLDER_ID = '1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf'
SCOPES = [
    'https://www.googleapis.com/auth/drive'
]

def create_service():
    """
    Google Drive API 서비스 객체를 생성합니다.
    """
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"❌ Service Account 파일을 찾을 수 없습니다: {SERVICE_ACCOUNT_FILE}")
            return None
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Google Drive API 서비스가 성공적으로 생성되었습니다.")
        return service
        
    except Exception as e:
        print(f"❌ Google Drive API 서비스 생성 실패: {str(e)}")
        return None

def calculate_file_hash(file_path):
    """
    파일의 SHA256 해시값을 계산합니다.
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"❌ 파일 해시 계산 실패: {str(e)}")
        return None

def create_test_file():
    """
    테스트용 파일을 생성합니다.
    """
    try:
        file_path = "test_upload_download.txt"
        content = f"""테스트 파일 - 업로드/다운로드 검증용
생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}
한글 텍스트: 안녕하세요! 구글 드라이브 테스트입니다.
English Text: Hello Google Drive!
숫자: 1234567890
특수문자: !@#$%^&*()_+-=[]{{}}|;:'".,<>?/~`

이 파일은 업로드 후 다운로드하여 무결성을 확인하는 용도입니다.
파일 내용이 정확히 일치하는지 SHA256 해시값으로 검증합니다.
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_hash = calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"✅ 테스트 파일 생성 완료: {file_path}")
        print(f"   파일 크기: {file_size} bytes")
        print(f"   SHA256 해시: {file_hash}")
        
        return file_path, file_hash
        
    except Exception as e:
        print(f"❌ 테스트 파일 생성 실패: {str(e)}")
        return None, None

def upload_file_to_drive(service, file_path, folder_id=GDRIVE_FOLDER_ID):
    """
    Google Drive에 파일을 업로드합니다.
    """
    try:
        if not os.path.exists(file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return None
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path)
        
        print(f"📤 파일 업로드 시작: {file_path}")
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        file_name = file.get('name')
        file_size = file.get('size')
        
        print(f"✅ 파일 업로드 성공!")
        print(f"   파일명: {file_name}")
        print(f"   파일 ID: {file_id}")
        print(f"   파일 크기: {file_size} bytes")
        print(f"   Google Drive 링크: https://drive.google.com/file/d/{file_id}/view")
        
        return file_id
        
    except HttpError as e:
        print(f"❌ Google Drive API 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 파일 업로드 실패: {str(e)}")
        return None

def download_file_from_drive(service, file_id, download_path):
    """
    Google Drive에서 파일을 다운로드합니다.
    """
    try:
        print(f"📥 파일 다운로드 시작: {file_id}")
        
        # 파일 메타데이터 가져오기
        file_metadata = service.files().get(
            fileId=file_id,
            fields='id, name, size',
            supportsAllDrives=True
        ).execute()
        
        file_name = file_metadata.get('name')
        file_size = file_metadata.get('size')
        
        print(f"   파일명: {file_name}")
        print(f"   파일 크기: {file_size} bytes")
        
        # 파일 다운로드
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"   다운로드 진행률: {int(status.progress() * 100)}%")
        
        # 파일 저장
        with open(download_path, 'wb') as f:
            f.write(fh.getvalue())
        
        downloaded_size = os.path.getsize(download_path)
        
        print(f"✅ 파일 다운로드 성공!")
        print(f"   저장 경로: {download_path}")
        print(f"   다운로드된 크기: {downloaded_size} bytes")
        
        return True
        
    except HttpError as e:
        print(f"❌ Google Drive API 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 파일 다운로드 실패: {str(e)}")
        return False

def verify_file_integrity(original_path, downloaded_path, original_hash):
    """
    원본 파일과 다운로드된 파일의 무결성을 검증합니다.
    """
    try:
        print(f"🔍 파일 무결성 검증 중...")
        
        # 파일 크기 비교
        original_size = os.path.getsize(original_path)
        downloaded_size = os.path.getsize(downloaded_path)
        
        print(f"   원본 파일 크기: {original_size} bytes")
        print(f"   다운로드 파일 크기: {downloaded_size} bytes")
        
        if original_size != downloaded_size:
            print("❌ 파일 크기가 일치하지 않습니다!")
            return False
        
        # 해시값 비교
        downloaded_hash = calculate_file_hash(downloaded_path)
        
        print(f"   원본 파일 SHA256: {original_hash}")
        print(f"   다운로드 파일 SHA256: {downloaded_hash}")
        
        if original_hash == downloaded_hash:
            print("✅ 파일 무결성 검증 성공! 파일이 완전히 일치합니다.")
            return True
        else:
            print("❌ 파일 해시값이 일치하지 않습니다!")
            return False
            
    except Exception as e:
        print(f"❌ 파일 무결성 검증 실패: {str(e)}")
        return False

def delete_file_from_drive(service, file_id):
    """
    Google Drive에서 파일을 삭제합니다.
    """
    try:
        print(f"🗑️  Google Drive에서 파일 삭제 중: {file_id}")
        
        service.files().delete(
            fileId=file_id,
            supportsAllDrives=True
        ).execute()
        
        print("✅ Google Drive에서 파일이 삭제되었습니다.")
        return True
        
    except HttpError as e:
        print(f"❌ Google Drive 파일 삭제 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 파일 삭제 오류: {str(e)}")
        return False

def cleanup_local_files(*file_paths):
    """
    로컬 파일들을 삭제합니다.
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️  로컬 파일 삭제: {file_path}")
        except Exception as e:
            print(f"⚠️  로컬 파일 삭제 실패 ({file_path}): {str(e)}")

def main():
    """
    메인 실행 함수
    """
    print("=" * 60)
    print("🚀 Google Drive 업로드/다운로드 테스트 도구")
    print("=" * 60)
    
    # Google Drive API 서비스 생성
    service = create_service()
    if not service:
        print("\n❌ Google Drive API 서비스 생성에 실패했습니다.")
        sys.exit(1)
    
    # 1단계: 테스트 파일 생성
    print("\n📝 1단계: 테스트 파일 생성")
    original_file, original_hash = create_test_file()
    if not original_file:
        print("\n❌ 테스트 파일 생성에 실패했습니다.")
        sys.exit(1)
    
    # 2단계: Google Drive에 업로드
    print("\n📤 2단계: Google Drive 업로드")
    file_id = upload_file_to_drive(service, original_file)
    if not file_id:
        print("\n❌ 파일 업로드에 실패했습니다.")
        cleanup_local_files(original_file)
        sys.exit(1)
    
    # 3단계: Google Drive에서 다운로드
    print("\n📥 3단계: Google Drive 다운로드")
    downloaded_file = "downloaded_" + os.path.basename(original_file)
    download_success = download_file_from_drive(service, file_id, downloaded_file)
    if not download_success:
        print("\n❌ 파일 다운로드에 실패했습니다.")
        delete_file_from_drive(service, file_id)
        cleanup_local_files(original_file)
        sys.exit(1)
    
    # 4단계: 파일 무결성 검증
    print("\n🔍 4단계: 파일 무결성 검증")
    integrity_check = verify_file_integrity(original_file, downloaded_file, original_hash)
    
    # 5단계: 정리 작업
    print("\n🧹 5단계: 정리 작업")
    delete_file_from_drive(service, file_id)
    cleanup_local_files(original_file, downloaded_file)
    
    # 최종 결과
    print("\n" + "=" * 60)
    if integrity_check:
        print("🎉 테스트 성공! 업로드/다운로드가 정상적으로 작동합니다.")
        print("✅ 파일 무결성이 완벽하게 유지되었습니다.")
    else:
        print("❌ 테스트 실패! 파일 무결성에 문제가 있습니다.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main() 