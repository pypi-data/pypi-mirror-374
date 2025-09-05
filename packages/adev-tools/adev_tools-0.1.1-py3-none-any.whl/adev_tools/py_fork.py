import os
import sys
import json
import requests
import argparse
import time
from datetime import datetime
from urllib.parse import quote
from pytz import timezone
from . import adev_lib as adev
import stat

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Global variables
GITLAB_TOKEN = adev.get_gitlab_info('token')
KST = timezone('Asia/Seoul')


def get_gitlab_project(path_with_namespace):
    proj_path = quote(path_with_namespace, safe='')
    url = f"https://gitlab.com/api/v4/projects/{proj_path}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{proj_path} path does not exist.")
        return None

def check_can_fork(project):
    only_not_same = False
    commit_list = []
    url_branch_name = quote("main")  # Assuming main branch
    commits = adev.gitlab_rest_api("GET", f"https://gitlab.com/api/v4/projects/{project['id']}/repository/commits?ref_name={url_branch_name}")
    for commit in commits:
        if not commit["message"].startswith("Merge branch"):
            break

    if commit:
        utc = commit["committed_date"]
        time_string = datetime.fromisoformat(utc).astimezone(KST).strftime('%Y-%m-%d %H:%M:%S')
        author = commit["committer_name"]
        url = commit["web_url"]
        title = commit["message"]
        if not project.get("forked_from_project", {}).get("id") or only_not_same:
            forked_by = "Upstream"
            commit_list.append({"Utc": utc, "Link": project["web_url"], "Remote": "upstream", "Time": time_string, "Author": author, "url": url, "Message": title, "ForkedBy": forked_by})
        else:
            forked_by = "Me"
            commit_list.append({"Utc": utc, "Link": project["web_url"], "Remote": "origin", "Time": time_string, "Author": author, "url": url, "Message": title, "ForkedBy": forked_by})

    if "fork" in commit["web_url"]:
        if project.get("forked_from_project", {}).get("id"):
            commits = adev.gitlab_rest_api("GET", f"https://gitlab.com/api/v4/projects/{project['forked_from_project']['id']}/repository/commits")
            for commit in commits:
                if not commit["message"].startswith("Merge branch"):
                    break
            utc = commit["committed_date"]
            time_string = datetime.fromisoformat(utc).astimezone(KST).strftime('%Y-%m-%d %H:%M:%S')
            author = commit["committer_name"]
            forked_by = "Upstream"
            url = commit["web_url"]
            title = commit["message"]
            commit_list.append({"Utc": utc, "Link": project["forked_from_project"]["web_url"], "Remote": "upstream", "Time": time_string, "Author": author, "url": url, "Message": title, "ForkedBy": forked_by})

        if commit_list[0]["Utc"] > commit_list[1]["Utc"]:
            can_fork = False
        else:
            can_fork = True
    return can_fork

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def fork_to_namespace(upstream, target_namespace, user):
    if "_altium" in upstream["path"].lower():
        clone_folder = f"{adev.get_artwork_folder()}/_fork/{user}"
    else:
        clone_folder = f"{adev.get_dev_folder()}/_fork/{user}"

    current_folder = os.getcwd()
    os.chdir(clone_folder)
    try:
        fork_project = get_gitlab_project(f"{target_namespace}/{upstream['path']}")
    except Exception as e:
        fork_project = None

    if fork_project and fork_project.get("id"):
        print(fork_project["web_url"])
        if not check_can_fork(fork_project):
            print("Forked project is ahead of upstream.")
            print("Please check and try again.")
            sys.exit(0)

        if  adev.confirm("Confirm", "Fork project exists. Delete it?"):
            print(f"******* Deleting forked project {upstream['path_with_namespace']} *******")
            adev.gitlab_rest_api("DELETE", f"https://gitlab.com/api/v4/projects/{fork_project['id']}")
            print("Fork repository deleted successfully.")
            fork_project = None
        else:
            sys.exit(0)


        fork_prj_folder = f"{clone_folder}/{upstream['path']}"
        if os.path.exists(fork_prj_folder):
            if upstream["path"] in current_folder:
                print(f"******* Moving to {clone_folder} *******")
                os.chdir(clone_folder)
            import shutil
            try:
                print(f"******* Removing {fork_prj_folder} *******")
                shutil.rmtree(fork_prj_folder,onerror=remove_readonly)
                print(f"{fork_prj_folder} folder deleted successfully.")
            except Exception as e:
                print(f"Error deleting folder: {e}")
                sys.exit(1)
        time.sleep(10)

    if not fork_project or not fork_project.get("id"):
        fork_list = adev.gitlab_rest_api("GET", f"https://gitlab.com/api/v4/projects/{upstream['id']}/forks")
        for forked in fork_list:
            if user in forked["path_with_namespace"] and forked["name"] == upstream["name"]:
                print(forked["web_url"])
                if adev.confirm("Confirm", "Repository with the same name exists. Delete it?"):
                    adev.gitlab_rest_api("DELETE", f"https://gitlab.com/api/v4/projects/{forked['id']}")
                    print("Deleting...")
                    time.sleep(5)
                else:
                    print("Please check and try again.")
                    sys.exit(0)

        print(f"******* Forking to {target_namespace} *******")
        post_data = {"namespace": target_namespace}
        try:
            fork_project = adev.gitlab_rest_api("POST", f"https://gitlab.com/api/v4/projects/{upstream['id']}/fork", post_data)
            time.sleep(10)
        except Exception as e:
            print("Forking failed.")
            sys.exit(0)

    if not fork_project or not fork_project.get("id"):
        print("Forking failed. Please contact the administrator.")
        sys.exit(0)
    else:
        print(f"******* Forked project {fork_project["web_url"]} *******")
        return fork_project

def main():
    parser = argparse.ArgumentParser(description="fork repository")
    parser.add_argument("search", type=str, help="search key for upstream repository find")
    parser.add_argument('-u','--user', default=adev.get_user_info('name_eng'),help='user(default: %(default)s)')
    args = parser.parse_args()

    if len(args.search) < 3:
        print("Please enter at least 3 characters for search key")
        sys.exit(0)

    upstream_list = []
    if args.user in ["welltech", "zestech"]:
        adev.get_main_projects(upstream_list, "jltech_lab/jl_artwork", args.search)
        # adev.get_main_projects(upstream_list, "jltech_lab/jl_artwork", args.search)
    else:
        adev.get_main_projects(upstream_list, "jltech_lab", args.search)

    selected_project = adev.list_select("Project", "Select a project:",upstream_list ,[proj["path_with_namespace"] for proj in upstream_list])
    if not selected_project:
        sys.exit(0)

    if "_altium" in selected_project["path"].lower():
        gitlab_group = "jltech_lab/jl_artwork"
    else:
        gitlab_group = "jltech_lab"

    fork_project = fork_to_namespace(selected_project, f"{gitlab_group}/fork/{args.user}", args.user)
    if args.user in ["welltech", "zestech"]:
         adev.send_slack_message("fork", "", fork_project)

    if args.user in ["welltech", "zestech"]:
        if adev.confirm("Confirm", "Clone the forked repository?", False):
            adev.clone_project(fork_project, args.user)
    else:
        if adev.confirm("Confirm", "Clone the forked repository?", True):
            adev.clone_project(fork_project, args.user)

if __name__ == "__main__":
    main()