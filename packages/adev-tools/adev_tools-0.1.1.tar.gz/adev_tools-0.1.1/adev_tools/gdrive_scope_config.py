#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive API 스코프 설정 옵션
사용 목적에 따라 적절한 스코프를 선택할 수 있습니다.
"""

# ============================================================================
# Google Drive API 스코프 옵션
# ============================================================================

# 옵션 1: 최소 권한 (파일 업로드만)
SCOPES_MINIMAL = [
    'https://www.googleapis.com/auth/drive.file'
]

# 옵션 2: 기본 권한 (파일 업로드 + 읽기)
SCOPES_BASIC = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly'
]

# 옵션 3: 확장 권한 (공유 드라이브 접근 포함)
SCOPES_EXTENDED = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

# 옵션 4: 전체 권한 (모든 Google Drive 기능)
SCOPES_FULL = [
    'https://www.googleapis.com/auth/drive'
]

# ============================================================================
# 권장 스코프 설정
# ============================================================================

# 기본 사용 (개인 Google Drive 폴더)
DEFAULT_SCOPES = SCOPES_BASIC

# 공유 드라이브 사용시 권장
SHARED_DRIVE_SCOPES = SCOPES_EXTENDED

# 전체 기능 사용시
FULL_FEATURE_SCOPES = SCOPES_FULL

# ============================================================================
# 스코프별 설명
# ============================================================================

SCOPE_DESCRIPTIONS = {
    'https://www.googleapis.com/auth/drive.file': 
        '앱에서 생성하거나 열린 파일만 접근 가능',
    
    'https://www.googleapis.com/auth/drive.readonly': 
        'Google Drive 파일 및 메타데이터 읽기 전용 접근',
    
    'https://www.googleapis.com/auth/drive.metadata.readonly': 
        'Google Drive 파일 메타데이터 읽기 전용 접근',
    
    'https://www.googleapis.com/auth/drive': 
        'Google Drive의 모든 파일에 대한 전체 접근 권한'
}

# ============================================================================
# 사용법 예시
# ============================================================================

"""
gdrive_service_account_upload.py에서 사용:

# 기본 사용
SCOPES = DEFAULT_SCOPES

# 공유 드라이브 사용시
SCOPES = SHARED_DRIVE_SCOPES

# 전체 기능 사용시
SCOPES = FULL_FEATURE_SCOPES

또는 직접 선택:
SCOPES = SCOPES_EXTENDED
"""

# ============================================================================
# 문제 해결 가이드
# ============================================================================

"""
오류별 해결 방법:

1. "Request had insufficient authentication scopes" 오류:
   → 더 넓은 스코프 사용 (SCOPES_EXTENDED 또는 SCOPES_FULL)

2. "Insufficient Permission" 오류:
   → SCOPES_FULL 사용 또는 Service Account 권한 확인

3. 공유 드라이브 접근 불가:
   → SHARED_DRIVE_SCOPES 또는 SCOPES_FULL 사용

4. 파일 업로드만 필요한 경우:
   → SCOPES_MINIMAL 사용 (보안상 권장)
"""

# ============================================================================
# 현재 권장 설정 (403 오류 해결용)
# ============================================================================

# 현재 문제 해결을 위한 권장 스코프
RECOMMENDED_SCOPES = SCOPES_FULL

print("📋 Google Drive API 스코프 설정 가이드")
print("=" * 50)
print("\n현재 권장 스코프 (403 오류 해결용):")
print("SCOPES = SCOPES_FULL")
print("\n스코프 내용:")
for scope in RECOMMENDED_SCOPES:
    print(f"  - {scope}")
    if scope in SCOPE_DESCRIPTIONS:
        print(f"    {SCOPE_DESCRIPTIONS[scope]}")
print("\n⚠️  참고: 보안상 필요한 최소 권한만 사용하는 것을 권장합니다.")
print("   파일 업로드만 필요한 경우 SCOPES_MINIMAL 사용") 