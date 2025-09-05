import subprocess
import os
import time
import requests
import glob
import base64
import sys
import argparse
import gitlab
import yaml
import pathlib
import threading
import json

# Google Drive API 관련 import는 함수 내에서 수행 (선택적 의존성)

# GitLab information
GITLAB_URL = 'https://gitlab.com'
BRANCH_NAME = 'main'
CI_TOOLS_PROJECT_ID = '59583175'

def run_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        sys.exit(e.returncode)


def check_stlink(sn):
    run_command(['STM32_Programmer_CLI.exe', '-l', 'stlink']);

def open_stlink(runner_name,stlink_name):
    # Load the stlink_list.json file
    with open('stlink_list.json', 'r') as f:
        stlink_list = json.load(f)

    # Get the stlink details using the stlink_name key from the stlink_list
    if f'{runner_name}-{stlink_name}' in stlink_list:
        stlink_details = stlink_list[f'{runner_name}-{stlink_name}']
        print(f"STLink details for {stlink_name}: {stlink_details}")
        stlink_port = stlink_details.get('port')
        stlink_sn = stlink_details.get('sn')
    else:
        print(f"No details found for the key '{stlink_name}'. Exiting with status 1.")
        sys.exit(1)

    check_stlink(stlink_sn)
    return stlink_sn

def get_running_job_id(project_id, pipeline_id):
    max_attempts = 5  # 최대 시도 횟수
    attempt = 0
    while attempt < max_attempts:
        response = requests.get(f"{GITLAB_URL}/api/v4/projects/{project_id}/pipelines/{pipeline_id}/jobs", headers=get_gitlab_headers())
        jobs = response.json()
        for job in jobs:
            if job['status'] == 'running':
                return job['id']
        print(f"checking running job... ({attempt + 1}/{max_attempts})")
        time.sleep(5)  # 10초 간격으로 상태 확인
        attempt += 1
    return None

    
def get_pipeline_job_id(pipeline_id):
    if pipeline_id:
        running_job_id = get_running_job_id(CI_TOOLS_PROJECT_ID, pipeline_id)
        if running_job_id:
            print(f"[job_link](https://gitlab.com/jltech_lab/ci-tools_gl/-/jobs/{running_job_id})")
            return running_job_id
        else:
            print("No running jobs found in the latest pipeline.")
            exit()
    else:
        print(f"No pipelines found for branch {BRANCH_NAME}. please check following link:")
        print(f"https://gitlab.com/jltech_lab/ci-tools_gl/-/pipelines")
        return None

def get_job_logs(job_id):
        log_url = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/jobs/{job_id}/trace'
        response = requests.get(log_url, headers=get_gitlab_headers())
        if response.status_code == 200:
            return response.text
        else:
            print(f'Failed to get job logs: {response.status_code}, {response.text}')
            exit()

def get_pipeline_job_log(job_id):
    # 작업이 완료될 때까지 대기
    max_attempts = 10  # 최대 시도 횟수
    attempt = 0
    while attempt < max_attempts:
        response = requests.get(f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/jobs/{job_id}', 
                              headers=get_gitlab_headers())
        if response.status_code == 200:
            job_status = response.json()['status']
            if job_status in ['success', 'failed', 'canceled']:
                break
        print(f"작업 진행 중... ({attempt + 1}/{max_attempts})")
        time.sleep(5)  # 10초 간격으로 상태 확인
        attempt += 1

    print('\n\n===========Log Start===========\n')
    job_logs = get_job_logs(job_id).split('\n')
    log_start = False
    for log in job_logs:
        if log.startswith('%LogEnd%'):
            log_start = False
        if log_start:
            print(f'{log}')
        if log.startswith('%LogStart%'):
            log_start = True
    print('\n\n===========Log End===========\n')



# Step 1: Get the project ID (if not known)
def get_project_id(project_name):
    response = requests.get(f"{GITLAB_URL}/api/v4/projects?search={project_name}", headers=get_gitlab_headers())
    projects = response.json()
    for project in projects:
        if project['name'] == project_name:
            return project['id']
    return None

# Step 2: Get the latest pipeline ID for the branch
def get_latest_pipeline_id(project_id, branch_name):
    response = requests.get(f"{GITLAB_URL}/api/v4/projects/{project_id}/pipelines?ref={branch_name}", headers=get_gitlab_headers())
    pipelines = response.json()
    if pipelines:
        return pipelines[0]['id']
    return None

# Step 3: Get the running job ID from the pipeline

def get_last_git_commit_message():
    try:
        result = subprocess.run(['git', 'log', '-5', '--pretty=%B'], 
                              stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        raw_commit_messages = result.stdout.strip().split('\n') if result.stdout else []
        commit_messages = [msg for msg in raw_commit_messages if msg.startswith('fix') or msg.startswith('feat')]
        commit_messages_text = "\n".join(commit_messages)
        return commit_messages_text
    except Exception as e:
        print(f"Git commit message 가져오기 실패: {e}")
        return "commit message unavailable"

def get_command_arg1():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return None

def get_command_arg2():
    if len(sys.argv) > 2:
        return sys.argv[2]
    return None


def push_file(file_path, commit_message):
    BRANCH_NAME = 'main'
    FILE_PATH = f'{file_path.replace('\\','%2F')}'

    # Read the file content and encode it to base64
    with open(file_path, 'rb') as file:
        file_content = base64.b64encode(file.read()).decode()


    # API endpoint to create/update a file
    url = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/repository/files/{FILE_PATH}'
    print(f'{url}')

# Request payload
    data = {
     'branch': BRANCH_NAME,
     'content': file_content,
     'commit_message': commit_message,
     'encoding': 'base64'
    }

    # Make the request to create/update the file
    response = requests.post(url, headers=get_gitlab_headers(), json=data)

    if response.status_code == 201:
        print('File created successfully')
    elif response.status_code == 200:
        print('File updated successfully')
    else:
        print(f'Failed to upload file: {response.status_code}')
        print(response.json())
        exit()

def push_multiple_files(file_paths, commit_message):
    """여러 파일을 하나의 커밋으로 푸시하는 함수"""
    BRANCH_NAME = 'main'
    
    # 각 파일에 대한 액션 리스트 생성
    actions = []
    
    for file_path in file_paths:
        # 파일 경로를 GitLab에서 사용할 수 있는 형태로 변환
        # 절대 경로를 상대 경로로 변환하고 슬래시를 통일
        normalized_path = os.path.normpath(file_path)
        if os.path.isabs(normalized_path):
            # 절대 경로인 경우 파일명만 사용
            file_path_for_gitlab = os.path.basename(normalized_path)
        else:
            # 상대 경로인 경우 그대로 사용
            file_path_for_gitlab = normalized_path
        
        # 백슬래시를 슬래시로 변환 (Windows 경로 처리)
        file_path_for_gitlab = file_path_for_gitlab.replace('\\', '/')
        
        # 파일 내용을 base64로 인코딩
        with open(file_path, 'rb') as file:
            file_content = base64.b64encode(file.read()).decode()
        
        # 액션 추가
        action = {
            'action': 'create',  # 또는 'update'
            'file_path': file_path_for_gitlab,
            'content': file_content,
            'encoding': 'base64'
        }
        actions.append(action)
        print(f'파일 추가됨: {file_path} -> {file_path_for_gitlab}')
    
    # API endpoint for commits
    url = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/repository/commits'
    
    # Request payload
    data = {
        'branch': BRANCH_NAME,
        'commit_message': commit_message,
        'actions': actions
    }
    
    # Make the request to create the commit
    response = requests.post(url, headers=get_gitlab_headers(), json=data)
    
    if response.status_code == 201:
        print(f'여러 파일이 성공적으로 커밋되었습니다. 총 {len(file_paths)}개 파일')
        return True
    else:
        print(f'파일 커밋 실패: {response.status_code}')
        print(response.json())
        return False

def check_branch_exists(branch_name):
    """
    GitLab API를 사용하여 특정 브랜치가 존재하는지 확인하는 함수
    """
    try:
        if not branch_name or not branch_name.strip():
            print(f'❌ 브랜치 이름이 유효하지 않습니다: "{branch_name}"')
            return False
            
        # GitLab API endpoint for branches
        url = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/repository/branches/{branch_name}'
        
        # GitLab API 요청 실행
        response = requests.get(url, headers=get_gitlab_headers())
        
        if response.status_code == 200:
            print(f'✅ 브랜치 "{branch_name}" 존재함')
            return True
        elif response.status_code == 404:
            print(f'ℹ️ 브랜치 "{branch_name}" 존재하지 않음')
            return False
        elif response.status_code == 401:
            print(f'❌ GitLab 인증 실패 - 토큰을 확인해주세요')
            return False
        elif response.status_code == 403:
            print(f'❌ GitLab 접근 권한 없음 - 프로젝트 권한을 확인해주세요')
            return False
        else:
            print(f'❌ 브랜치 확인 실패: {response.status_code}')
            print(f'   응답: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ GitLab 서버 연결 실패 - 네트워크 연결을 확인해주세요")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ GitLab API 요청 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 브랜치 확인 중 예상치 못한 오류 발생: {str(e)}")
        return False

def create_branch_from_main(branch_name):
    """
    GitLab API를 사용하여 main 브랜치에서 새 브랜치를 생성하는 함수
    """
    try:
        if not branch_name or not branch_name.strip():
            print(f'❌ 브랜치 이름이 유효하지 않습니다: "{branch_name}"')
            return False
            
        # 브랜치 이름 유효성 검사 (GitLab 브랜치 이름 규칙)
        if any(char in branch_name for char in [' ', '..', '~', '^', ':', '?', '*', '[']):
            print(f'❌ 브랜치 이름에 유효하지 않은 문자가 포함되어 있습니다: "{branch_name}"')
            print('   브랜치 이름은 공백, .., ~, ^, :, ?, *, [ 등의 문자를 포함할 수 없습니다.')
            return False
            
        # GitLab API endpoint for creating branches
        url = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/repository/branches'
        
        # 브랜치 생성을 위한 request payload
        data = {
            'branch': branch_name,
            'ref': 'main'  # main 브랜치에서 새 브랜치 생성
        }
        
        # GitLab API 요청 실행
        response = requests.post(url, headers=get_gitlab_headers(), json=data)
        
        if response.status_code == 201:
            branch_data = response.json()
            print(f'✅ 브랜치 "{branch_name}" 생성 성공')
            print(f'   브랜치 생성 기준: main')
            return True
        elif response.status_code == 400:
            response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            if 'Branch already exists' in str(response_data):
                print(f'ℹ️ 브랜치 "{branch_name}"가 이미 존재합니다')
                return True  # 이미 존재하는 경우 성공으로 처리
            else:
                print(f'❌ 브랜치 생성 실패 - 잘못된 요청: {response.text}')
                return False
        elif response.status_code == 401:
            print(f'❌ GitLab 인증 실패 - 토큰을 확인해주세요')
            return False
        elif response.status_code == 403:
            print(f'❌ GitLab 접근 권한 없음 - 프로젝트 쓰기 권한을 확인해주세요')
            return False
        else:
            print(f'❌ 브랜치 생성 실패: {response.status_code}')
            print(f'   응답: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ GitLab 서버 연결 실패 - 네트워크 연결을 확인해주세요")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ GitLab API 요청 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 브랜치 생성 중 예상치 못한 오류 발생: {str(e)}")
        return False

def push_empty_commit(commit_message, site=None):
    """
    GitLab API를 사용하여 파일 변경 없이 commit message만으로 empty commit을 생성하는 함수
    site가 제공되면 해당 site 이름의 브랜치를 사용하거나 생성함
    """
    try:
        # site가 제공된 경우 브랜치 로직 처리
        if site:
            branch_name = site
            
            # 브랜치 존재 여부 확인
            if not check_branch_exists(branch_name):
                print(f'📝 브랜치 "{branch_name}"가 존재하지 않아 main에서 생성합니다.')
                if not create_branch_from_main(branch_name):
                    print(f'❌ 브랜치 생성 실패로 main 브랜치를 사용합니다.')
                    branch_name = 'main'
            else:
                print(f'📝 기존 브랜치 "{branch_name}"를 사용합니다.')
        else:
            branch_name = 'main'
        
        # GitLab API endpoint for commits
        url = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/repository/commits'
        
        # Empty commit을 위한 request payload (actions 배열이 비어있으면 empty commit)
        data = {
            'branch': branch_name,
            'commit_message': commit_message,
            'actions': []  # 빈 actions 배열로 empty commit 생성
        }
        
        # GitLab API 요청 실행
        response = requests.post(url, headers=get_gitlab_headers(), json=data)
        
        if response.status_code == 201:
            commit_data = response.json()
            commit_id = commit_data.get('id', 'unknown')
            print(f'✅ Empty commit 생성 성공')
            print(f'   브랜치: {branch_name}')
            print(f'   Commit ID: {commit_id[:8]}...')
            print(f'   Message: {commit_message}')
            return True
        else:
            print(f'❌ Empty commit 생성 실패: {response.status_code}')
            print(f'   응답: {response.text}')
            return False
            
    except Exception as e:
        print(f"❌ Empty commit 생성 중 오류 발생: {str(e)}")
        return False

def runner_command(VARIABLES, site=None):
    TRIGGER_TOKEN = 'glptt-afc45e88e8264516e1442b1266a10d4964e4ff54'
    TRIGGER_URL = f'{GITLAB_URL}/api/v4/projects/{CI_TOOLS_PROJECT_ID}/trigger/pipeline'
    
    # site가 제공되면 해당 site를 ref로 사용, 그렇지 않으면 main 사용
    ref_branch = site if site else 'main'
    
    payload = {
        'token': TRIGGER_TOKEN,
        'ref': ref_branch,
        **{f'variables[{key}]': value for key, value in VARIABLES.items()}
    }

    # Make the API request to trigger the pipeline
    response = requests.post(TRIGGER_URL, data=payload, headers=get_gitlab_headers())
    response_data = response.json()
    pipeline_id = response_data.get('id')
    get_pipeline_job_log(get_pipeline_job_id(pipeline_id))

def get_latest_file(folder_name,extension):
    files = glob.glob(f'{folder_name}/*.{extension}')
    files = [f for f in files if not f.endswith('firmware.bin')] 
    latest_file = max(files, key=os.path.getctime) if files else None

    if latest_file:
        print(f"Latest {extension} file: {latest_file}")
    else:
        print(f"No {extension} files found in the {folder_name} folder.")
        exit()
    return latest_file

def get_or_create_site_folder(service, parent_folder_id, site_name):
    """
    지정된 부모 폴더에서 site 폴더를 찾거나 생성합니다.
    """
    try:
        # site 폴더가 이미 존재하는지 확인
        query = f"name='{site_name}' and parents in '{parent_folder_id}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            # 폴더가 이미 존재함
            folder_id = folders[0]['id']
            print(f"✅ 기존 site 폴더 사용: {site_name} (ID: {folder_id})")
            return folder_id
        else:
            # 폴더가 존재하지 않으므로 생성
            folder_metadata = {
                'name': site_name,
                'parents': [parent_folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = service.files().create(
                body=folder_metadata,
                fields='id, name',
                supportsAllDrives=True
            ).execute()
            
            folder_id = folder.get('id')
            print(f"📁 새 site 폴더 생성: {site_name} (ID: {folder_id})")
            return folder_id
            
    except Exception as e:
        print(f"❌ site 폴더 생성/확인 중 오류: {str(e)}")
        # 오류 발생 시 원래 부모 폴더 ID 반환
        return parent_folder_id

def check_existing_file(service, folder_id, file_name):
    """
    지정된 폴더에서 같은 이름의 파일이 이미 존재하는지 확인합니다.
    """
    try:
        # 같은 이름의 파일이 이미 존재하는지 확인
        query = f"name='{file_name}' and parents in '{folder_id}' and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, createdTime)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            # 파일이 이미 존재함 (여러 개가 있을 경우 가장 최근 것 반환)
            existing_file = files[0]  # 첫 번째 파일 사용
            file_id = existing_file['id']
            print(f"🔍 기존 파일 발견: {file_name} (ID: {file_id})")
            return file_id
        else:
            # 파일이 존재하지 않음
            return None
            
    except Exception as e:
        print(f"❌ 기존 파일 확인 중 오류: {str(e)}")
        return None

def upload_gdrive(file_path, site):
    """
    Service Account를 이용한 Google Drive 파일 업로드
    site 폴더를 생성하고 그 안에 파일을 업로드
    """
    try:
        # Google Drive API 설정
        # https://drive.google.com/drive/folders/1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf
        GDRIVE_FOLDER_ID = '1B_Fa0AC7tbc7TSlFQSymIBiF-Cqz7hMf'
        SERVICE_ACCOUNT_FILE = get_service_account_file()
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # 필요한 라이브러리 import
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        from google.oauth2 import service_account
        
        # Service Account 파일 존재 확인
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"오류: Service Account 파일을 찾을 수 없습니다: {SERVICE_ACCOUNT_FILE}")
            return None
        
        # Service Account 인증 정보 로드
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        
        # Drive API 서비스 생성
        service = build('drive', 'v3', credentials=credentials)
        
        # site 폴더 확인 및 생성
        site_folder_id = get_or_create_site_folder(service, GDRIVE_FOLDER_ID, site)
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            print(f"오류: 업로드할 파일을 찾을 수 없습니다: {file_path}")
            return None
        
        file_name = os.path.basename(file_path)
        
        # 같은 이름의 파일이 이미 존재하는지 확인
        existing_file_id = check_existing_file(service, site_folder_id, file_name)
        if existing_file_id:
            print(f'✅ 기존 파일 사용: {file_name}')
            print(f'   파일 ID: {existing_file_id}')
            print(f'   Google Drive 링크: https://drive.google.com/file/d/{existing_file_id}/view')
            return existing_file_id
        
        # 파일 메타데이터 설정
        file_metadata = {
            'name': file_name,
            'parents': [site_folder_id]
        }
        
        # 미디어 업로드 객체 생성
        media = MediaFileUpload(file_path)
        
        print(f"📤 Google Drive 업로드 시작: {file_name}")
        
        # 파일 업로드 실행 (Shared Drive 지원)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, parents',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        file_name = file.get('name')
        
        print(f'✅ 파일이 성공적으로 업로드되었습니다.')
        print(f'   파일명: {file_name}')
        print(f'   파일 ID: {file_id}')
        print(f'   Google Drive 링크: https://drive.google.com/file/d/{file_id}/view')
        
        return file_id
        
    except HttpError as e:
        error_details = e.content.decode('utf-8') if e.content else str(e)
        print(f'❌ Google Drive API 오류: {e}')
        
        # 스토리지 할당량 오류 처리
        if "storageQuotaExceeded" in error_details:
            print("🔧 해결 방법: Service Account는 Shared Drive 사용이 필요합니다.")
            print("   1. Google Drive에서 공유 드라이브 생성")
            print("   2. Service Account를 공유 드라이브에 편집자 권한으로 추가")
            print("   3. 공유 드라이브 내 폴더 ID 사용")
        elif e.resp.status == 404:
            print("🔧 해결 방법: 폴더 접근 권한을 확인해주세요.")
            print("   1. 폴더 ID가 올바른지 확인")
            print("   2. Service Account를 폴더에 편집 권한으로 공유")
        
        return None
        
    except Exception as e:
        print(f'❌ Google Drive 업로드 중 오류 발생: {str(e)}')
        return None

def upload_file(folder,extension,command_args):
    site = command_args.split('|')[1] if '|' in command_args else command_args

    latest_file = get_latest_file(folder,extension)
    file_id = upload_gdrive(latest_file, site)

    # 파일 업로드 실패 시 처리
    if file_id is None:
        print("❌ Google Drive 업로드 실패로 인해 작업을 중단합니다.")
        exit()

    last_commit_message = get_last_git_commit_message()
    COMMIT_MESSAGE = f'{latest_file.replace(folder + "\\", "")}[{command_args}|{file_id}]\n{last_commit_message}'
        
    success = push_empty_commit(COMMIT_MESSAGE, site)
    if not success:
        print("Empty commit 푸시 실패합니다.")
        exit()
    print(f"✅ COPY 명령 완료: empty commit 생성됨")
    return site


def get_jltech_rnd_runners():
    # GitLab API 설정
    GITLAB_URL =get_gitlab_info('url')
    GITLAB_TOKEN = get_gitlab_info('token')
    GROUP_ID = "10854409"
    # 그룹의 러너 가져오기
    url = f"{GITLAB_URL}/api/v4/groups/{GROUP_ID}/runners"
    response = requests.get(url, headers=get_gitlab_headers())

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"러너 정보를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
    

def check_runner_status(runner_name):
    runners = get_jltech_rnd_runners()
    if runner_name == 'list':
        try:
            for runner in runners:
                if runner['description'].startswith('adev-'):
                    print(f"status: {runner['status']}\trunner: {runner['description'].split('-')[1]}")
        except Exception as e:
            print(f"오류 발생: {str(e)}")
        sys.exit(0)
    else:
        for runner in runners:
            if runner['description'] == f'adev-{runner_name}' and runner['status'] == 'online':
                print(f"runner: {runner['description'].split('-')[1]} is online")
                break
        else:
            print(f"Runner [{runner}] not found or is not online")
            exit()
class SingletonConfig:
    _instance = None
    _lock = threading.Lock()
    _config_file = pathlib.Path.home() / ".adev_config.yml"

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        print(self._config_file)
        if self._config_file.exists():
            with open(self._config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            print(f"오류: 설정 파일을 찾을 수 없습니다: {self._config_file}")
            print("설정 파일을 생성하거나 올바른 위치에 배치해주세요.")
            sys.exit(1)

    def save_config(self):
        with open(self._config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True)

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

def config():
    return SingletonConfig.get_instance()

def get_user_info(field):
    return config().get('environment', {}).get('user', {}).get(field, '')

def get_gitlab_info(field):
    return config().get('environment', {}).get('gitlab', {}).get(field, '')

def get_jira_info(field):
    return config().get('environment', {}).get('jira', {}).get(field, '')

def get_dev_folder():
    return f"{config().get('environment', {}).get('root_folder', '')}dev"

def get_artwork_folder():
    return f"{config().get('environment', {}).get('root_folder', '')}artwork"

def get_service_account_file():
    """
    Service Account 키 파일 경로를 반환합니다.
    기본값: {dev_folder}/service-account-key.json
    """
    return f"{get_dev_folder()}/service-account-key.json"

def get_gitlab_headers():
    headers = {
        'Private-Token': get_gitlab_info('token')
    }
    return headers