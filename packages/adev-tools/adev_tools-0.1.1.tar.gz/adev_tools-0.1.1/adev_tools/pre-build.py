# Author: Joachim Baumann
# Version: 1.0.2
#
# This script is based on the information for advanced scripting provided
# by platformio
# https://docs.platformio.org/en/latest/projectconf/advanced_scripting.html
#
# We try to get all needed information from the .cproject file, collect all
# source directories from that to create the src_filter and read platformio's
# own board definition to glean the cpu type.

from os import mkdir, path, symlink, walk,environ,getcwd,listdir
import xml.etree.ElementTree as ET
import re
import time
import fileinput
import subprocess
import argparse
import git

def create_version_info(root_folder):
    compiled_epoch_time = int(time.time())
    compiled_epoch_time_hex = hex(compiled_epoch_time).replace('0x','')
    compiled_local_time = time.strftime('%y%m%d-%H%M', time.localtime())

    repo = git.Repo(root_folder)

    try:
        if (repo.is_dirty()): 
            sha = "0"
        else:
            sha = repo.head.commit.hexsha[0:8]
    except:
        sha = "0"

    print("Current local time:", compiled_local_time)
    print("Current epoch time:", compiled_epoch_time_hex)
    print("sha:", sha)
# Write the current time to a header file
    with open(f"{root_folder}/src/version_info.h", "w") as file:
        file.write(f'#define COMPILED_EPOCH_TIME {compiled_epoch_time}\n')
        file.write(f'#define COMPILED_EPOCH_TIME_HEX "{compiled_epoch_time_hex}"\n')
        file.write(f'#define COMPILED_LOCAL_TIME "{compiled_local_time}"\n')
        file.write(f'#define COMMIT_SHA 0x{sha}\n')

# Get the current time and date

def main():
    if ( path.basename(getcwd()).lower().endswith(("debug", "release")) ):
        root_folder = "../../.."
    elif path.basename(getcwd()).endswith("build"):
        root_folder = ".."
    else:
        root_folder = "."
    create_version_info(root_folder)

if __name__ == "__main__":
    main()
