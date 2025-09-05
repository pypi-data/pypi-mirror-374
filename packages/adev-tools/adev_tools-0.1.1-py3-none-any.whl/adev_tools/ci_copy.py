import argparse
from . import ci_lib as ci

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="gitlab runner copy file")
    parser.add_argument("runner", type=str, help="runner name if list show all runners")
    parser.add_argument('-s','--src_dir',default='exe_folder',help='source file path(default: exe_folder)')
    parser.add_argument('-t','--target',help='target file path(folder or file)')
    args = parser.parse_args()

    ci.check_runner_status(args.runner)

    if args.target:
        print(f'copy [{args.target}] using the runner [{args.runner}]');

        if (args.src_dir == 'exe_folder'):
            extension = 'exe'
        elif (args.src_dir == 'firmware'):
            extension = 'bin'
        else:
            import os
            if os.path.isfile(args.src_dir):
                extension = 'file'
            elif os.path.isdir(args.src_dir):
                extension = 'folder'
            else:
                print(f"{args.src_dir} 경로가 존재하지 않습니다.")
                exit()

        site=ci.upload_file(args.src_dir,extension,f'COPY|{args.runner}|{args.target}')
        ci.runner_command({
            'RUNNER_NAME': f'{args.runner}',
            'RUNNER_COMMAND': 'copy',
            'TARGET_PATH': f'{args.target}',
            'SOURCE_DIR': f'{args.src_dir}'
        },site)
    else:
        print("No target path provided")
        exit()