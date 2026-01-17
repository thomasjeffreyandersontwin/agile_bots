# Search Examples - Story IO CLI
# Examples showing how to search for components in story graphs

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path
Set-Location $WorkspaceRoot

# Example 1: Search for any component with "Power"
Write-Host "Example 1: Search for any component with 'Power'" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Power"

# Example 2: Search for epics only
Write-Host "`nExample 2: Search for epics only" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Animation" `
    -Type "epic"

# Example 3: Search for features only
Write-Host "`nExample 3: Search for features only" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Trigger" `
    -Type "feature"

# Example 4: Search for stories only
Write-Host "`nExample 4: Search for stories only" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Receive" `
    -Type "story"

Write-Host "`nAll search examples completed!" -ForegroundColor Green
