import os
import argparse
import git
import re
import sys
from git import Repo
from . import adev_lib as adev
from openai import OpenAI
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_commit_message_with_openai():
    """Generates a commit message in Korean using the OpenAI API."""
    staged_diff = adev.get_staged_changes()

    if not staged_diff:
        print("Error: No staged changes found.")
        return None

    api_key, model = adev.get_openai_config()
    client = OpenAI(api_key=api_key)

    # Construct the prompt with the diff
    prompt = f"""
        Generate a concise and descriptive git commit message based on the following diff in korean:
        Diff:
        ```diff
        {staged_diff}
        ```
        Commit message:
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert software developer that writes great git commit messages."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,  # Lower temperature for more deterministic output
            max_tokens=60    # Adjust based on how long you expect the commit message to be
        )
        # Extract the commit message from the response
        if response and response.choices:
            commit_message = response.choices[0].message.content.strip()
            if commit_message.startswith("```") and commit_message.endswith("```"):
                commit_message = commit_message[3:-3].strip()  # "```" 제거
            return commit_message
        else:
            logging.error(f"failed to generate commit message")
            return None

    except Exception as e:
        logging.error(f"Error generating commit message: {e}")
        return None

def review_changed_code_with_ollama():
    diff = adev.get_staged_changes()
    if not diff:
        print("Error: No staged changes found.")
        return None
    prompt = f"""
    Please review the following changes and suggest new code in korean:\n```diff\n{diff}\n```
    """
    model = adev.config().get('environment', {}).get('ollama', {}).get('commit_message_model', '')
    print(f"Review staged changes with Ollama model(model:{model})")
    message = adev.get_ollama_response(model,prompt)
    return message

def review_changed_code_with_openai():

    diff = adev.get_staged_changes()

    if not diff:
        print("Error: No staged changes found.")
        return None

    prompt = f"""
    You are a senior programming expert Bot, responsible for reviewing code changes and providing review recommendations. At the beginning of the suggestion, it is necessary to clearly make a decision to "reject" or "accept" the code change, and rate the change in the format "Change Score: Actual Score", with a score range of 0-100 points. Then, point out the existing problems in concise language and a stern tone. If you feel it is necessary, you can directly provide the modified content. Your review proposal must use rigorous Markdown format in korean
    Diff:
    ```diff
    {diff}
    ```
    Please review the code changes and suggest new code in this section in korean:
    """

    # OpenAI 클라이언트 초기화
    api_key,model = adev.get_openai_config()
    print(f"Review staged changes with openai model(model:{model})")
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a senior programming expert Bot, responsible for reviewing code changes and providing review recommendations."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f"Error: {e}")
        return None

def create_issue_link_amend(type,commit_message,parent_issue_key):
    # Issue Details
    summary = commit_message.split('\n')[0]
    #other lines to description
    description = '\n'.join(commit_message.split('\n')[1:])
    issue_dict = {
        'project': {'key': adev.jl_project().key},
        'summary': summary,
        'description': description,
        'issuetype': {'name': type},  # Change to 'Bug', 'Story', etc.
        'components': [{'name': adev.jl_component().name}],
        'parent' : {'key': parent_issue_key}
    }
    # 이슈 생성
    new_issue = adev.jl_client().create_issue(fields=issue_dict)
    # 상위 이슈가 제공되지 않은 경우 관련 이슈 선택
    if  parent_issue_key == None:
        jql=f"project ='{adev.jl_project().key}' AND issueType not in (Epic) AND updated >= -14  order by updated desc"
        related_issue_key = adev.get_issue_from_list(jql,"관련 이슈를 선택해주세요:")
        if related_issue_key:
            # 이슈 연결
            adev.jl_client().create_issue_link(
            type="Relates",
            inwardIssue=new_issue.key,
            outwardIssue=related_issue_key
            )
            parent_issue_key = related_issue_key

    if(args.type == 'Hotfix'):
        commit_type = 'fix'
    else:
        commit_type = None

    if (commit_type):
        repo.git.commit('-m',f"{commit_type}({parent_issue_key or ''}:{new_issue.key}): {commit_message}")
    else:
        repo.git.commit('-m',f"({parent_issue_key or ''}:{new_issue.key}): {commit_message}")

    # 원격 저장소에 변경 사항 푸시
    print(f"https://jltechrnd.atlassian.net/browse/{new_issue.key}")

def generate_commit_message():  
    diff = adev.get_staged_changes()
    if diff:
        commit_message_en = adev.generate_commit_message_ollama_en(diff)
        if commit_message_en:
            commit_message_ko = adev.generate_commit_message_ollama_ko(commit_message_en)
            if commit_message_ko:
                return commit_message_ko + "\n" + commit_message_en
    return None

def log_review_result(message):
    if message is None:
        print("-"*100)
        print("메시지가 없습니다. 프로그램을 종료합니다.")
        print("-"*100)
        sys.exit(0)

    print("-"*100)
    print(message)
    print("-"*100)

    while True:
        response = input("계속 진행하시겠습니까? (Y/n): ").lower()
        if response == '' or response == 'y':  # Enter 키나 'y' 입력 시 계속 진행
            break
        elif response == 'n':
            print("프로그램을 종료합니다.")
            sys.exit(0)
        print("잘못된 입력입니다. Enter 또는 y/n을 입력해주세요.")


def handle_commit_message_generation_error():
    print("커밋 메시지 생성에 실패했습니다.")
    sys.exit(1)  # 비정상 종료 코드

def main():
    repo = Repo('.')  # Path to Git repository
    current_branch_name = repo.active_branch.name  # 현재 브랜치 이름
    repo.git.add(".")
    if current_branch_name == 'main':
        print("main 브랜치에서는 이 작업을 할 수 없습니다. 다른 브랜치에서 작업해주세요.")
        sys.exit(0)

    parser = argparse.ArgumentParser(description="JIRA 이슈를 생성하고 커밋 메시지를 연결합니다.")
    issue_types = ['subtask', 'hotfix','amend'] if current_branch_name == 'develop' else ['subtask','amend']
    issue_types_display = ['subtask(Sub-task):하위이슈', 'hotfix(Hotfix):하위이슈','amend(Amend):수정'] if current_branch_name == 'develop' else ['subtask(Sub-task):하위이슈','amend(Amend):수정']

    
    parser.add_argument("type",nargs='?',default='_select',type=str, help="type (default: %(default)s), options: " + ", ".join(issue_types))
    parser.add_argument("-m",'--message',default=None,type=str, help="message (default: %(default)s)")
    parser.add_argument("-a",'--ai-agent',default="ollama",type=str, help="ai agency(ollama,openai) (default: %(default)s)")
    args = parser.parse_args()

    # Jira 및 GitLab 초기화를 통합하는 함수를 호출하여,
    # 다양한 초기화 함수들을 단일 관리할 수 있도록 합니다.
    adev.adev_init()  # 초기화 과정 실행

    try:
        message = review_changed_code_with_openai()
        log_review_result(message)
    except Exception as e:
        logging.error(f"코드 리뷰 중 오류 발생: {e}. 구체적인 오류를 확인하세요.")
        sys.exit(1)


    # 커밋 메시지 생성 로직
    if args.ai_agent == "ollama":
        commit_message = adev.create_commit_message_with_ollama()
    else:
        commit_message = create_commit_message_with_openai()

     # 사용자가 메시지를 제공한 경우, 자동 생성된 메시지와 결합
    if args.message:
        commit_message = args.message + "\n" + commit_message

    if commit_message is None:
        handle_commit_message_generation_error()


    print("-"*100)
    print(commit_message)
    print("-"*100)

    if args.type == "_select" or args.type not in issue_types:
        args.type = adev.list_select('issue_types','선택',issue_types,issue_types_display)

    if args.type == None:
        sys.exit(0)

    if args.type == 'amend':
        old_message = repo.head.commit.message.strip()
        commit_message = f"{old_message}\n\n{commit_message}"
        repo.git.commit('--amend', '-m',f"{commit_message}")
        print("-"*100)
        print(commit_message)
        print("-"*100)
        sys.exit(0)

    if current_branch_name == 'develop':
        issue_types_for_jira = ['Sub-task','Hotfix']
    else:
        issue_types_for_jira = ['Sub-task']

    args.type = issue_types_for_jira[issue_types.index(args.type)]
    pattern = r'^(.*-\d+)_'
    match = re.match(pattern, current_branch_name)
    if match:
        parent_issue_key = match.group(1)
    else:
        jql=f"project ='{adev.jl_project().key}' AND issueType in ('Task','문제해결') AND component = '{adev.jl_component()}' order by updated desc"

        parent_issue_key = adev.get_issue_from_list(jql,"상위이슈를 선택해주세요:")
    
    if current_branch_name != 'develop' or parent_issue_key:
        create_issue_link_amend(args.type,commit_message,parent_issue_key)
    else:
        print("상위이슈가 없습니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()

