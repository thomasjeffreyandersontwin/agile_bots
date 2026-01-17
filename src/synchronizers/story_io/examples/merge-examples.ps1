# Merge Examples - Story IO CLI
# Examples showing how to merge extracted story graphs with originals

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path
Set-Location $WorkspaceRoot

# Example 1: Basic merge (extract, then merge)
Write-Host "Example 1: Basic merge workflow" -ForegroundColor Cyan

# Step 1: Sync from DrawIO to extract changes
Write-Host "Step 1: Extracting from DrawIO..." -ForegroundColor Yellow
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_extracted.json"

# Step 2: Generate merge report and merge
Write-Host "`nStep 2: Merging extracted with original..." -ForegroundColor Yellow
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 merge `
    -Extracted "demo/mm3e_animations/docs/story_graph_extracted.json" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_merged.json" `
    -ReportPath "demo/mm3e_animations/docs/merge_report.json"

Write-Host "Merge completed! Check merge_report.json for details." -ForegroundColor Green

Write-Host "`nAll merge examples completed!" -ForegroundColor Green
