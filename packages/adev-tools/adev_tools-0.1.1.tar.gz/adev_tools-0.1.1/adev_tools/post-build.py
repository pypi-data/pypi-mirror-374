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

from os import mkdir, path, symlink, walk,environ,getcwd,listdir,remove,chdir
import xml.etree.ElementTree as ET
import re
import time
import fileinput
import shutil
import subprocess
import fnmatch
import argparse
import git

def install_package(package_name):
    try:
        subprocess.check_call(["pip", "install", package_name])
        print(f"{package_name} installed successfully!")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}.")

def copy_exe_google_drive():
   google_folder =environ.get('GDRIVE', 'G:')+f"/공유 드라이브/연구소/software"
   if path.exists(google_folder):
      software_folder =f"{google_folder}/{project_name}"
      if not path.exists(software_folder):
           mkdir(software_folder)

      check_file_filter = f'*{sha}.exe'
      destination_file = f'{software_folder}/{project_name}_{compiled_local_time}_{sha}.exe'
      same_sha_exe_files = [f for f in listdir(software_folder) if fnmatch.fnmatch(f, check_file_filter)]
      print(same_sha_exe_files)
   #delete same sha exe files
      for same_sha_exe_file in same_sha_exe_files:
          same_sha_exe_file_path = f'{software_folder}/{same_sha_exe_file}'
          print(f'delete {same_sha_exe_file_path}')
          remove(same_sha_exe_file_path)

      shutil.copy(source_exe_file, destination_file)
      print(f'copy {destination_file}')

def copy_exe_local_folder():
   exe_folder = f"exe_folder"
   if  not path.exists(exe_folder):
        mkdir(exe_folder)

   for file_name in listdir(exe_folder):
        file_path = path.join(exe_folder, file_name)
        if path.isfile(file_path):
            remove(file_path)
            print(f"Removed {file_path}")

   destination_file = f'{exe_folder}/{project_name}_{compiled_local_time}_{sha}.exe'
   shutil.copy(source_exe_file,destination_file)

if __name__ == "__main__":
    install_package("gitpython")
    print("Program has been built!")

    compiled_epoch_time = int(time.time())
    compiled_epoch_time_hex = hex(compiled_epoch_time).replace('0x','')
    compiled_local_time = time.strftime('%y%m%d-%H%M', time.localtime())

    if ( path.basename(getcwd()).lower().endswith(("debug", "release")) ):
       source_exe_folder = getcwd()
       chdir("../../..")
       source_exe_file = f'{source_exe_folder}/{path.basename(getcwd())}.exe'
    elif ( path.basename(getcwd()).endswith("build")):
       source_exe_folder = getcwd()
       chdir("..")
       source_exe_file = f'{source_exe_folder}/{path.basename(getcwd())}.exe'
    else:
       source_exe_file = f'build/windows/Release/{path.basename(getcwd())}.exe'

    repo = git.Repo(".")
    project_name = path.basename(getcwd()).split('_')[0]
    print("project name", project_name)
    

    sha = repo.head.commit.hexsha[0:8]
    print("Current local time:", compiled_local_time)
    print("Current epoch time:", compiled_epoch_time_hex)
    print("sha:", sha)

    if (not repo.is_dirty()): 
        copy_exe_google_drive()
        copy_exe_local_folder()
    else:
        print("Program is dirty, skipping copy")




