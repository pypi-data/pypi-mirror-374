#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Service Account 설정 예시
이 파일을 복사해서 gdrive_service_account_upload.py의 상단 설정 부분을 수정하세요.
"""

# ============================================================================
# 기본 설정
# ============================================================================

# Service Account 키 파일 경로
SERVICE_ACCOUNT_FILE = '/dskim/dev/service-account-key.json'

# ============================================================================
# 방법 1: Shared Drive 사용 (권장)
# ============================================================================

# 업로드 방법 설정
UPLOAD_METHOD = 'shared_drive'

# 공유 드라이브 내 폴더 ID
# 예: https://drive.google.com/drive/folders/1ABC123DEF456GHI789JKL
GDRIVE_FOLDER_ID = '1ABC123DEF456GHI789JKL'  # 실제 공유 드라이브 폴더 ID로 변경

# Domain Admin Email (shared_drive 사용시 None)
DOMAIN_ADMIN_EMAIL = None

# ============================================================================
# 방법 2: Domain-wide Delegation 사용
# ============================================================================

# # 업로드 방법 설정
# UPLOAD_METHOD = 'domain_delegation'

# # 개인 Google Drive 폴더 ID
# GDRIVE_FOLDER_ID = '1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf'

# # Google Workspace 관리자 이메일
# DOMAIN_ADMIN_EMAIL = 'admin@your-domain.com'  # 실제 관리자 이메일로 변경

# ============================================================================
# API 스코프 설정
# ============================================================================

SCOPES = ['https://www.googleapis.com/auth/drive']

# ============================================================================
# 사용법:
# ============================================================================
"""
1. 위 설정을 gdrive_service_account_upload.py 파일의 상단에 복사
2. 실제 값으로 수정
3. python gdrive_service_account_upload.py 실행

Shared Drive 사용시 필요한 작업:
1. Google Drive에서 공유 드라이브 생성
2. Service Account를 공유 드라이브에 편집자 권한으로 추가
3. 공유 드라이브 내 폴더 ID를 GDRIVE_FOLDER_ID에 설정

Domain-wide Delegation 사용시 필요한 작업:
1. Google Cloud Console에서 Service Account에 도메인 전체 위임 설정
2. Google Workspace 관리 콘솔에서 클라이언트 ID 추가
3. 관리자 이메일을 DOMAIN_ADMIN_EMAIL에 설정
""" 