import os
import sys
import argparse
import adev_lib as adev


if __name__ == "__main__":

    config = adev.config()

    parser = argparse.ArgumentParser(description="프로젝트 폴더 가기")
    parser.add_argument("search", type=str, help="search key for project finding")
    parser.add_argument('-u','--user', default=adev.get_user_info('name_eng'),help='user name(default: %(default)s)')
    args = parser.parse_args()

    search_projects = []

    for folder in [adev.get_dev_folder() + "/upstream", adev.get_artwork_folder() + "/upstream", adev.get_dev_folder() + "/_fork/" + args.user]:
        if folder and os.path.exists(folder):
            for dir in os.listdir(folder):
                if os.path.isdir(os.path.join(folder, dir)) and args.search.lower() in dir.lower():
                    search_projects.append(os.path.join(folder, dir))

    if not search_projects:
        print("No projects found.", file=sys.stderr)
        sys.exit(0)

    project_path = adev.list_select("프로젝트 검색 결과", "프로젝트 번호를 선택하세요 (취소: Enter):", search_projects)
    if not project_path:
        sys.exit(0)

    # 선택된 경로를 chdir.txt 파일에 저장
    with open(os.path.expanduser('~/.chdir.txt'), 'w') as f:
        f.write(project_path)
    sys.exit(0)


