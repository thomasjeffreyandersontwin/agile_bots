# Render Examples - Story IO CLI
# Examples showing how to render story graphs to DrawIO files

# Get script directory and navigate to workspace root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path

# Change to workspace root
Set-Location $WorkspaceRoot

# Example 1: Basic outline render
Write-Host "Example 1: Basic outline render" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 render-outline `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story-map-outline.drawio"

# Example 2: Render with increments
Write-Host "`nExample 2: Render with increments" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 render-increments `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story-map-increments.drawio"

# Example 3: Render from different project
Write-Host "`nExample 3: Render from different project" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 render-outline `
    -StoryGraph "demo/cheap_wealth_online/docs/stories/structured.json" `
    -Output "demo/cheap_wealth_online/docs/stories/story-map-outline.drawio"

Write-Host "`nAll render examples completed!" -ForegroundColor Green
