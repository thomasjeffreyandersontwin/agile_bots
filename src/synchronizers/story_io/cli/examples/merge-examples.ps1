# Merge Examples - Story IO CLI
# Examples showing how to merge extracted story graphs with originals

# Example 1: Basic merge (extract, then merge)
Write-Host "Example 1: Basic merge workflow" -ForegroundColor Cyan

# Step 1: Sync from DrawIO to extract changes
Write-Host "Step 1: Extracting from DrawIO..." -ForegroundColor Yellow
.\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_extracted.json"

# Step 2: Generate merge report and merge
Write-Host "`nStep 2: Merging extracted with original..." -ForegroundColor Yellow
.\story-io.ps1 merge `
    -Extracted "demo/mm3e_animations/docs/story_graph_extracted.json" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_merged.json" `
    -ReportPath "demo/mm3e_animations/docs/merge_report.json"

Write-Host "Merge completed! Check merge_report.json for details." -ForegroundColor Green

# Example 2: Merge with custom report path
Write-Host "`nExample 2: Merge with custom report path" -ForegroundColor Cyan
.\story-io.ps1 merge `
    -Extracted "demo/mm3e_animations/docs/story_graph_extracted.json" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_merged_custom.json" `
    -ReportPath "demo/mm3e_animations/docs/reports/custom_merge_report.json"

# Example 3: Complete edit-merge-render workflow
Write-Host "`nExample 3: Complete edit-merge-render workflow" -ForegroundColor Cyan

# 1. Render initial diagram
Write-Host "Step 1: Rendering initial diagram..." -ForegroundColor Yellow
.\story-io.ps1 render-outline `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story-map-outline-workflow.drawio"

Write-Host "Now edit the DrawIO file manually..." -ForegroundColor Yellow
Write-Host "Press any key when done editing..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 2. Sync back from edited DrawIO
Write-Host "`nStep 2: Syncing changes from DrawIO..." -ForegroundColor Yellow
.\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline-workflow.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_workflow_extracted.json"

# 3. Merge to preserve original data (Steps, behavioral_ac, etc.)
Write-Host "`nStep 3: Merging to preserve original data..." -ForegroundColor Yellow
.\story-io.ps1 merge `
    -Extracted "demo/mm3e_animations/docs/story_graph_workflow_extracted.json" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_workflow_merged.json"

# 4. Re-render with merged data
Write-Host "`nStep 4: Re-rendering with merged data..." -ForegroundColor Yellow
.\story-io.ps1 render-outline `
    -StoryGraph "demo/mm3e_animations/docs/story_graph_workflow_merged.json" `
    -Output "demo/mm3e_animations/docs/story-map-outline-workflow-final.drawio"

Write-Host "`nAll merge examples completed!" -ForegroundColor Green

