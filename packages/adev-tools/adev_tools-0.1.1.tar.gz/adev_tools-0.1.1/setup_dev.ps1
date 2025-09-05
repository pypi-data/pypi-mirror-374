# ADEV Tools 개발 환경 설정 스크립트

param(
    [Parameter(Mandatory=$false)]
    [switch]$ForceReinstall
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

Write-ColorOutput "🔧 ADEV Tools 개발 환경 설정" $Blue
Write-ColorOutput "================================" $Blue

# Python 버전 확인
Write-ColorOutput "🐍 Python 버전 확인 중..." $Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "❌ Python이 설치되지 않았습니다." $Red
    exit 1
}
Write-ColorOutput "✅ $pythonVersion" $Green

# 가상환경 설정
if ($ForceReinstall -and (Test-Path ".venv")) {
    Write-ColorOutput "🗑️ 기존 가상환경 제거 중..." $Yellow
    Remove-Item -Recurse -Force ".venv"
}

if (-not (Test-Path ".venv")) {
    Write-ColorOutput "📦 가상환경 생성 중..." $Yellow
    python -m venv .venv
}

Write-ColorOutput "🔧 가상환경 활성화 중..." $Yellow
.\.venv\Scripts\Activate.ps1

# pip 업그레이드
Write-ColorOutput "📦 pip 업그레이드 중..." $Yellow
python -m pip install --upgrade pip

# 개발 종속성 설치
Write-ColorOutput "📦 개발 종속성 설치 중..." $Yellow
pip install -e ".[dev]"

# pre-commit 훅 설정 (선택사항)
Write-ColorOutput "🔗 개발 도구 설정 중..." $Yellow
pip install pre-commit
# pre-commit install

# 설정 파일 템플릿 생성
Write-ColorOutput "📝 설정 파일 확인 중..." $Yellow
if (-not (Test-Path "adev_config.yml")) {
    if (Test-Path "adev_config_template.yml") {
        Copy-Item "adev_config_template.yml" "adev_config.yml"
        Write-ColorOutput "✅ 설정 파일 템플릿이 adev_config.yml로 복사되었습니다." $Green
        Write-ColorOutput "⚠️ adev_config.yml 파일을 편집하여 설정을 완료하세요." $Yellow
    }
}

# CLI 명령어 테스트
Write-ColorOutput "🧪 CLI 명령어 테스트 중..." $Yellow
$testCommands = @(
    "adev-fork --help",
    "adev-branch --help", 
    "adev-commit --help"
)

foreach ($cmd in $testCommands) {
    Write-ColorOutput "Testing: $cmd" $Blue
    Invoke-Expression $cmd
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ $cmd 성공" $Green
    } else {
        Write-ColorOutput "❌ $cmd 실패" $Red
    }
}

Write-ColorOutput "================================" $Blue
Write-ColorOutput "🎉 개발 환경 설정 완료!" $Green
Write-ColorOutput "" $White
Write-ColorOutput "다음 단계:" $Yellow
Write-ColorOutput "1. adev_config.yml 파일을 편집하여 API 키 및 설정 완료" $White
Write-ColorOutput "2. 가상환경 활성화: .\.venv\Scripts\Activate.ps1" $White
Write-ColorOutput "3. 테스트 실행: pytest" $White
Write-ColorOutput "4. 코드 포맷팅: black ." $White
Write-ColorOutput "5. 린팅: flake8 ." $White
