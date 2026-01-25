# Bump version, rebuild, and reinstall the Bot Panel extension
# Usage: .\panel_bump_and_install.ps1 [patch|minor|major] [-NoReload]
# Default: patch (0.1.0 -> 0.1.1), auto-reloads window
# -NoReload: Skip automatic window reload (requires manual reload)

param(
    [ValidateSet('patch', 'minor', 'major')]
    [string]$BumpType = 'patch',
    
    [switch]$NoReload = $false
)

$ErrorActionPreference = 'Stop'

# Navigate to panel directory using relative paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agileDir = Split-Path -Parent (Split-Path -Parent $scriptDir)  # Get workspace root (two levels up from src\panel)
$panelDir = Join-Path (Join-Path $agileDir "src") "panel"
Set-Location $panelDir

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Bot Panel Version Bump" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Read current version from package.json
$packageJsonPath = Join-Path $panelDir "package.json"
$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
$currentVersion = $packageJson.version
Write-Host "Current version: $currentVersion" -ForegroundColor Yellow

# Parse version
$versionParts = $currentVersion -split '\.'
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]
$patch = [int]$versionParts[2]

# Bump version based on type
switch ($BumpType) {
    'major' { 
        $major++
        $minor = 0
        $patch = 0
    }
    'minor' { 
        $minor++
        $patch = 0
    }
    'patch' { 
        $patch++
    }
}

$newVersion = "$major.$minor.$patch"
Write-Host "New version:     $newVersion" -ForegroundColor Green
Write-Host ""

# Update package.json
Write-Host "[1/6] Updating package.json..." -ForegroundColor Cyan
$packageJsonContent = Get-Content $packageJsonPath -Raw
$packageJsonContent = $packageJsonContent -replace "`"version`":\s*`"$currentVersion`"", "`"version`": `"$newVersion`""
# Write without BOM to avoid vsce JSON parse errors
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($packageJsonPath, $packageJsonContent, $utf8NoBom)
# Give filesystem time to sync
Start-Sleep -Milliseconds 200
Write-Host "      Done: package.json updated" -ForegroundColor Green

# Package extension
Write-Host "[2/6] Packaging extension..." -ForegroundColor Cyan
# Remove old vsix files first
Remove-Item "$panelDir\bot-panel-*.vsix" -Force -ErrorAction SilentlyContinue
# Kill Cursor's sandbox offline mode entirely
Remove-Item Env:\npm_config_offline -ErrorAction SilentlyContinue
Remove-Item Env:\npm_config_prefer_offline -ErrorAction SilentlyContinue
$env:npm_config_offline = $null
$env:npm_config_prefer_offline = $null
# Prefer local vsce (avoids npx fetch / cache/network issues)
$vsceExe = Join-Path $panelDir "node_modules\.bin\vsce.cmd"
if (Test-Path $vsceExe) {
    & $vsceExe package --allow-missing-repository --allow-star-activation 2>&1 | Out-Null
} else {
    npx @vscode/vsce package --allow-missing-repository --allow-star-activation 2>&1 | Out-Null
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: Packaging failed!" -ForegroundColor Red
    exit 1
}
# Verify the file was created
Start-Sleep -Milliseconds 500
Write-Host "      Done: Extension packaged: bot-panel-$newVersion.vsix" -ForegroundColor Green

# Uninstall old extension
Write-Host "[3/6] Uninstalling old extension..." -ForegroundColor Cyan
cursor --uninstall-extension agilebot.bot-panel > $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Warning: Uninstall warning (may not be installed)" -ForegroundColor Yellow
} else {
    Write-Host "      Done: Old extension uninstalled" -ForegroundColor Green
}

# Install new extension
Write-Host "[4/6] Installing new extension..." -ForegroundColor Cyan
$vsixPath = Join-Path $panelDir "bot-panel-$newVersion.vsix"
if (-not (Test-Path $vsixPath)) {
    Write-Host "      ERROR: VSIX file not found: $vsixPath" -ForegroundColor Red
    exit 1
}
cursor --install-extension "$vsixPath" --force > $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR: Installation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "      Done: Extension v$newVersion installed" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Extension upgraded: $currentVersion -> $newVersion" -ForegroundColor Green
Write-Host ""

# Auto-reload window by default
if (-not $NoReload) {
    Write-Host "[5/6] Reloading Cursor window..." -ForegroundColor Cyan
    try {
        # Find the Cursor window and send reload command
        # This uses VS Code's command URI scheme
        $reloadCmd = "cursor://command/workbench.action.reloadWindow"
        Start-Process $reloadCmd -ErrorAction SilentlyContinue
        
        # Give it a moment
        Start-Sleep -Milliseconds 500
        
        Write-Host "      Done: Window reload triggered" -ForegroundColor Green
        Write-Host ""
        Write-Host "Extension v$newVersion will be active momentarily!" -ForegroundColor Green
    } catch {
        Write-Host "      Warning: Could not auto-reload. Please reload manually:" -ForegroundColor Yellow
        Write-Host "      Press Ctrl+Shift+P -> Developer: Reload Window" -ForegroundColor Yellow
    }
} else {
    Write-Host "Extension installed successfully!" -ForegroundColor Green
    Write-Host "The extension may activate automatically, or you can reload when ready:" -ForegroundColor Cyan
    Write-Host "  Ctrl+Shift+P -> Developer: Reload Window" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To skip auto-reload: .\panel_bump_and_install.ps1 -NoReload" -ForegroundColor DarkGray
}
Write-Host ""
