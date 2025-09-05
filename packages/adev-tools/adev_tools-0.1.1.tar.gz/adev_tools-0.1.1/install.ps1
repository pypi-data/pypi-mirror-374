# Ensure dist directory exists
if (-not (Test-Path -Path "dist" -PathType Container)) {
    New-Item -Path "dist" -ItemType Directory
}

Get-ChildItem -Filter "*.py" | ForEach-Object {
    if ($_.Name -ne "ci_lib.py" -and $_.Name -ne "adev_lib.py" -and -not $_.Name.StartsWith("wip")) {
        $exePath = Join-Path -Path "dist" -ChildPath ($_.BaseName + ".exe")
        $shouldBuild = $false
        
        # Check if EXE doesn't exist or Python file is newer
        if (-not (Test-Path -Path $exePath)) {
            $shouldBuild = $true
        }
        else {
            $pyLastWrite = $_.LastWriteTime
            $exeLastWrite = (Get-Item $exePath).LastWriteTime
            if ($pyLastWrite -gt $exeLastWrite) {
                $shouldBuild = $true
            }
        }

        if ($shouldBuild) {
            pyinstaller --onefile $_.Name
            Write-Host "Built: $($_.Name)"
            Copy-Item -Path $exePath -Destination $env:SP -Force
        }
        else {
            Write-Host "Skipped: $($_.Name) (up to date)"
        }
    }
}

# Uncomment this section if you want to convert PS1 scripts to EXE
<#
Get-ChildItem -Filter "*.ps1" | ForEach-Object {
    if ($_.Name -ne "install.ps1") {
        Invoke-PS2EXE -InputFile $_.Name -OutputFile "dist/$($_.Name.Replace('.ps1', '.exe'))"
    }
}
#>
# Cleanup spec files
Remove-Item -Path "*.spec" -Force