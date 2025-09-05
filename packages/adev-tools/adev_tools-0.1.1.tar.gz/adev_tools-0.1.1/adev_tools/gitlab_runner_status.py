import os
import requests
from datetime import datetime
from pytz import timezone
from colorama import Fore, Back, Style, init
from tabulate import tabulate

# Initialize colorama for cross-platform colored text
init(autoreset=True)

def gitlab_rest_api(method, uri, data=None):
    headers = {"PRIVATE-TOKEN": os.environ.get("GITLAB", "")}
    try:
        response = requests.request(
            method=method,
            url=uri,
            headers=headers,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"{e}\n{method} Error: {uri}") from e

# Get runners and display status table
runners = gitlab_rest_api("GET", "https://gitlab.com/api/v4/runners")

# Prepare table data with color coding
table_data = []
for runner in runners:
    if runner.get('status') == 'offline':
        description = f"{Back.RED}{runner.get('description', '')}{Style.RESET_ALL}"
    else:
        description = runner.get('description', '')
    
    table_data.append([
        runner.get('id'),
        description,
        runner.get('active'),
        runner.get('paused'),
        runner.get('status')
    ])

# Print formatted table
headers = ["ID", "Description", "Active", "Paused", "Status"]
print(tabulate(table_data, headers=headers, tablefmt="simple", stralign="left"))

# Check for failed jobs
kst = timezone('Asia/Seoul')
for runner in runners:
    jobs = gitlab_rest_api("GET", 
        f"https://gitlab.com/api/v4/runners/{runner['id']}/jobs?order_by=id")
    
    if jobs and jobs[0].get('status') == 'failed':
        job = jobs[0]
        created_at = datetime.fromisoformat(job['created_at'].replace('Z', '+00:00'))
        kst_time = created_at.astimezone(kst)

        print(f"\n{Fore.GREEN}======= {runner['description']}[{job['name']}] 작업 정보 =========")
        print(f"상   태 : {job['status']}")
        print(f"화   면 : {Fore.BLUE}{job['web_url']}")
        print(f"시   작 : {kst_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"경   과 : {job.get('duration', 'N/A')}(초)")
        print(f"요 청 자 : {job['commit']['author_name']}")
        print(f"Commit  : {Fore.BLUE}{job['commit']['web_url']}")
        print(f"내    용 : {job['commit']['message']}")
        print(f"================================================={Style.RESET_ALL}")