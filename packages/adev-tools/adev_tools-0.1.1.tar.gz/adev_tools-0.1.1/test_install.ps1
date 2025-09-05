# ADEV Tools 설치 테스트 스크립트

param(
    [Parameter(Mandatory=$false)]
    [switch]$TestPyPI,
    
    [Parameter(Mandatory=$false)]
    [switch]$LocalInstall
)

# 색상 정의
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Blue"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "🧪 ADEV Tools 설치 테스트" $Blue
Write-ColorOutput "================================" $Blue

# 테스트용 가상환경 생성
$testEnvPath = ".test_env"
if (Test-Path $testEnvPath) {
    Write-ColorOutput "🗑️ 기존 테스트 환경 제거 중..." $Yellow
    Remove-Item -Recurse -Force $testEnvPath
}

Write-ColorOutput "📦 테스트 가상환경 생성 중..." $Yellow
python -m venv $testEnvPath

Write-ColorOutput "🔧 테스트 환경 활성화 중..." $Yellow
& "$testEnvPath\Scripts\Activate.ps1"

# pip 업그레이드
pip install --upgrade pip

# 설치 방법에 따른 설치
if ($LocalInstall) {
    Write-ColorOutput "📦 로컬 패키지 설치 중..." $Yellow
    pip install -e .
} elseif ($TestPyPI) {
    Write-ColorOutput "📦 Test PyPI에서 설치 중..." $Yellow
    pip install --index-url https://test.pypi.org/simple/ adev-tools
} else {
    Write-ColorOutput "📦 PyPI에서 설치 중..." $Yellow
    pip install adev-tools
}

if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "❌ 설치 실패" $Red
    exit 1
}

Write-ColorOutput "✅ 설치 완료" $Green

# CLI 명령어 테스트
Write-ColorOutput "🧪 CLI 명령어 테스트 중..." $Yellow

$commands = @(
    "adev-fork",
    "adev-branch", 
    "adev-commit",
    "adev-diff2commit",
    "adev-cloneupstream",
    "adev-ci-copy",
    "adev-ci-stlink",
    "adev-gitlab-runner-status",
    "adev-issues",
    "adev-gdrive-config",
    "adev-gdrive-upload",
    "adev-gdrive-open-altium",
    "adev-pre-build",
    "adev-post-build",
    "adev-test-branch",
    "adev-test-gdrive",
    "adev-test-upload-download",
    "adev-config-example"
)

$successCount = 0
$totalCount = $commands.Count

foreach ($cmd in $commands) {
    try {
        Write-ColorOutput "Testing: $cmd --help" $Blue
        & $cmd --help 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ $cmd" $Green
            $successCount++
        } else {
            Write-ColorOutput "❌ $cmd (exit code: $LASTEXITCODE)" $Red
        }
    } catch {
        Write-ColorOutput "❌ $cmd (exception: $($_.Exception.Message))" $Red
    }
}

# 결과 요약
Write-ColorOutput "================================" $Blue
Write-ColorOutput "📊 테스트 결과" $Blue
Write-ColorOutput "성공: $successCount / $totalCount" $(if ($successCount -eq $totalCount) { $Green } else { $Yellow })

if ($successCount -eq $totalCount) {
    Write-ColorOutput "🎉 모든 명령어가 정상적으로 작동합니다!" $Green
} else {
    Write-ColorOutput "⚠️ 일부 명령어에 문제가 있습니다." $Yellow
}

# 테스트 환경 정리
Write-ColorOutput "🧹 테스트 환경 정리 중..." $Yellow
deactivate
Start-Sleep -Seconds 2
Remove-Item -Recurse -Force $testEnvPath

Write-ColorOutput "🏁 테스트 완료" $Blue
