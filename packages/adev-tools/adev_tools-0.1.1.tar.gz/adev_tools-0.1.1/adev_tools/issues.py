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
from . import adev_lib as adev
import gitlab 
from urllib.parse import quote
from tabulate import tabulate
import wcwidth
import pandas as pd

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
    global current_branch_name
    current_branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    print(f"Component:{adev.jl_component()} Platform:{adev.jl_platform()} branch:{current_branch_name}")



def get_filter(state, component):
    jql = f"project ='{adev.jl_project().key}' AND issueType not in (Epic) AND status in ({state})"
    if component == 'on':
        jql += f" AND component = '{adev.jl_component()}'"
    return jql


def main():
    global forkedOnlyCmd

    forkedOnlyCmd = False

    parser = argparse.ArgumentParser(description="show project status")
    parser.add_argument('status',nargs='?',default="last", help="status[todo|doing|done|all|last|epic](default: last)")
    parser.add_argument('-u','--user', default=adev.get_user_info('name_eng'),help=f"user(default: %(default)s)")
    parser.add_argument('-c','--component_only', default='on',help=f"component only[on|off](default: on)")
    parser.add_argument('-q','--query', default=None,help=f"query string(default: None)")
    args = parser.parse_args()

    init()
    check_folder()
    adev.jl_init()
    display_project_info()

    if args.status == 'done':
        jql=get_filter("'Done'", args.component_only)
    elif args.status == 'todo':
        jql=get_filter("'To Do'", args.component_only)
    elif args.status == 'doing':
        jql=get_filter("'In Progress'", args.component_only)
    elif args.status == 'last':
        if args.component_only == 'on':
            jql=f"project ='{adev.jl_project().key}' AND issueType in ('Task','문제해결') AND component = '{adev.jl_component()}' AND updated >= -14  order by updated desc"
        else:
            jql=f"project ='{adev.jl_project().key}' AND issueType in ('Task','문제해결') AND updated >= -14  order by updated desc"
    elif args.status == 'all':
        jql=get_filter("'In Progress','To Do','Done'",args.component_only)
    elif args.status == 'epic':
        jql=f"project ='{adev.jl_project().key}' AND  type = Epic ORDER BY created DESC"
    else:
        print(f"status {args.status} is not supported")
        sys.exit(0)

    print(f"JQL({args.status}):{jql}")

    issue_key = adev.get_issue_from_list(jql)
    if issue_key:
        url = f"https://jltechrnd.atlassian.net/browse/{issue_key}"
        adev.open_chrome(url)

if __name__ == "__main__":
    main()