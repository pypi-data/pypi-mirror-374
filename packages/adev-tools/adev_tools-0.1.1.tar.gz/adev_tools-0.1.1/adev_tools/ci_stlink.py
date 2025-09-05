import argparse
import sys
import ci_lib as ci

def stlink_local(args):
    if args.cmd == 'program':
        bin_file = "firmware/firmware.bin"
        print(f"*** Flashing firmware:{bin_file}")
        # ci.run_command(['STM32_Programmer_CLI.exe', '-c', 'port=SWD',f'SN={stlink_sn}', '-v', '-d', bin_file, offset])
        ci.run_command(['STM32_Programmer_CLI.exe', '-c', 'port=SWD','-v','-d', bin_file, '0x08020000'])
        ci.run_command(['STM32_Programmer_CLI.exe', '-c', 'port=SWD', '-rst'])
    elif args.cmd == 'reset':
        # ci.run_command(['STM32_Programmer_CLI.exe', '-c', 'port=SWD',f'SN={stlink_sn}', '-rst'])
        print(f"*** reset board")
        ci.run_command(['STM32_Programmer_CLI.exe', '-c', 'port=SWD', '-rst'])
    else:
        print("No command provided")
        exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="gitlab runner stlink control")
    parser.add_argument("runner",nargs='?',default='list', type=str, help="local or runner name if list show all runners(default: %(default)s)")
    parser.add_argument('-s','--stlink', nargs='?',default='stlink1',help='stlink number to use (default: %(default)s)')
    parser.add_argument('-c','--cmd', default='reset',help='reset|program(default: %(default)s)')
    args = parser.parse_args()

    if args.runner == 'local':
        stlink_local(args)
        sys.exit(0)
    else:
        ci.check_runner_status(args.runner)

    if args.cmd == 'program':
        print(f'Programming the board [{args.stlink}] using the runner [{args.runner}]');
        site=ci.upload_file("firmware","bin",f'UPLOAD|{args.runner}|{args.stlink}')
        ci.runner_command({
        'RUNNER_NAME': f'{args.runner}',
        'RUNNER_COMMAND': 'program',
        'STLINK_NAME': f'{args.stlink}'
        },site)
    elif args.cmd == 'reset':
        print(f'Reset the board [{args.stlink}] using the runner [{args.runner}]');
        ci.runner_command({
            'RUNNER_NAME': f'{args.runner}',
            'RUNNER_COMMAND': 'reset',
            'STLINK_NAME': f'{args.stlink}'
        })
    else:
        print("No command provided")
        exit()