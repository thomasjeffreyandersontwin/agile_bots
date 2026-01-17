# Synchronize Examples - Story IO CLI
# Examples showing how to synchronize story graphs from DrawIO files

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path
Set-Location $WorkspaceRoot

# Example 1: Basic outline sync (extract from DrawIO)
Write-Host "Example 1: Basic outline sync" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Output "demo/mm3e_animations/docs/story_graph_synced.json"

# Example 2: Sync with original for comparison
Write-Host "`nExample 2: Sync with original for comparison" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_synced.json"

# Example 3: Sync increments
Write-Host "`nExample 3: Sync increments" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 sync-increments `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-increments.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_increments_synced.json"

Write-Host "`nAll sync examples completed!" -ForegroundColor Green
