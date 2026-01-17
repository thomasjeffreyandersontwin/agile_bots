# Complete Workflow Example - Story IO CLI
# This example demonstrates a complete workflow from rendering to editing to merging

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
.\story-io.ps1 render-outline `
    -StoryGraph $StoryGraphPath `
    -Output "$OutputDir/01-initial-outline.drawio"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error rendering outline!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Initial outline rendered" -ForegroundColor Green

# Step 2: Search for stories to modify
Write-Host "`nStep 2: Searching for stories..." -ForegroundColor Yellow
.\story-io.ps1 search `
    -StoryGraph $StoryGraphPath `
    -Query "Power" `
    -Type "story" | Out-File "$OutputDir/02-search-results.txt"
Write-Host "[OK] Search results saved to search-results.txt" -ForegroundColor Green

# Step 3: Add users to stories
Write-Host "`nStep 3: Adding users to stories..." -ForegroundColor Yellow
$StoriesToUpdate = @(
    @{Story="Receive Power Characteristics"; User="GM"},
    @{Story="Extract Power Item"; User="System"},
    @{Story="Extract Target Token"; User="System"}
)

foreach ($Story in $StoriesToUpdate) {
    Write-Host "  Adding user '$($Story.User)' to '$($Story.Story)'..." -ForegroundColor Gray
    .\story-io.ps1 add-user `
        -StoryGraph $StoryGraphPath `
        -StoryName $Story.Story `
        -UserName $Story.User `
        -Output "$OutputDir/03-with-users.drawio"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [WARNING] Failed to add user to $($Story.Story)" -ForegroundColor Yellow
    }
}
Write-Host "[OK] Users added to stories" -ForegroundColor Green

# Step 4: Render with increments
Write-Host "`nStep 4: Rendering with increments..." -ForegroundColor Yellow
.\story-io.ps1 render-increments `
    -StoryGraph $StoryGraphPath `
    -Output "$OutputDir/04-increments.drawio"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error rendering increments!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Increments diagram rendered" -ForegroundColor Green

# Step 5: Synchronize back from edited DrawIO (simulated)
Write-Host "`nStep 5: Simulating synchronization from edited DrawIO..." -ForegroundColor Yellow
Write-Host "  (In real workflow, you would edit the DrawIO file first)" -ForegroundColor Gray

# Use the file we just created as if it was edited
if (Test-Path "$OutputDir/03-with-users.drawio") {
    .\story-io.ps1 sync-outline `
        -DrawIOFile "$OutputDir/03-with-users.drawio" `
        -Original $StoryGraphPath `
        -Output "$OutputDir/05-extracted.json"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Changes extracted from DrawIO" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Sync failed (this is expected if DrawIO wasn't manually edited)" -ForegroundColor Yellow
    }
}

# Step 6: Merge extracted with original
Write-Host "`nStep 6: Merging extracted with original (if extracted exists)..." -ForegroundColor Yellow
if (Test-Path "$OutputDir/05-extracted.json") {
    .\story-io.ps1 merge `
        -Extracted "$OutputDir/05-extracted.json" `
        -Original $StoryGraphPath `
        -Output "$OutputDir/06-merged.json" `
        -ReportPath "$OutputDir/06-merge-report.json"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Merged story graph created" -ForegroundColor Green
        Write-Host "  Check merge-report.json for details" -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] No extracted file to merge" -ForegroundColor Gray
}

# Step 7: Final render of merged data
Write-Host "`nStep 7: Rendering final merged diagram..." -ForegroundColor Yellow
if (Test-Path "$OutputDir/06-merged.json") {
    .\story-io.ps1 render-outline `
        -StoryGraph "$OutputDir/06-merged.json" `
        -Output "$OutputDir/07-final.drawio"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Final diagram rendered" -ForegroundColor Green
    }
} else {
    Write-Host "  [SKIP] No merged file to render" -ForegroundColor Gray
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
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open $OutputDir/01-initial-outline.drawio in DrawIO" -ForegroundColor White
Write-Host "  2. Edit the diagram as needed" -ForegroundColor White
Write-Host "  3. Run sync-outline to extract changes" -ForegroundColor White
Write-Host "  4. Run merge to preserve original data" -ForegroundColor White
Write-Host "  5. Re-render final diagram" -ForegroundColor White

