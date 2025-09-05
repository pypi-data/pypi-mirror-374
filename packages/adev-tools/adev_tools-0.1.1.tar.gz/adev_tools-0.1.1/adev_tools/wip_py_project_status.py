import os
import re
import sys
import argparse
import json
import subprocess
from collections import defaultdict
from typing import List, Dict, Any
import requests
from requests.auth import HTTPBasicAuth
from jira import JIRA
from git import Repo
import adev_lib as adev
import gitlab 
from urllib.parse import quote
from tabulate import tabulate
import wcwidth

def wide_len(s):
    return sum(wcwidth.wcwidth(c) if wcwidth.wcwidth(c) > 0 else 1 for c in s)

# Global variables
JOB = None
project_key = None
component = None
platform = None
working_repo = None
user_permission = None
user_level = None
gitlab_user_id = None
current_version = None
current_branch_name = None
cred = None  # Placeholder for Jira credentials

def env_setup():
    global JOB
    if re.search(r"artwork", os.getcwd(), re.IGNORECASE):
        JOB = 'ALTIUM'
    elif re.search(r"dev", os.getcwd(), re.IGNORECASE):
        JOB = 'DEV'

def init():
    env_setup()

def check_folder():
    global project_key, component, platform, JOB,forkedOnlyCmd
    remote_origin = ""
    if os.path.exists("./.git"):
        remote_origin = subprocess.check_output(["git", "remote", "-v"]).decode()
        remote_origin = [line for line in remote_origin.splitlines() if "origin" in line and "push" in line][0]
        if "http" in remote_origin:
            print("Remote Repository를 ssh로 해주세요")
            sys.exit(0)

        if forkedOnlyCmd:
            match = re.search(r':(.*/[^/]*).git', remote_origin)
            path_with_namespace = match.group(1)
            if not re.search(r'/fork/', path_with_namespace):
                print("fork 된 프로젝트가 아닙니다", file=sys.stderr)
                sys.exit(0)
    else:
        print("git 폴더가 없습니다", file=sys.stderr)
        sys.exit(0)

def gitlab_rest_api(method, uri, data=None):
    headers = {"PRIVATE-TOKEN": os.getenv("GITLAB")}
    try:
        if data:
            response = requests.request(method, uri, headers=headers, json=data)
        else:
            response = requests.request(method, uri, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"{e}\n{method} Error:{uri}")
    return response.json()



def set_user_info():
    # Project name and namespace (e.g., "your_group/your_project")
    #get prarent group
    members = adev.get_project_inherited_members()
    for member in members:
        if member['name'] == os.getenv("USER_NAME"):
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

def display_project_info():
    # 버전 정보 가져오기
    # versions = [v for v in get_jira_versions(project_key) if re.match(component, v['name']) and v.get('startDate') and not v.get('releaseDate')]
    # if not versions:
    #     print("버전 정보가 없습니다. version 명령으로 버젼을 설정해주세요", file=sys.stderr)
    # elif len(versions) == 1:
    #     global current_version
    #     current_version = versions[0]['name']
    # else:
    #     print("다수의 Open된 버전이 존재합니다.", file=sys.stderr)
    gitlab_user_permission,gitlab_user_id = set_user_info()
    global current_branch_name
    current_branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    print(f"컴포넌트:{adev.jl_component()}  권한:{gitlab_user_permission} branch:{current_branch_name}")

def jiraIssues(jql):
    limit = 99 
    issues = adev.jl_client().search_issues(jql, maxResults=99)
    issue_type_pattern = re.compile(r"^(작업|문제해결|기능|UI|규격)")
    issues_filtered = [issue for issue in issues if issue_type_pattern.match(issue.fields.issuetype.name)]

    issueList = []
    for issue in issues_filtered:
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


def jira_rest_api(method, uri, data=None):
    auth = HTTPBasicAuth(cred['username'], cred['password'])
    try:
        if data:
            response = requests.request(method, uri, auth=auth, json=data)
        else:
            response = requests.request(method, uri, auth=auth)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"{e}\n{method} Error:{uri}")
    return response.json()

def getIssuesByJql(jql):
    jqlUrlEncode = requests.utils.quote(jql)
    issues = jira_rest_api("GET", f"https://jltechrnd.atlassian.net/rest/api/3/search?jql={jqlUrlEncode}&per_page=100")['issues']
    return issues

def get_filter(state, component):
    jql = f"project ='{adev.jl_project().key}' AND issueType not in (Epic) AND status in ({state})"
    if component == 'on':
        jql += f" AND component = '{adev.jl_component()}'"
    return jql

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

def main():
    global forkedOnlyCmd

    forkedOnlyCmd = False

    parser = argparse.ArgumentParser(description="show project status")
    parser.add_argument('-s','--status',default="last", help="status[todo|doing|done|all|last](default: last)")
    parser.add_argument('-u','--user', default=adev.get_user_info('name_eng'),help=f"user(default: %(default)s)")
    parser.add_argument('-c','--component', default='off',help=f"component only[on|off](default: off)")
    args = parser.parse_args()

    init()
    check_folder()
    adev.jl_init()
    adev.gl_init()
    display_project_info()
    jql=get_filter("'In Progress','To Do'", args.component)
    issueList = jiraIssues(jql)
    # if args.status == 'done':
    #     issueList = jiraIssues(get_filter("'Done'", args.component))
    # elif args.status == 'todo':
    #     jiraIssues(issueList, get_filter("'To Do'", args.component))
    # elif args.status == 'last':
    #     jiraIssues(issueList, filter_last(args.component))
    # elif args.status == 'doing':
    #     jiraIssues(issueList, get_filter("'In Progress'", args.component))
    # else:

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

    # 테이블 형식으로 출력
    print(tabulate(tableData, headers='keys', tablefmt='simple', showindex=False, numalign='left', stralign='left'))

if __name__ == "__main__":
    main()