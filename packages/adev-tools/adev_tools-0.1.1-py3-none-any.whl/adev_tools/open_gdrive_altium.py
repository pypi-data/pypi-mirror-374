import os
import argparse
import shutil
import subprocess
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tabulate import tabulate
import pickle
import adev_lib as adev

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    import logging
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    creds = None
    CREDENTIALS_FILE = f'{adev.get_dev_folder()}/credentials.json'
    TOKEN_FILE = f'{adev.get_dev_folder()}/token.pickle'

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def add_files(service, folder_id, search,version):
    query = f"'{folder_id}' in parents and "
    query += f"name contains '{search}' and "
    query += "mimeType='application/pdf' and trashed=false"
    print(query)

    results = service.files().list(
        q=query,
        pageSize=20,
        fields="nextPageToken, files(id, name)",
        orderBy="modifiedTime desc"
    ).execute()

    #files filter by version
    if version:
        results['files'] = [file for file in results['files'] if f'v{version}' in file['name']]

    return results.get('files', [])

def main():
    parser = argparse.ArgumentParser(description="search & open schematic file")
    parser.add_argument("search", type=str, help="search key for schematic file")
    parser.add_argument("-v","--version",default=None, type=str, help="version (x.x.x)")
    args = parser.parse_args()

    # Configuration
    ARTWORK_FOLDER_ID = '1PsQSY7rXQEdDtMhpF7kYWhYF3c3RndS2'

    # Get Google Drive service
    service = get_drive_service()
    
    # Search for files
    files = add_files(service, ARTWORK_FOLDER_ID, args.search,args.version)
    if not files:
        print("\033[31m검색된 프로젝트가 없습니다\033[0m")  # Red text
        return
    
    # Handle file selection
    if len(files) == 1:
        selected = files[0]
    else:
        selected = adev.list_select('Project', 'Project를 선택해주세요:', files,[file["name"] for file in files])
        if not selected:
            return
    
    # Open in Chrome
    url = f'https://drive.google.com/file/d/{selected["id"]}'
    adev.open_chrome(url)

if __name__ == '__main__':
    main()