# ADEV Tools PyPI 배포 스크립트

param(
    [Parameter(Mandatory=$false)]
    [string]$Version,
    
    [Parameter(Mandatory=$false)]
    [switch]$TestPyPI,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests
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

function Check-Command {
    param([string]$Command)
    if (!(Get-Command $Command -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "❌ $Command 가 설치되지 않았습니다." $Red
        return $false
    }
    return $true
}

Write-ColorOutput "🚀 ADEV Tools PyPI 배포 시작" $Blue
Write-ColorOutput "================================" $Blue

# 필수 도구 확인
Write-ColorOutput "📋 필수 도구 확인 중..." $Yellow

$requiredCommands = @("python", "pip", "git")
$allCommandsAvailable = $true

foreach ($cmd in $requiredCommands) {
    if (Check-Command $cmd) {
        Write-ColorOutput "✅ $cmd 사용 가능" $Green
    } else {
        $allCommandsAvailable = $false
    }
}

if (-not $allCommandsAvailable) {
    Write-ColorOutput "❌ 필수 도구가 누락되었습니다. 설치 후 다시 시도하세요." $Red
    exit 1
}

# 가상환경 확인 및 생성
if (-not (Test-Path ".venv")) {
    Write-ColorOutput "📦 가상환경 생성 중..." $Yellow
    python -m venv .venv
}

Write-ColorOutput "🔧 가상환경 활성화 중..." $Yellow
.\.venv\Scripts\Activate.ps1

# 빌드 도구 설치
Write-ColorOutput "📦 빌드 도구 설치 중..." $Yellow
pip install --upgrade pip
pip install build twine pytest black flake8

# 개발 종속성 설치
Write-ColorOutput "📦 개발 종속성 설치 중..." $Yellow
pip install -e ".[dev]"

# 버전 업데이트 (선택사항)
if ($Version) {
    Write-ColorOutput "📝 버전 업데이트: $Version" $Yellow
    # pyproject.toml에서 버전 업데이트
    $pyprojectPath = "pyproject.toml"
    $content = Get-Content $pyprojectPath
    $content = $content -replace 'version = "[^"]*"', "version = `"$Version`""
    Set-Content $pyprojectPath $content
    
    # __init__.py에서 버전 업데이트
    $initPath = "adev_tools/__init__.py"
    $content = Get-Content $initPath
    $content = $content -replace '__version__ = "[^"]*"', "__version__ = `"$Version`""
    Set-Content $initPath $content
}

# 테스트 실행 (생략 가능)
if (-not $SkipTests) {
    Write-ColorOutput "🧪 테스트 실행 중..." $Yellow
    pytest
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ 테스트 실패. 배포를 중단합니다." $Red
        exit 1
    }
    Write-ColorOutput "✅ 모든 테스트 통과" $Green
}

# 코드 품질 검사
Write-ColorOutput "🔍 코드 품질 검사 중..." $Yellow
black --check .
flake8 .

# 빌드 (생략 가능)
if (-not $SkipBuild) {
    Write-ColorOutput "🏗️ 패키지 빌드 중..." $Yellow
    
    # 이전 빌드 결과물 정리
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist"
    }
    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
    }
    if (Test-Path "*.egg-info") {
        Remove-Item -Recurse -Force "*.egg-info"
    }
    
    # 빌드 실행
    python -m build
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ 빌드 실패" $Red
        exit 1
    }
    Write-ColorOutput "✅ 빌드 완료" $Green
}

# 업로드 대상 결정
if ($TestPyPI) {
    $repository = "testpypi"
    $repositoryUrl = "https://test.pypi.org/legacy/"
    Write-ColorOutput "📤 Test PyPI에 업로드 중..." $Yellow
} else {
    $repository = "pypi"
    $repositoryUrl = "https://upload.pypi.org/legacy/"
    Write-ColorOutput "📤 PyPI에 업로드 중..." $Yellow
}

# 업로드 실행
Write-ColorOutput "🚀 배포 실행 중..." $Yellow
if ($TestPyPI) {
    twine upload --repository testpypi dist/*
} else {
    # 실제 PyPI 업로드 전 확인
    Write-ColorOutput "⚠️ 실제 PyPI에 배포하시겠습니까? (y/N)" $Yellow
    $confirm = Read-Host
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        twine upload dist/*
    } else {
        Write-ColorOutput "❌ 배포가 취소되었습니다." $Yellow
        exit 0
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput "🎉 배포 완료!" $Green
    Write-ColorOutput "설치 명령어: pip install adev-tools" $Blue
    if ($TestPyPI) {
        Write-ColorOutput "테스트 설치: pip install --index-url https://test.pypi.org/simple/ adev-tools" $Blue
    }
} else {
    Write-ColorOutput "❌ 배포 실패" $Red
    exit 1
}

Write-ColorOutput "================================" $Blue
Write-ColorOutput "🏁 배포 스크립트 완료" $Blue
