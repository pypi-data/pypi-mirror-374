import sys
import adev_lib as adev

# Global variables
users = "(dskim|romeo|jhk|mckim|jsjung|jmyu|jsjsung|mhkim|welltech|zestech|joitim423|agjagjn)"
JOB = None

def main():
    adev.env_setup()
    if len(sys.argv) < 2:
        print("검색할 단어를 입력해주세요", file=sys.stderr)
        sys.exit(1)
    arg1 = sys.argv[1]
    if len(arg1) < 3:
        print("3글자 이상을 입력해주세요", file=sys.stderr)
        sys.exit(1)
    arg2 = sys.argv[2] if len(sys.argv) > 2 else None

    gitlab_group = "jltech_lab"
    project_list = []
    adev.get_main_projects(project_list, gitlab_group, arg1, arg2)

    selected_project = adev.list_select("Project", "Project를 선택해주세요 (취소: Enter):",project_list, [p["path_with_namespace"] for p in project_list])
    if selected_project:
        adev.clone_project(selected_project)

if __name__ == "__main__":
    main()