# Complete Workflow Example - Story IO CLI
# This example demonstrates a complete workflow from rendering to editing to merging

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path
Set-Location $WorkspaceRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete Story IO Workflow Example" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$StoryGraphPath = "demo/mm3e_animations/docs/story_graph.json"
$OutputDir = "demo/mm3e_animations/docs/workflow"

# Create workflow directory
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Step 1: Render initial outline
Write-Host "Step 1: Rendering initial outline..." -ForegroundColor Yellow
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 render-outline `
    -StoryGraph $StoryGraphPath `
    -Output "$OutputDir/01-initial-outline.drawio"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Initial outline rendered" -ForegroundColor Green
} else {
    Write-Host "Error rendering outline!" -ForegroundColor Red
    exit 1
}

# Step 2: Search for stories
Write-Host "`nStep 2: Searching for stories..." -ForegroundColor Yellow
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 search `
    -StoryGraph $StoryGraphPath `
    -Query "Power" `
    -Type "story" | Out-File "$OutputDir/02-search-results.txt"

Write-Host "[OK] Search results saved" -ForegroundColor Green

# Step 3: Add users to stories
Write-Host "`nStep 3: Adding users to stories..." -ForegroundColor Yellow
Write-Host "  Adding user 'GM' to 'Receive Power Characteristics'..." -ForegroundColor Gray
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 add-user `
    -StoryGraph $StoryGraphPath `
    -StoryName "Receive Power Characteristics" `
    -UserName "GM" `
    -Output "$OutputDir/03-with-users.drawio"

Write-Host "[OK] Users added to stories" -ForegroundColor Green

# Step 4: Render with increments
Write-Host "`nStep 4: Rendering with increments..." -ForegroundColor Yellow
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 render-increments `
    -StoryGraph $StoryGraphPath `
    -Output "$OutputDir/04-increments.drawio"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Increments diagram rendered" -ForegroundColor Green
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Workflow Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Files created in: $OutputDir" -ForegroundColor White
Get-ChildItem -Path $OutputDir -File | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}

Write-Host "`n[SUCCESS] Complete workflow finished!" -ForegroundColor Green
