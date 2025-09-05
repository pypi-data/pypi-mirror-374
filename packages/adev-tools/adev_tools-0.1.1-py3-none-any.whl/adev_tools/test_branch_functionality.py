#!/usr/bin/env python3
"""
브랜치 기능 테스트 스크립트
push_empty_commit 함수의 site 브랜치 생성 및 체크아웃 기능을 테스트합니다.
"""

import sys
import os

# ci_lib 모듈을 import하기 위해 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ci_lib import check_branch_exists, create_branch_from_main, push_empty_commit
except ImportError as e:
    print(f"❌ ci_lib 모듈 import 실패: {e}")
    print("현재 디렉토리에 ci_lib.py 파일이 있는지 확인해주세요.")
    sys.exit(1)

def test_branch_functions():
    """브랜치 관련 함수들을 테스트합니다."""
    
    print("🧪 브랜치 기능 테스트 시작")
    print("=" * 50)
    
    # 테스트할 브랜치 이름들
    test_branches = [
        "test-site-1",
        "test-site-2", 
        "production",
        "staging"
    ]
    
    for branch_name in test_branches:
        print(f"\n📝 테스트 브랜치: {branch_name}")
        print("-" * 30)
        
        # 1. 브랜치 존재 여부 확인
        print("1️⃣ 브랜치 존재 여부 확인")
        exists = check_branch_exists(branch_name)
        
        if not exists:
            # 2. 브랜치가 없으면 생성
            print("2️⃣ 브랜치 생성 시도")
            created = create_branch_from_main(branch_name)
            if created:
                print(f"✅ 브랜치 '{branch_name}' 생성 성공")
            else:
                print(f"❌ 브랜치 '{branch_name}' 생성 실패")
                continue
        else:
            print(f"ℹ️ 브랜치 '{branch_name}' 이미 존재함")
        
        # 3. Empty commit 테스트
        print("3️⃣ Empty commit 테스트")
        test_message = f"테스트 커밋 - {branch_name} 브랜치"
        success = push_empty_commit(test_message, branch_name)
        
        if success:
            print(f"✅ Empty commit 성공: {branch_name}")
        else:
            print(f"❌ Empty commit 실패: {branch_name}")

def test_invalid_branch_names():
    """유효하지 않은 브랜치 이름 테스트"""
    
    print("\n🧪 유효하지 않은 브랜치 이름 테스트")
    print("=" * 50)
    
    invalid_names = [
        "",           # 빈 문자열
        "   ",        # 공백만
        "branch name", # 공백 포함
        "branch..name", # 연속 점
        "branch~name",  # 틸드
        "branch:name",  # 콜론
        "branch?name",  # 물음표
        "branch*name",  # 별표
        "branch[name",  # 대괄호
    ]
    
    for invalid_name in invalid_names:
        print(f"\n📝 테스트 중: '{invalid_name}'")
        
        # 브랜치 존재 확인 테스트
        exists = check_branch_exists(invalid_name)
        print(f"   존재 확인 결과: {exists}")
        
        # 브랜치 생성 테스트
        created = create_branch_from_main(invalid_name)
        print(f"   생성 시도 결과: {created}")

def main():
    """메인 테스트 함수"""
    
    print("🚀 push_empty_commit 브랜치 기능 테스트")
    print("이 테스트는 실제 GitLab API를 호출합니다.")
    print("계속하시겠습니까? (y/N): ", end="")
    
    user_input = input().strip().lower()
    if user_input not in ['y', 'yes']:
        print("테스트를 취소합니다.")
        return
    
    try:
        # 정상적인 브랜치 이름 테스트
        test_branch_functions()
        
        # 유효하지 않은 브랜치 이름 테스트
        test_invalid_branch_names()
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료")
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 