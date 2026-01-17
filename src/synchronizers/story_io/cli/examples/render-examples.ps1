# Render Examples - Story IO CLI
# Examples showing how to render story graphs to DrawIO files

# Example 1: Basic outline render
Write-Host "Example 1: Basic outline render" -ForegroundColor Cyan
.\story-io.ps1 render-outline `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story-map-outline.drawio"

# Example 2: Render with increments
Write-Host "`nExample 2: Render with increments" -ForegroundColor Cyan
.\story-io.ps1 render-increments `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story-map-increments.drawio"

# Example 3: Render with layout preservation
Write-Host "`nExample 3: Render with layout preservation" -ForegroundColor Cyan
.\story-io.ps1 render-outline `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Layout "demo/mm3e_animations/docs/layout.json"

# Example 4: Render from different project
Write-Host "`nExample 4: Render from different project" -ForegroundColor Cyan
.\story-io.ps1 render-outline `
    -StoryGraph "demo/cheap_wealth_online/docs/stories/structured.json" `
    -Output "demo/cheap_wealth_online/docs/stories/story-map-outline.drawio"

# Example 5: Using absolute paths
Write-Host "`nExample 5: Using absolute paths" -ForegroundColor Cyan
$WorkspaceRoot = Get-Location
.\story-io.ps1 render-outline `
    -StoryGraph "$WorkspaceRoot\demo\mm3e_animations\docs\story_graph.json" `
    -Output "$WorkspaceRoot\demo\mm3e_animations\docs\story-map-outline.drawio"

Write-Host "`nAll render examples completed!" -ForegroundColor Green

