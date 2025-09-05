import os
import argparse
import git
import re
import sys
from git import Repo
from . import adev_lib as adev

def create_issue(args):
    issue_dict = {
        'project': {'key': adev.jl_project().key},
        'summary': args.branch,
        'description': '',
        'issuetype': {'name': args.type},  # Change to 'Bug', 'Story', etc.
        'components': [{'name': adev.jl_component().name}]
    }
    if args.parent:
        issue_dict['parent'] = {'key': args.parent}
        # Create Issue
    new_issue = adev.jl_client().create_issue(fields=issue_dict)
    return new_issue

def main():
    parser = argparse.ArgumentParser(description="create jira issue & link commit message")
    parser.add_argument("branch",nargs='?',default='_select', type=str, help="branch name %(default)s")
    parser.add_argument('-t','--type', default='task',help='IssueType [task|problem] (default: %(default)s)')

    issue_types = ['task','problem']
    issue_types_for_jira = ['Task','문제해결']
    args = parser.parse_args()

    adev.adev_init()

    if args.branch == '_select':
        jql=f"project ='{adev.jl_project().key}' AND issueType in ('문제해결','Task') AND component = '{adev.jl_component()}' AND updated >= -14  order by updated desc"
        issue_key = adev.get_issue_from_list(jql,"branch 생성 이슈 선택해주세요:")
        if issue_key == None:
            sys.exit(0)

        issue = adev.jl_client().issue(issue_key)
        if (issue.fields.issuetype.name == '문제해결'):
            args.type = 'problem'
        else:
            args.type = 'task'
        args.branch = issue.fields.summary
    else: # 이슈를 생성함
        args.type = issue_types_for_jira[issue_types.index(args.type)]
        jql=f"project ='{adev.jl_project().key}' AND issueType in (Epic) AND updated >= -14  order by updated desc"
        issue_key = adev.get_issue_from_list(jql,"상위이슈를 선택해주세요:")
        if issue_key:
            args.parent = issue_key

        issue = create_issue(args)
        args.branch = issue.summary


    repo = Repo('.')  # Path to Git repository
    current_branch_name = repo.active_branch.name
    if current_branch_name != 'develop':
        repo.git.checkout('develop')
        print("develop 브랜치로 이동합니다.")

    branch_name= f"{issue.key}_"+args.branch.replace(' ','_')

    if branch_name in repo.heads:
        print(f"오류: '{branch_name}' 브랜치가 이미 존재합니다.")
    else:
        repo.create_head(branch_name)

    repo.git.checkout(branch_name)
    print(f"https://jltechrnd.atlassian.net/browse/{issue.key}")

if __name__ == "__main__":
    main()