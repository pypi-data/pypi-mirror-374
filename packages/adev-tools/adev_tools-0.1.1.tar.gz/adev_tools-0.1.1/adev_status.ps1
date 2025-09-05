# . "$($env:SP)/adev_lib.ps1"
function env_setup {
    if ([regex]::matches($PWD, "artwork", "IgnoreCase")) {
        $global:JOB = 'ALTIUM'
    }
    elseif ([regex]::matches($PWD, "dev", "IgnoreCase")) {
        $global:JOB = 'DEV'
    }
    # elseif ([string]::IsNullOrWhiteSpace($global:JOB)) {
    #     $option = Read-Host "Job [A]ltium [D]ev"
    #     Switch ($option) {
    #         A { $chosenJob = "ALTIUM" }
    #         D { $chosenJob = "DEV" }
    #         default { $chosenJob = "DEV" }
    #     }
    #     $global:JOB = $ChosenJob
    # }
    # OrLciePHqHZk0kzq1IyvA84F
    # Define Credentials
}

function init {
    env_setup
}
function check_folder {
    #check current folder & check project name
    [string] $global:remoteOrigin = ""
    If ((Test-Path "./.git") -eq $True) {
        $remoteOrigin = $(git remote -v | Where-Object { $_ -match "origin" } | Where-Object { $_ -match "push" })
        [void]($remoteOrigin -match ':(.*/[^/]*).git')
        [string] $path_with_namespace = $Matches[1]
        if ($remoteOrigin -match 'http') {
            Write-Output "Remote Repository를 ssh로 해주세요"
            exit 0
        }


        #fork 된 프로젝트만 작업이 가능하다. upstream은 그냥 최종 시험용으로 사용한다.
        if (( $($path_with_namespace -match "\/fork\/") -ne 'True' )) {
            if ($global:command -match "$forkedOnlyCmd") {
                Write-Host "fork 된 프로젝트가 아닙니다 " -ForegroundColor red
                exit 0
            }
        }

        if ($path_with_namespace -match "\/([a-z0-9-_]+)$") {
            $path=$matches[1]
        } else {
            Write-Host "repository 이름이 형식에 맞지않습니다." -ForegroundColor red
            exit 0
        }

        if ( $path -match "([a-z0-9]+)-([a-z0-9-_]+)_(\w+)$" ) {
            $global:project_key = $($Matches[1].toUpper())
            $global:component = $($Matches[2].toUpper())
            $global:platform =$($Matches[3].toUpper()) 
        }
        elseif ( $path -match "([a-z0-9]+)-([a-z0-9-]+)$" ) {
            $global:project_key = $($Matches[1].toUpper())
            $global:component = $($Matches[2].toUpper())
        }
        elseif ( $path -match "([a-z0-9]+)_(\w+)$" ) {
            $global:project_key = $($Matches[1].toUpper())
            $global:platform =$($Matches[2].toUpper()) 
            if ($Matches[2] -match 'pio') {
                $global:component = "FW"
            }
            elseif ($Matches[2] -match 'qt') {
                $global:component = "SW"
            }
            elseif ($Matches[2] -match 'altium') {
                $global:component = "HW"
            } else {
                $global:component = "SW"
            }
        }
        elseif ( $path -match "([a-z0-9]+)$" ) {
            $global:project_key = $($Matches[1].toUpper())
        }
        else {
            Write-Host "SP script 지원 Folder가 아닙니다. go 명령어로 프로젝트 폴더로 들어가세요" -ForegroundColor red
            exit 0
        }
    }
    elseif ($(Get-Location).path -match '_jira$') {
        $(Get-Location).path
        if ($(Get-Location).path -match '[\\/](\w+)-([\uAC00-\uD7AFa-zA-Z0-9@_-]+)_jira$') {
            $global:project_key = $($Matches[1].toUpper())
            $global:component = $($Matches[2].toUpper())
            $global:JOB = 'JIRA'
        }
        elseif ($(Get-Location).path -match '(\w+)_jira$') {
            $global:project_key = $($Matches[1].toUpper())
            $global:JOB = 'JIRA'
            $global:component = ""
        }
    }
    else {
        Write-Host "SP script 지원 Folder가 아닙니다. go 명령어로 프로젝트 폴더로 들어가세요" -ForegroundColor red
        exit 0
    }
    if ([string]::IsNullOrWhiteSpace($component)) {
        if ($JOB -eq 'DEV') {
            $global:component = 'SW'
        }
        elseif ($JOB -eq 'ALTIUM') {
            $global:component = 'HW'
        }
        else {
            $global:component = ""
        }
    }
}

function set_project {
    $gitstatus = (Get-GitStatus)
    if ($gitstatus) {
        $remoteOrigin = $(git remote -v | Where-Object { $_ -match "origin" } | Where-Object { $_ -match "push" })
        [void]($remoteOrigin -match ':(.*/[^/]*).git')
        [string] $path_with_namespace = $Matches[1]
        $global:working_repo = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$([uri]::EscapeDataString($path_with_namespace))"
        if ($working_repo.forked_from_project) {
            $remoteUpstream = $(git remote -v | Where-Object { $_ -match "upstream" } | Where-Object { $_ -match "push" })
            if ([string]::IsNullOrWhiteSpace($remoteUpstream)) {
                Invoke-Expression "git remote add upstream $($working_repo.forked_from_project.ssh_url_to_repo)"
            }
        } 
    }

    if ($global:JOB -eq "ALTIUM") {
        if ( -not $($working_repo.path -match '_altium$')) {
            Write-Output "Altium Project 가 아닙니다."
            exit 0
        }
    }
    $global:workingProject = Get-JiraProject -Project "$project_key" -Credential $cred
    if ([string]::IsNullOrWhiteSpace($workingProject.id)) {
        Write-Host "$project_key Jira Project가 존재 하지 않습니다." -ForegroundColor red
        exit 0
    }
}

function gitlab_rest_api {
    param(
        $method, $uri, $data
    )
    try {
        if ($data) {
            $result = (Invoke-WebRequest -Method $method -Headers @{"PRIVATE-TOKEN" = "$($env:GITLAB)" } -uri "$uri" -ContentType 'application/json;charset=utf-8' -Body $data)
        }
        else {
            $result = (Invoke-WebRequest -Method $method -Headers @{"PRIVATE-TOKEN" = "$($env:GITLAB)" } -uri "$uri" -ContentType 'application/json;charset=utf-8')
        }
    }
    catch {
        throw "$_`n$method Error:$uri"
    }
    return ($result.content | ConvertFrom-Json);
}
function set_user_info { 
    if ([string]::IsNullOrWhiteSpace($working_repo.forked_from_project.id)) {
        $global:user_permission = 'Devloper'
        $userList = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($working_repo.id)/members/all" 
        foreach ($user in $userList) {
            if ($user.name -eq "$env:USER_NAME") {
                $global:user_level = $user.access_level
                $global:gitlab_user_id = $user.id
            }
        }
        if ($user_level -eq 50) {
            $global:user_permission = 'Owner'
        }
        elseif ($user_level -eq 40) {
            $global:user_permission = 'Maintainer'
        }
        elseif ($user_level -eq 30) {
            $global:user_permission = 'Devloper'
        }
        elseif ($user_level -eq 20) {
            $global:user_permission = 'Repoter'
        }
        # exit 0
    }
    else {
        $userList = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($working_repo.forked_from_project.id)/members/all" 
        foreach ($user in $userList) {
            if ($user.name -eq "$env:USER_NAME") {
                $global:user_level = $user.access_level
                $global:gitlab_user_id = $user.id
            }
        }
        if ($user_level -eq 50) {
            $global:user_permission = 'Owner'
        }
        elseif ($user_level -eq 40) {
            $global:user_permission = 'Maintainer'
        }
        elseif ($user_level -eq 30) {
            $global:user_permission = 'Devloper'
        }
        elseif ($user_level -eq 20) {
            $global:user_permission = 'Repoter'
        }
    }
}

function checkCurrentFolder {
    check_folder
    set_project
    if ([string]::IsNullOrEmpty($global:component)) {
    } else {
        #check component exist if not exist create
        $componets = $(Get-JiraComponent $global:workingProject -Credential $cred)
        if (-not ($componets -match "$global:component")) {
            Write-Host "$component 컴포넌트를 생성해주세요" -ForegroundColor red
            Write-Host "https://jltechrnd.atlassian.net/browse/$($project_key)"
            # $post_data = @{
            #     "name"= "$component"
            #     "project"= "$project_key"
            # }
            #   'isAssigneeTypeValid'="false"
            #   'name'= "$global:component"
            #   'description'= ""
            #   'project'= "$($global:workingProject.key)"
            #   'assigneeType'= "PROJECT_LEAD"
            #   'leadAccountId'= "$env:JIRA_USERID"
            # $body = ($post_data | ConvertTo-Json | Out-String)
            # jira_rest_api POST "https://your-domain.atlassian.net/rest/api/3/component" $body
            exit 0
        }
    }
    $versions = $(Get-JiraVersion $project_key -Credential $cred) | Where-Object { $_.Name -match "$global:component" -and -not [string]::IsNullOrEmpty($_.StartDate) -and [string]::IsNullOrEmpty($_.ReleaseDate) }
    if ($versions.count -eq 0) {
        Write-Host "버전 정보가 없습니다. version 명령으로 버젼을 설정해주세요" -ForegroundColor red
    } elseif ($versions.count -eq 1) {
        $global:current_version = $versions[0].Name;
    } else {
        Write-Host "다수의 Open된 버전이 존재합니다." -ForegroundColor red
    }
    if ($JOB -ne 'JIRA') {
        set_user_info
        $global:current_branch_name = $(git rev-parse --abbrev-ref HEAD)
        Write-Host "$version 컴포넌트:$($global:component) 현재버젼:$current_version 권한:$global:user_permission branch:$current_branch_name" -ForegroundColor green
    }
    else {
        Write-Host "$version 컴포넌트:$($global:component) 현재버젼:$current_version " -ForegroundColor green
    }
}
function parseOptions {
    param(
        $argv, $options
    )
    $opts = @()
    if (!$argv) { return $null }
    foreach ($arg in $argv) {
        # Make sure the argument is something you are expecting
        $test = ($arg -is [int]) -or 
                    ($arg -is [string]) -or
                    ($arg -is [float])
        if (!$test) {
            Write-Host "Bad argument: $arg is not an integer, float, nor string." -ForegroundColor Red
            throw "Error: Bad Argument"
        }
        if ($arg -like '-*') { $opts += $arg }
    }
    $argv = [Collections.ArrayList]$argv
    if ($opts) { 
        foreach ($opt in $opts) { 
            switch ($opt) {
                '-a' { $options.opt1 = [bool] 1}
                '-a' { $options.altium = [bool] 1}
                '-a' { $options.all = [bool] 1 }
                '-a' { $options.add = [bool] 1 }
                '-b' { $options.label = [bool] 1 }
                '-all' { $options.opt1 = [bool] 1 }
                '-last' { $options.last = [bool] 1 }
                '-c' { $options.opt2 = [bool] 1 }
                '-j' { $options.jira = [bool] 1; $options.opt2 = [bool] 1 }                    
                '-c' { $options.opt3 = [bool] 1;$options.create=[bool]1}
                '-n' { $options.new = [bool] 1 }
                '-u' { $options.upload = [bool] 1 }
                '-u' { $options.user = [bool] 1 }
                '-d' { $options.dev = [bool] 1;$options.delete = [bool] 1;$options.draft = [bool] 1 }
                '-s' { $options.slack = [bool] 1}
                '-s' { $options.search = [bool] 1}
                '-s' { $options.set = [bool] 1}
                '-l' { $options.link = [bool] 1 }
                '-l' { $options.list = [bool] 1 }
                '-i' { $options.doing = [bool] 1 }
                '-f' { $options.info = [bool] 1 }
                '-o' { $options.open = [bool] 1 }
                '-k' { $options.key = [bool] 1 }
                '-g' { $options.files = [bool] 1 }
                '-r' { $options.refresh = [bool] 1 }
                '-v' { $options.history = [bool] 1 }
                '-w' { $options.wiki = [bool] 1 }
                '-m' { $options.mergeopen = [bool] 1;$options.me = [bool] 1 }
                '--help' { Write-Host $help -ForegroundColor Cyan; break 1 }
                '-h' { Write-Host $help -ForegroundColor Cyan; break 1 }
                default { 
                    Write-Host "Bad option: $opt is not a valid option." -ForegroundColor Red
                    throw "Error: Bad Option"
                }
            }
            $argv.Remove($opt)
        }
    }            
    return [array]$argv, $options
}
function jiraIssues {
    param (
        $issueList, $jql
    )
    $limit = 99
    #
    # 컴포넌트 상위 하위(타입) 상태 담당자 설명 Link
    #
    # $issue.fields.issueLinks.inwardIssue
    # $issue.fields.issueLinks.outwardIssue
    $jiraIssues = getIssuesByJql($jql)
    $jiraIssues
    $issueTypeName = "(^작업|문제해결|기능|UI|규격)"
    $issues = $jiraIssues | Where-Object { $($_.fields.issueType.name -match $issueTypeName) }
    if ($issues.count) {
        foreach ($issue in $Issues) {
            # Write-Output $issue.fields.issueLinks.type
            # Write-Output $issue.fields.issueLinks.inwardI(ssue
            $linked_issues = ""
            if (-not [string]::IsNullOrEmpty($issue.fields.issueLinks.inwardIssue)) {
                $linked_issues = $($issue.fields.issueLinks.inwardIssue.key -join ',')
                $linked_issues = ($linked_issues -replace '[0-9A-Z]+\-', "")
            } 
            $status = $($issue.fields.status.name.replace(' ', ''))
            $prefix = " ";
            if ($status -eq "진행중") {
                $prefix = "*"
            }
            elseif ($status -eq "완료됨") {
                $prefix = "!"
            }
            if ($issue.fields.parent.key) {
                if ($issue.fields.parent.fields.issueType.name -eq '에픽') {
                    $parent_display = "(EPIC)[$($issue.fields.parent.key)]$($issue.fields.parent.fields.summary)"
                }
                else {
                    $parent_display = "[$($issue.fields.parent.key)]$($issue.fields.parent.fields.summary)"
                }
            }
            $issue_display = "$prefix[$($issue.key)]$($issue.fields.summary)"
            [void]($issueList.add(@{issueObject=$issue;updated = $($issue.fields.updated); Parent = $parent_display;Component = "$($issue.fields.components.name)"; IssueType = "$($issue.fields.issueType.name)"; Assignee = "$($issue.fields.assignee.displayName)"; LinkedIssue = "$linked_issues"; Issue = "$issue_display" }))
        }
    }
    if ($global:JOB -eq "DEV") {
        $issueTypeName = "^(Gitlab|하위|BugFix|Hotfix)"
    }
    elseif ($global:JOB -eq "ALTIUM") {
        $issueTypeName = "^(Altium|하위|BugFix|Hotfix)"
    }
    else {
        $issueTypeName = "^(하위)"
    }
    $issues = $jiraIssues | Where-Object { $($_.fields.issueType.name -match $issueTypeName) }
    if ($issues.count) {
        foreach ($issue in $Issues) {
            $count++
            if ($count -le $limit) {
                $linked_issues = "";
                if (-not [string]::IsNullOrEmpty($issue.fields.issueLinks.inwardIssue)) {
                    $linked_issues = $($issue.fields.issueLinks.inwardIssue.key -join ',')
                    $linked_issues = ($linked_issues -replace '[0-9A-Z]+\-', "")
                }
                $status = $($issue.fields.status.name.replace(' ', ''))
                $prefix = " ";
                if ($status -eq "진행중") {
                    $prefix = "*"
                }
                elseif ($status -eq "완료됨") {
                    $prefix = "!"
                }
                if ($issue.fields.parent.key) {
                    if ($issue.fields.parent.fields.issueType.name -eq '에픽') {
                        $parent_display = "(EPIC)[$($issue.fields.parent.key)]$($issue.fields.parent.fields.summary)"
                    }
                    else {
                        $parent_display = "[$($issue.fields.parent.key)]$($issue.fields.parent.fields.summary)"
                    }
                }
                $issue_display = "$prefix[$($issue.key)]$($issue.fields.summary)"
                [void]($issueList.add(@{issueObject=$issue;updated = $($issue.fields.updated); Parent = $parent_display;Component = "$($issue.fields.components.name)"; IssueType = "$($issue.fields.issueType.name)"; Assignee = "$($issue.fields.assignee.displayName)"; LinkedIssue = "$linked_issues"; Issue = "$issue_display" }))
                # [void]($issueList.add(@{updated = $($issue.fields.updated); Parent = $parent_display;Component = "$($issue.fields.components.name)"; IssueType = "$($issue.fields.issueType.name)"; Assignee = "$($issue.fields.assignee.displayName)"; LinkedIssue = "$linked_issues"; Issue = "$issue_display" }))
            } 
        }
    }
}
function conflunece_page_list {
    try {
        $space = Get-ConfluenceSpace -SpaceKey $project_key -Credential $cred
        if ($space) {
            $pages = Get-ConfluencePage -SpaceKey $project_key -Credential $cred;
            $pages | Format-Table @{
                Label      = "Confluence"
                Expression = { $_.Title }
            }, Version, @{
                Label      = "ID"
                Expression =
                {
                    "https://jltechrnd.atlassian.net/wiki/spaces/$project_key/pages/$($_.ID)"
                }
            } -AutoSize
        }
    }
    catch {
    }
}

function lucid_access_token {
    $client_id = "a85f4sB3ueTfBwOKxwOQ-cZxhiOFSEzgdsPoNIDm"
    $client_secret = "T3A5lgtaIJJjym9ISnSDC1t2gOomrL9A2mzICrlhRM2mn5XWhPow6zRD5WSPa6ZRHm388XCD_KT9-COFbO3J"
    $secureTxtPath = "$HOME/.lucid_token.txt"

    if (Test-Path $secureTxtPath) {
        $refresh_token = Get-Content $secureTxtPath
        $body = @{
            refresh_token = "$refresh_token"
            client_id     = $client_id
            client_secret = $client_secret
            grant_type    = "refresh_token"
        }
        $response = Invoke-RestMethod -Method Post -Uri https://api.lucid.co/oauth2/token -Body $body
        $response.refresh_token | Set-Content -Path $secureTxtPath
        $access_token = $response.access_token
        return $access_token;
    } else {
        $redirect_url = "https://lucid.app/oauth2/clients/$client_id/redirect"
        $scope = "lucidchart.document.content+offline_access"
        $url = "https://lucid.app/oauth2/authorizeUser?client_id=$client_id&redirect_uri=$redirect_url&scope=$scope"
        $message = "아래 주소를 연후 rnd@jltech.co.kr로 인증 후 결과 코드를 입력해주세요`n" + $url + "`nCode"
        $code = Read-Host "$message"
        # $response = Invoke-RestMethod -Method Get -Uri $url;
        # $response;
        # exit 0
        $body = @{
            code          = "$code"
            client_id     = $client_id
            client_secret = $client_secret
            grant_type    = "authorization_code"
            redirect_uri  = "https://lucid.app/oauth2/clients/$client_id/redirect"
        }
        $response = Invoke-RestMethod -Method Post -Uri https://api.lucid.co/oauth2/token -Body $body
        # Extract access token from the response
        $response.refresh_token | Set-Content -Path $secureTxtPath
    }
}

function showgitlabissue {
    param (
        $project, $gitlabissueList
    )
    $limit = 99
    $count = 0
    if ($project.path_with_namespace -match 'fork') {
        $issue = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.forked_from_project.id)/issues?state=opened"
    }
    else {
        $issue = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.id)/issues?state=opened"
    }
    if ($issues.count) {
        foreach ($issue in $Issues) {
            $count++
            if ($count -le $limit) {
                $utc = $issue.updated_at
                $updated_at_str = $([System.TimeZoneInfo]::ConvertTime($utc, $global:kst))
                [void]($gitlabissueList.add(@{Gitlab = $issue.title; Link = $issue.web_url; Updated_at = $updated_at_str }))
            } 
        }
    }
}

function get_mr_info {
    param (
        $command
    )
    # URL-encoded project path
    if ($working_repo.path_with_namespace -match "fork") {
        $project = $working_repo.forked_from_project
    }
    else {
        $project = $working_repo
    }
    $mr_list = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.id)/merge_requests?state=opened"
    if ($mr_list.count -gt 0) {
        Write-Host "=== Opend MR on Main " -ForegroundColor green
        if ($mr_list) {
            foreach ($mr in $mr_list) {
                # get full info for pipelines and diverged commits count
                if ($($mr.author.name) -eq "$env:USER_NAME" -and ($mr.source_branch -eq 'main')) {
                    $found_mr = $mr
                    Write-Host "- title: $($mr.title) opened by $($mr.author.name) - labels: $($mr.labels -join ', ')" -ForegroundColor Yellow
                    Write-Host "- mr_url:($($mr.source_branch)=>$($mr.target_branch)) $($mr.web_url)" -ForegroundColor Yellow`
                }
                else {
                    Write-Host "- title: $($mr.title) opened by $($mr.author.name) - labels: $($mr.labels -join ', ')"
                    Write-Host "- mr_url:($($mr.source_branch)=>$($mr.target_branch)) $($mr.web_url)" 
                }
            }
        }
    }
    return $found_mr
}

function pipeline_info {
    param (
        $project
    )
    try {
        $pipeline_info = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.id)/pipelines"
        $global:kst = [System.TimeZoneInfo]::FindSystemTimeZoneById("Korea Standard Time")
        $time = $([System.TimeZoneInfo]::ConvertTime($($pipeline_info[0].updated_at), $global:kst))
        if ($pipeline_info[0].status -eq 'failed') {
            Write-Host "[CI/CD]status:$($pipeline_info[0].status) Last Updated:$($time)" -ForegroundColor red
        }
        elseif ($pipeline_info[0].status -eq 'success') {
            Write-Host "[CI/CD]status:$($pipeline_info[0].status) Last Updated:$($time)" -ForegroundColor blue
        }
        else {
            Write-Host "[CI/CD]status:$($pipeline_info[0].status) Last Updated:$($time)" 
        }
        Write-Host "Pipeline:$($pipeline_info[0].web_url)" -ForegroundColor blue
        if ($project.forked_from_project) {
            $project = $project.forked_from_project
            $pipeline_info = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.id)/pipelines"
            $global:kst = [System.TimeZoneInfo]::FindSystemTimeZoneById("Korea Standard Time")
            $time = $([System.TimeZoneInfo]::ConvertTime($($pipeline_info[0].updated_at), $global:kst))
            if ($pipeline_info[0].status -eq 'failed') {
                Write-Host "[CI/CD]status:$($pipeline_info[0].status) Last Updated:$($time)" -ForegroundColor red
            }
            elseif ($pipeline_info[0].status -eq 'success') {
                Write-Host "[CI/CD]status:$($pipeline_info[0].status) Last Updated:$($time)" -ForegroundColor blue
            }
            else {
                Write-Host "[CI/CD]status:$($pipeline_info[0].status) Last Updated:$($time)" 
            }
            Write-Host "Pipeline:$($pipeline_info[0].web_url)" -ForegroundColor blue
        }
    }
    catch {
    }
}
function jira_rest_api {
    param (
        $method, $uri, $data
    )

    $SecureCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes(
            $('{0}:{1}' -f $cred.UserName, $cred.GetNetworkCredential().Password )
        ))
    try {
        if ($data) {
            # $result = (Invoke-WebRequest -Method $method -Headers @{"Authorization" = "Basic ZHNraW1Aamx0ZWNoLmNvLmtyOjBGQ3dkanlHRENHaGVTeUc5OWI2M0Q2Mw==" }  -uri "$uri" -ContentType 'application/json;charset=utf-8' -Body $data)
            $result = (Invoke-WebRequest -Method $method -Headers @{"Authorization" = "Basic $SecureCreds" }  -uri "$uri" -ContentType 'application/json;charset=utf-8' -Body $data)
        }
        else {
            # $result = (Invoke-WebRequest -Method $method  -Headers @{"Authorization" = "Basic ZHNraW1Aamx0ZWNoLmNvLmtyOjBGQ3dkanlHRENHaGVTeUc5OWI2M0Q2Mw==" }  -uri "$uri" -ContentType 'application/json;charset=utf-8' )
            $result = (Invoke-WebRequest -Method $method  -Headers @{"Authorization" = "Basic $SecureCreds" }  -uri "$uri" -ContentType 'application/json;charset=utf-8' )
        }
    }
    catch {
        throw "$_`n$method Error:$uri"
    }
    return ($result.content | ConvertFrom-Json);
}
function getIssuesByJql {
    param (
        $jql
    )
    $jqlUrlEncode = $([System.Web.HTTPUtility]::UrlEncode("$jql"))
    $issues = $(jira_rest_api GET "https://jltechrnd.atlassian.net/rest/api/3/search?jql=$($jqlUrlEncode)&per_page=100").issues
    return $issues
}
 function get_filter {
    param ($state,$options)
    $jql ="project ='$project_key' AND issueType not in (Epic) AND status in ($state)"
    if ($options.opt1) {
        # $jql += " AND (component = Null OR component = '$global:component')"
    } else {
        # $jql += " AND assignee in ($env:JIRA_USERID,NULL)"
        if ($component) {
            $jql += " AND component = '$global:component'"
        }
    }
    return  $jql
 }   

function commits_info {
    param (
        [Parameter(Mandatory = $true)]  $project,
        [Parameter(Mandatory = $false)]  [bool]$onlyNotSame 
    )
    if ($onlyNotSame) {
        $display = $false;
    }
    else {
        $display = $true;
    }
    $commitList = New-Object System.Collections.ArrayList
    $url_branch_name = [uri]::EscapeDataString($global:current_branch_name)
    $commits = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.id)/repository/commits?ref_name=$url_branch_name"
    forEach ($lastCommit in $commits) {
        if (-not ($lastCommit.message -match '^Merge\sbranch')) {
            break;
        }
    }

    if ($lastCommit) {
        $utc = $($lastCommit.committed_date)
        $TimeString = $([System.TimeZoneInfo]::ConvertTime($utc, $global:kst))
        $Author = $lastCommit.committer_name
        $Url = $($lastCommit.web_url)
        $Title = $($lastCommit.message)
        if ([string]::IsNullOrWhiteSpace($project.forked_from_project.id) -or $onlyNotSame) {
            $ForkedBy = "Upstream"
            [void]($commitList.add(@{Utc = $utc; Link = "$($project.web_url)"; Remote = "upstream"; Time = "$TImeString"; Author = "$Author"; url = "$Url" ; Message = "$Title"; ForkedBy = "$ForkedBy" }))
        } else {
            $ForkedBy = "Me"
            [void]($commitList.add(@{Utc = $utc; Link = "$($project.web_url)"; Remote = "origin"; Time = "$TImeString"; Author = "$Author"; url = "$Url" ; Message = "$Title"; ForkedBy = "$ForkedBy" }))
        }
    }

    if ($lastCommit.web_url -match '\/fork\/(\w+)' ) {
        #forked folder project
        if (-not [string]::IsNullOrWhiteSpace($project.forked_from_project.id)) {
            $commits = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.forked_from_project.id)/repository/commits"
            forEach ($lastCommit in $commits) {
                if (-not ($lastCommit.message -match '^Merge\sbranch')) {
                    break;
                }
            }
            $utc = $($lastCommit.committed_date)
            $TimeString = $([System.TimeZoneInfo]::ConvertTime($utc, $global:kst))
            $Author = $lastCommit.committer_name
            $ForkedBy = "Upstream"
            $Url = $($lastCommit.web_url)
            $Title = $($lastCommit.message)
            [void]($commitList.add(@{Utc = $utc; Link = "$($project.forked_from_project.web_url)"; Remote = "upstream"; Time = "$TImeString"; Author = "$Author"; url = "$Url" ; Message = "$Title"; ForkedBy = "$ForkedBy" }))
        }
        if ($commitList[0].Utc -gt $commitList[1].Utc) {
            $forkRepoStatus = "**** origin  >>>>>>> upsream"
        }
        elseif ($commitList[0].Utc -lt $commitList[1].Utc) {
            $forkRepoStatus = "**** origin <<<<<<< upstream"
        }
        else {
            $forkRepoStatus = "**** origin == upstream"
        }
    }
    elseif ($project.forks_count) {
        $forkList = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($project.id)/forks"
        foreach ($forked in $forkList) {
            $commits = gitlab_rest_api GET "https://gitlab.com/api/v4/projects/$($forked.id)/repository/commits" 
            forEach ($lastCommit in $commits) {
                if (-not ($lastCommit.message -match '^Merge\sbranch')) {
                    break;
                }
            }
            $utc = $($lastCommit.committed_date)
            $TimeString = $([System.TimeZoneInfo]::ConvertTime($utc, $global:kst))
            $Author = $lastCommit.committer_name
            $ForkedBy = $forked.namespace.name;
            $Url = $($lastCommit.web_url)
            $Title = $($lastCommit.message)
            [void]($commitList.add(@{Utc = $utc; Link = "$($forked.web_url)"; Remote = "forked"; Time = "$TImeString"; Author = "$Author"; url = "$Url" ; Message = "$Title"; ForkedBy = "$ForkedBy" }))
            if ($onlyNotSame) {
                if ($commitList[0].Utc -gt $utc) {
                    $display=$true;
                }
                elseif ($commitList[0].Utc -lt $utc) {
                    $display=$true;
                } else {
                    $display=$display || $false;
                }
            }
        }
    }
    if ($display) {
        $tableData = $($commitList | ForEach-Object { New-Object object | Add-Member -NotePropertyMembers $_ -PassThru })
        $sorted_data = $tableData | Sort-Object -Descending -Property Utc
        if ($sorted_data[0].Remote -ne "upstream" -and $onlyNotSame) {
            $sorted_data | Format-Table Remote, Link, Time, Author, ForkedBy, Message -AutoSize
        } elseif (-not $onlyNotSame -and $forkRepoStatus -ne "") {
            $sorted_data | Format-Table Remote, Link, Time, Author, ForkedBy, Message -AutoSize
            if ($forkRepoStatus -ne "") {
                Write-Output $forkRepoStatus
            }
        }
    }
}

$options = @{
        opt1 = [bool] 0
        opt2 = [bool] 0
        opt3 = [bool] 0
    }
$line_help = "Project 상황 정보: status [-h|-a] [todo|doing|done]"
$help = @"
    Project 상황 정보
    사용법: status [-h|-a] [todo|doing|done]

    Options:         
        -h,--help   Help    Prints this message
        -a,--all    모든 Jira Issue 검색
"@
if ($args[0] -eq 'help') {
    Write-Host "$arg[1] $line_help" -ForegroundColor cyan
    exit 0
}

[void](init)
[void](checkCurrentFolder)
$argv,$options = parseOptions $args $options $help
if ($argv) {
    $global:arg1 = $argv[0]
    $global:arg2 = $argv[1]
} else {
    $global:arg1 = ""
    $global:arg2 = ""
}

$issueList = New-Object System.Collections.ArrayList
if ($arg1 -eq 'done') {
    [void](jiraIssues $issueList "$(get_filter "'Done'" $options)" )
} elseif ($arg1 -eq 'todo') {
    [void](jiraIssues $issueList "$(get_filter "'To Do'" $options)" "$global:component")
} elseif ($arg1 -eq 'last') {
    [void](jiraIssues $issueList "$(filter_last $options)" "$global:component")
} elseif ($arg1 -eq 'doing') {
    [void](jiraIssues $issueList "$(get_filter "'In Progress'" $options)" "$global:component")
} else {
    [void](jiraIssues $issueList "$(get_filter "'In Progress','To Do'" $options)" "$global:component")
}
$tableData = $($issueList | ForEach-Object { New-Object object | Add-Member -NotePropertyMembers $_ -PassThru })
# $tableData
# exit 0
$tableData | Format-Table Component, IssueType,Assignee,@{
    Label = "버젼"
    Expression = { $_.issueObject.fields.fixVersions.name }
 },@{
    Label = "Jira Issue"
    Expression =
    {
        if ($_.IssueType -eq "문제해결")
            { $color = "41"}
        else 
            { $color = "0" }
        $e = [char]27
       "$e[${color}m$($_.Issue)${e}[0m"
    }
 },Parent,LinkedIssue,@{
    Label = "버젼"
    Expression = { $_.issueObject.fields.fixVersions.name }
 } -AutoSize

conflunece_page_list

try {
    $access_token = lucid_access_token; 
    $headers = @{
        Authorization       = "Bearer $access_token"
        "Lucid-Api-Version" = "1"
        "Content-Type"      = "application/json" 
    }
    $body = @{ 
        product  = @("lucidchart")
        keywords = "#$project_key"
    }
    $json = ConvertTo-Json -inputObject $body
    $temp = Invoke-RestMethod -Method POST -Uri 'https://api.lucid.co/documents/search' -Header $headers -Body $json
    $list = $($temp | ForEach-Object { Write-Output $_  }) | Where-Object -FilterScript { [string]::IsNullOrEmpty($_.trashed) } 
    if ($list.count -ne 0) {
        $list | Format-Table @{
            Label      = "Lucid"
            Expression = { $_.title }
        }, editUrl, lastModified -AutoSize
    }
}
catch {
    Write-Host "Lucid Auth Error" -ForegroundColor red
}

if ($JOB -ne 'JIRA') {
    $gitlabissueList = New-Object System.Collections.ArrayList
    [void](showgitlabissue $working_repo $gitlabissueList)
    $tableData = $($gitlabissueList | ForEach-Object { New-Object object | Add-Member -NotePropertyMembers $_ -PassThru })
    $tableData | Sort-Object -Descending -Property Updated_at | Format-Table Gitlab, Link, Updated_at -AutoSize

    $gitstatus = (Get-GitStatus)
    if ($gitstatus.working) {
        Write-Host "=== 수정된 문서=========" -ForegroundColor red
        Write-Host ($gitstatus.working -join "`r`n") -ForegroundColor red
        Write-Host "========================" -ForegroundColor red
    }
    [void](get_mr_info "status")
    [void](pipeline_info $working_repo)
    Write-Output (commits_info $working_repo)
    if (-not [string]::IsNullOrWhiteSpace($working_repo.forked_from_project.id)) {
        Write-Output (commits_info $working_repo.forked_from_project)
    }
}