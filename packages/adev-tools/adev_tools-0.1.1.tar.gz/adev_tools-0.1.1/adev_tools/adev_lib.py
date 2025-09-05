import os
import re
import sys
import requests
import subprocess
from tabulate import tabulate
from urllib.parse import quote
import threading
from gitlab import Gitlab
from jira import JIRA
from git import Repo
import yaml
import pathlib
import json
import time
from typing import Optional
import logging
import ollama
import urllib.parse



# 로깅 설정 추가
logging.basicConfig(level=logging.INFO)

def get_or_create_component(jira_client,project_key, component_name):
    # Get all components in the project
    components = jira_client.project_components(project_key)
    
    # Check if component exists
    for component in components:
        if component.name == component_name:
            return component
    
    # If not, create the component
    print(f"Creating component '{component_name}'...")
    new_component = jira_client.create_component(
        name=component_name,
        project=project_key,
        description="Component created via Python API",
        assigneeType="PROJECT_LEAD",  # Optional: Set component lead
    )
    return new_component

class SingletonJira:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, url, auth):
        self.jira_client = JIRA(url, basic_auth=auth)
        repo = Repo('.')  # Path to Git repository
        repo_name = os.path.basename(repo.working_tree_dir)
        project_key, component, platform = parseProjectName(repo_name)
        self.project = self.jira_client.project(project_key)
        if self.project is None:
            print("JiraProject not found")
            sys.exit(0)

        self.component = get_or_create_component(self.jira_client,project_key, component)
        self.platform = platform

    @classmethod
    def get_instance(cls, url=None, auth=None):
        with cls._lock:
            if cls._instance is None:
                # First initialization requires URL and auth
                if url is None or auth is None:
                    raise ValueError("URL and auth must be provided for the first initialization.")
                cls._instance = cls(url, auth)
            else:
                # Prevent reinitialization with new parameters
                if url is not None or auth is not None:
                    raise ValueError("SingletonJira already initialized. Do not provide parameters.")
            return cls._instance

def jl_init():
    try:
        jl =SingletonJira.get_instance(
            url=get_jira_info('url'),
            auth=(get_user_info('email'), get_jira_info('api_token'))
        )
    except ValueError as e:
        print(e)

def jl_client():
    return SingletonJira.get_instance().jira_client

def jl_project():
    return SingletonJira.get_instance().project

def jl_component():
    return SingletonJira.get_instance().component

def jl_platform():
    if (SingletonJira.get_instance().platform == "py"):
        return "python"
    elif (SingletonJira.get_instance().platform == "pio"):
        return "platformio"
    elif (SingletonJira.get_instance().platform == "qt6"):
        return "qt6"
    elif (SingletonJira.get_instance().platform == "gl"):
        return "gitlab_ci/cd"
    else:
        return SingletonJira.get_instance().platform 
class SingletonGitlab:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Prevent direct instantiation
        raise RuntimeError("Use get_instance() instead.")

    @classmethod
    def get_instance(cls, **kwargs):
        with cls._lock:
            if cls._instance is None:
                # Bypass __new__ to create an instance
                instance = object.__new__(cls)
                # Initialize the GitLab client with provided parameters
                instance.gitlab_client = Gitlab(**kwargs)
                cls._instance = instance
                # Initialize the project details from the Git repository and GitLab
                instance._initialize_project()
            else:
                # If the singleton already exists, do not accept new parameters
                if kwargs:
                    raise ValueError("SingletonGitlab already initialized. Do not provide parameters.")
            return cls._instance

    def _initialize_project(self):
        """
        Initializes the GitLab project by:
         - Loading the local Git repository.
         - Extracting the project name and full path.
         - Determining the GitLab group (or subgroup) based on repository URL.
         - Searching for and setting the corresponding GitLab project.
        """
        # Load the local Git repository (assumes the current directory is a Git repo)
        repo = Repo('.')  # Path to Git repository

        # Extract the project name and its full path (namespace included)
        project_name = os.path.basename(repo.working_tree_dir)
        project_name_with_path = repo.remotes.origin.url.split(':')[1].replace('.git', '')

        # Retrieve the GitLab group using configuration info
        group = self.gitlab_client.groups.get(get_gitlab_info('group_id'))

        # Check if the project is in a subgroup (more than two parts in the path)
        if len(project_name_with_path.split('/')) > 2:
            subgroup_name = project_name_with_path.split('/')[1]
            try:
                # Attempt to find the subgroup by searching for it
                sub_groups = group.subgroups.list(search=quote(subgroup_name))
                search_group = next((self.gitlab_client.groups.get(sub_group.id) for sub_group in sub_groups if sub_group.path == subgroup_name), None)

                if search_group is None:
                    raise ValueError(f"Subgroup '{subgroup_name}'을(를) 찾을 수 없습니다.")

            except Exception as e:
                print(f"Subgroup '{subgroup_name}'을(를) 가져오지 못했습니다: {e}")
                sys.exit(1)
        else:
            search_group = group

        # Search for the project within the group (or subgroup)
        projects = search_group.projects.list(search=quote(project_name))
        self.project = None
        for project in projects:
            if project.path_with_namespace == project_name_with_path:
                # If a matching project is found, retrieve its details via GitLab API
                self.project = self.gitlab_client.projects.get(project.id)
                break

        if self.project is None:
            print("GitlabProject not found")
            sys.exit(0)

def gl_init():
    try:
        gl = SingletonGitlab.get_instance(
            url=get_gitlab_info('url'),
            private_token=get_gitlab_info('token')
        )
    except ValueError as e:
        print(e)

def gl_client():
    return SingletonGitlab.get_instance().gitlab_client

def gl_project():
    return SingletonGitlab.get_instance().project




def gitlab_rest_api(method, uri, data=None):
    headers = {"PRIVATE-TOKEN": os.environ.get("GITLAB")}
    try:
        if data:
            response = requests.request(method, uri, headers=headers, json=data)
        else:
            response = requests.request(method, uri, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"{e}\n{method} Error: {uri}")

def get_main_projects(project_list, group, regexp=None, company=None):
    global JOB
    if regexp == "-all":
        regexp = "_altium" if JOB == "ALTIUM" else ""

    if company:
        print(f"(1) {group}/{company} group 프로젝트를 검색중입니다.", flush=True)
        url_encode = quote(f"{group}/{company}")
        projects = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/projects?per_page=100")
        for project in projects:
            if re.search(regexp, project["path"]):
                project_list.append(project)

        sub_groups = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/subgroups?per_page=100")
        for sub_group in sub_groups:
            sub_path = sub_group["path"]
            if not sub_path.startswith('_'):
                print(f"{group}/{company}/{sub_path} group 프로젝트를 검색중입니다.", flush=True)
                try:
                    url_encode = quote(f"{group}/{company}/{sub_path}")
                    sub_projects = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/projects?per_page=100")
                    for project in sub_projects:
                        if re.search(regexp, project["path"]):
                            project_list.append(project)
                except Exception:
                    pass
    elif not regexp or regexp == "_altium":
        print(f"(2) {group} group 프로젝트를 검색중입니다.", flush=True)
        url_encode = quote(group)
        try:
            projects = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/projects?per_page=100")
            for project in projects:
                if re.search(regexp, project["path"]):
                    project_list.append(project)
        except Exception:
            pass

        sub_groups = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/subgroups?per_page=100")
        for sub_group in sub_groups:
            sub_path = sub_group["path"]
            if not sub_path.startswith('_') and not re.search(r'fork', sub_path):
                url_encode = quote(f"{group}/{sub_path}")
                print(f"{group}/{sub_path} group 프로젝트를 검색중입니다.", flush=True)
                sub_projects = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/projects?per_page=100")
                for project in sub_projects:
                    if re.search(regexp, project["path"]):
                        project_list.append(project)
    else:
        print(f"(3) {group} group 프로젝트를 검색중입니다.", flush=True)
        try:
            url_encode= urllib.parse.quote(group,safe='')
            projects = gitlab_rest_api("GET", f"https://gitlab.com/api/v4/groups/{url_encode}/search?scope=projects&search={regexp}&per_page=100")
            for project in projects:
                if not re.search(r'fork', project["path_with_namespace"]):
                    project_list.append(project)
        except Exception:
            pass

def clone_project(project, userid=None):
    if re.search(r"_altium$", project["path"], re.IGNORECASE):
        clone_folder = os.environ.get("ARTWORK")
    else:
        clone_folder = os.environ.get("DEV")

    if userid:
        clone_folder = os.path.join(clone_folder, "_fork", userid)
    else:
        clone_folder = os.path.join(clone_folder, "upstream")

    proj_folder_path = os.path.join(clone_folder, project["path"])
    if os.path.exists(proj_folder_path):
        print("===== 이미 clone이 된 상태입니다. clone 된 폴더로 이동합니다.", flush=True)
        print(proj_folder_path, flush=True)
        with open(os.path.expanduser('~/.chdir.txt'), 'w') as f:
            f.write(proj_folder_path)
    else:
        if not os.path.exists(clone_folder):
            os.makedirs(clone_folder)
        os.chdir(clone_folder)
        subprocess.run(["git", "clone", project["ssh_url_to_repo"]], check=True)
        print(f"==== clone {project['web_url']} project ====", flush=True)
        print(proj_folder_path, flush=True)
        with open(os.path.expanduser('~/.chdir.txt'), 'w') as f:
            f.write(proj_folder_path)

def select_option(message, options):
    while True:
        try:
            choice = int(input(f"{message} (0-{len(options)-1}): "))
            if choice <= len(options)-1:
                return options[choice]
            elif  choice == 0:
                return None
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")
    return None

def list_select(title, message, options, display_list=None):
    if display_list == None:
        display_list = options

    if not options:
        return None
    
    if (len(options) == 1):
        return options[0]
    # 0번을 Exit 옵션으로 추가
    numbered = [[0, "Exit"]] + [[i+1, display] for i, display in enumerate(display_list)]
    print(tabulate(numbered, headers=['No', title], tablefmt='simple'))

    selected = select_option(message, ["Exit"] + options)
    return None if selected == "Exit" else selected


def env_setup():
    global JOB
    cwd = os.getcwd()
    if re.search(r"artwork", cwd, re.IGNORECASE):
        JOB = 'ALTIUM'
    elif re.search(r"dev", cwd, re.IGNORECASE):
        JOB = 'DEV'

def confirm(title, question, default=True):
    decision = input(f"[{title}]{question}(yes/no)(default: {'y' if default else 'n'}): ").lower()
    if decision in ['y', 'yes', 'Y']:
        return True
    elif decision in ['n', 'no', 'N']:
        return False
    else:
        return default

def get_gitlab_project(path_with_namespace):
    proj_path = quote(path_with_namespace)
    url = f"https://gitlab.com/api/v4/projects/{proj_path}"
    print(url)
    try:
        response = requests.get(url, headers={"PRIVATE-TOKEN": get_gitlab_info('token')})
        print(response)
        response.raise_for_status()
        print(response)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{proj_path} path does not exist.", file=sys.stderr)
        return None

def send_slack_message(command, issue, param):
    # Determine Slack webhook URL
    if command == "fork":
        slack_url = "https://hooks.slack.com/services/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"
    else:
        user_name_eng = get_user_info('name_eng')
        if user_name_eng == "jmyu":
            slack_url = "https://hooks.slack.com/services/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"
        elif user_name_eng == "dskim":
            slack_url = "https://hooks.slack.com/services/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"
        elif user_name_eng == "romeo":
            slack_url = "https://hooks.slack.com/services/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"
        elif user_name_eng == "jhk":
            slack_url = "https://hooks.slack.com/services/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"
        elif user_name_eng == "mckim":
            slack_url = "https://hooks.slack.com/services/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"
        elif user_name_eng == "mhkim":
            slack_url = "https://hooks.slack.com/services/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"
        elif user_name_eng == "jsjung":
            slack_url = "https://hooks.slack.com/services/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"
        else:
            slack_url = "https://hooks.slack.com/services/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"

    # Build message components
    attachment = {
        "color": "#FF0000",  # Red color
        "fallback": f"SP Noti By {os.environ.get('USER_NAME', '')}",
        "author_name": os.environ.get("USER_NAME", "")
    }

    if command == "fork":
        if (issue):
            attachment.update({
            "title": f"Gitlab:{param.get('name', '')}",
            "title_link": param.get("web_url", ""),
            "text": f"<https://jltechrnd.atlassian.net/browse/{issue.get('key', '')}|{issue.get('key', '')} {issue.get('summary', issue.get('fields', {}).get('summary', ''))}>",
            "pretext": param.get("ssh_url_to_repo", "")
            })
        else:
            attachment.update({
                "title": f"Gitlab:{param.get('name', '')}",
                "title_link": param.get("web_url", ""),
                "text": param.get("ssh_url_to_repo", ""),
                "pretext": param.get("web_url", "")
            })
    elif command == "comment":
        # add_dev_history(issue, param)  # Uncomment if you implement this function
        attachment.update({
            "title": f"{issue.get('key', '')} ({issue.get('status', issue.get('fields', {}).get('status', {}).get('name', ''))}) {issue.get('summary', issue.get('fields', {}).get('summary', ''))}",
            "title_link": f"https://jltechrnd.atlassian.net/browse/{issue.get('key', '')}",
            "text": param,
            "pretext": f"{issue.get('key', '')} 댓글이 추가 되었습니다"
        })
    elif command == "commit":
        attachment.update({
            "title": f"commit:{param.get('path_with_namespace', '')} branch:{param.get('current_branch_name', '')}",
            "text": param.get("message", ""),
            "pretext": f"[https://jltechrnd.atlassian.net/browse/{issue.get('key', '')}]에 댓글이 추가 되었습니다"
        })
    elif command == "push":
        url_branch_name = quote(param.get("current_branch_name", ""))
        project_id = param.get("working_repo", {}).get("id", "")
        commits = requests.get(
            f"https://gitlab.com/api/v4/projects/{project_id}/repository/commits?ref_name={url_branch_name}"
        ).json()
        last_commit = commits[0] if commits else {}

        attachment.update({
            "title": f"commit:{param.get('working_repo', {}).get('path_with_namespace', '')} branch:{param.get('current_branch_name', '')}",
            "title_link": last_commit.get("web_url", ""),
            "text": param.get("message", ""),
            "pretext": f"[https://jltechrnd.atlassian.net/browse/{issue.get('key', '')}]에 댓글이 추가 되었습니다"
        })
    elif command == "hotfix":
        attachment.update({
            "title": f"{issue.get('key', '')} ({issue.get('status', issue.get('fields', {}).get('status', {}).get('name', ''))}) {issue.get('summary', issue.get('fields', {}).get('summary', ''))}",
            "title_link": f"https://jltechrnd.atlassian.net/browse/{issue.get('key', '')}",
            "text": f"- origin: {param.get('web_url', '')}\n - upstream: {param.get('forked_from_project', {}).get('web_url', '')}",
            "pretext": f"{issue.get('key', '')} hotfix"
        })

    # Send message to Slack
    payload = {"attachments": [attachment]}
    response = requests.post(slack_url, json=payload)
    return response.status_code == 200

def parseProjectName(repo_name):
    pattern = r'^([^-]+)-([^_]+)_(.*)$'
    match = re.match(pattern, repo_name)
    if match:
        project_key = match.group(1).upper()
        component = match.group(2).upper()
        platform = match.group(3).upper()
        return project_key, component, platform
    return None, None, None


def get_jira_project(project_key):
    try:
        project = jl_client().project(project_key)
        return {
            'id': project.id,
            'key': project.key,
            'name': project.name
        }
    except Exception as e:
        print(f"프로젝트 정보를 가져오는데 실패했습니다: {e}", file=sys.stderr)
        return {}

def get_project_inherited_members():
    try:
        # Get direct project members
        project_members = gl_project().members.list(all=True)
        # Dictionary to store unique members (avoid duplicates)
        all_members = {m.id: m for m in project_members}

        # Check if the project belongs to a group
        if gl_project().namespace['kind'] == 'group':
            group_id = gl_project().namespace['id']
            group = gl_client().groups.get(group_id)

            # Get all inherited members from the group (including subgroups)
            group_members = group.members.list(all=True)
            for m in group_members:
                all_members[m.id] = m  # Ensure uniqueness
        # Format output with necessary details
        return [{"id": m.id, "username": m.username, "name": m.name, "access_level": m.access_level} for m in all_members.values()]

    except Gitlab.exceptions.GitlabGetError as e:
        return f"Error fetching members: {e}"

def set_user_info():
    # Project name and namespace (e.g., "your_group/your_project")
    #get prarent group
    members = get_project_inherited_members()
    for member in members:
        if member['name'] == get_user_info('name_eng'):
            user_level = member['access_level']
            gitlab_user_id = member['id']
            break

    if user_level == 50:
        gitlab_user_permission = 'Owner'
    elif user_level == 40:
        gitlab_user_permission = 'Maintainer'
    elif user_level == 30:
        gitlab_user_permission = 'Developer'
    elif user_level == 20:
        gitlab_user_permission = 'Reporter'
    else:
        gitlab_user_permission = None

    return gitlab_user_permission,gitlab_user_id

def open_chrome(url):
    PROFILE = config().get('environment', {}).get('chrome', {}).get('profile', 'Default')
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome_path = next((path for path in possible_paths if os.path.exists(path)), None)
    subprocess.Popen([chrome_path, url, f'--profile-directory={PROFILE}'])

def get_status_prefix(status: str) -> str:
    """
    상태에 따른 prefix를 반환합니다
    진행중: *
    완료됨: !
    그 외: 공백
    """
    status_prefix_map = {
        "진행중": "*",
        "완료됨": "!"
    }
    return status_prefix_map.get(status, " ")

def jiraIssues(jql):
    limit = 99 
    issues = jl_client().search_issues(jql, maxResults=99)

    issueList = []
    for issue in issues:
        linked_issues =','.join([i.outwardIssue.key for i in issue.fields.issuelinks if hasattr(i, 'outwardIssue')])
        linked_issues +=','.join([i.inwardIssue.key for i in issue.fields.issuelinks if hasattr(i, 'inwardIssue')])
        status = issue.fields.status.name.replace(' ', '')

        #진행중:* 완료됨:!
        prefix = get_status_prefix(status)

        parent_display = ""
        if hasattr(issue.fields,'parent'): 
            if issue.fields.parent.fields.issuetype.name == '에픽':
                parent_display = f"(EPIC)[{issue.fields.parent.key}]{issue.fields.parent.fields.summary}"
            else:
                parent_display = f"[{issue.fields.parent.key}]{issue.fields.parent.fields.summary}"
        issue_display = f"{prefix}[{issue.key}]{issue.fields.summary}"
        issueList.append({
                'issueObject': issue,
                'updated': issue.fields.updated,
                'Parent': parent_display,
                'Component': ', '.join([c.name for c in issue.fields.components]),
                'IssueType': issue.fields.issuetype.name,
                'Assignee': issue.fields.assignee.displayName if issue.fields.assignee else '',
                'LinkedIssue': linked_issues,
                'Issue': issue_display
            })
    return issueList

def get_issue_from_list(jql,prompt="Issue를 선택해주세요:"):
    issueList = jiraIssues(jql)

    tableData = []
    for issue in issueList:
        tableData.append({
            'Component': issue['Component'],
            'IssueType': issue['IssueType'].strip(),
            'Assignee': issue['Assignee'],
            'Jira Issue': issue['Issue'],
            'Parent': issue['Parent'],
            'LinkedIssue': issue['LinkedIssue']
        })

    # 'Exit'을 포함한 헤더를 추가하여 테이블 형식으로 출력
    tableData.insert(0, {
        'Component': 'Exit',
        'IssueType': '',
        'Assignee': '',
        'Jira Issue': '',
        'Parent': '',
        'LinkedIssue': ''
    })
    # 테이블 형식으로 출력
    print(tabulate(tableData, headers='keys', tablefmt='simple', showindex=range(0, len(tableData)), numalign='left', stralign='left'))
    issue_key = select_option(prompt, ["Exit"]+[issue['Issue'].split('[')[1].split(']')[0] for issue in issueList])
    if issue_key == 'Exit':
        sys.exit(0)
    return issue_key


class SingletonConfig:
    _instance = None
    _lock = threading.Lock()
    _config_file = pathlib.Path.home() / ".adev_config.yml"

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        if self._config_file.exists():
            with open(self._config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            print("config file not found")
            return {}

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
    return f"{config().get('environment', {}).get('root_folder', '')}/dev"

def get_artwork_folder():
    return f"{config().get('environment', {}).get('root_folder', '')}/artwork"


def get_staged_changes(repo_path='.'):
    """GitPython을 사용하여 스테이징된 변경 사항을 diff 형식으로 가져옵니다."""
    try:
        repo = Repo(repo_path)
        diff = repo.git.diff('--staged')
        return diff

    except Repo.exc.InvalidGitRepositoryError:
        print(f"Error: Not a git repository: {repo_path}")
        return None
    except Repo.exc.GitCommandError as e:
        print(f"Error getting staged changes: {e}")
        return None



def generate_commit_message_ollama_ko(messages):
    """Generates a commit message in Korean, using the Ollama API."""
    api_url = config().get('environment', {}).get('ollama', {}).get('default_model_api_url', '')
    model = config().get('environment', {}).get('ollama', {}).get('default_model', '')

    print(f"Generating Korean commit message with Ollama model: {model}")

    prompt = f"""
    You are a helpful and harmless AI assistant. Summarize the following commit message in Korean. 
    Do not include an introductory phrase like "Here is..." or "...Here is:".

    Commit Message:
    {messages}

    Summary in Korean:
    """

    headers = {'Content-Type': 'application/json'}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        summary_message = result['response']
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        return summary_message
    except requests.exceptions.RequestException as e:
        print(f"Error generating commit message: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing Ollama API response: {e}")
        return None
    
def get_ollama_response(model,prompt):
    api_url = config().get('environment', {}).get('ollama', {}).get('url', '')
    client = ollama.Client(host=api_url)
    try:
        start_time = time.time()

        response = client.generate(
            model=model,
            prompt=prompt,
        )                            
        message = response['response']
        if message.startswith("```") and message.endswith("```"):
            message = message[3:-3].strip()  # "```" 제거
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        return message
    except requests.exceptions.RequestException as e:
        print(f"Error generating commit message: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing Ollama API response: {e}")
        return None

def create_commit_message_with_ollama():
    diff = get_staged_changes()
    model = config().get('environment', {}).get('ollama', {}).get('commit_message_model', '')

    print(f"Generating English commit message with Ollama model: {model}")

    prompt = f"""
    Generate a Git commit message for the changes below. Use conventional commit format in plain text. if first line is plaintext Do not include.

    Diff:
    ```diff
    {diff}
    ```

    Commit Message in English:
    """
    return get_ollama_response(model,prompt)


def commit_changes(repo_path, message):
    """GitPython을 사용하여 생성된 커밋 메시지로 git commit을 수행합니다."""
    try:
        repo = Repo(repo_path)
        repo.git.commit('-m', message)
        print("Commit successful!")
    except Repo.exc.GitCommandError as e:
        logging.error(f"Error committing changes: {e}")

def adev_init():
    """Initializes the ADEV configuration."""
    if config() != {}:
        jl_init()  # Jira 초기화
        gl_init()  # Gitlab 초기화
    else:
        logging.error("Config file not found")
        sys.exit(0)

def get_openai_config():
    """OpenAI API 설정을 가져옵니다."""
    config_data = config().get('environment', {})
    api_key = config_data.get('openai', {}).get('api_key', '')
    model = config_data.get('openai', {}).get('model', 'gpt-4o-mini')
    if not api_key:
        raise ValueError("API 키가 설정되어 있지 않습니다.")
    return api_key, model