# Add User Examples - Story IO CLI
# Examples showing how to add users to stories

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..\..\..\..") | Select-Object -ExpandProperty Path
Set-Location $WorkspaceRoot

# Example 1: Add GM user to a specific story
Write-Host "Example 1: Add GM user to 'Receive Power Characteristics'" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 add-user `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -StoryName "Receive Power Characteristics" `
    -UserName "GM" `
    -Output "demo/mm3e_animations/docs/story-map-outline-with-gm.drawio"

# Example 2: Add user with epic and feature specified
Write-Host "`nExample 2: Add user with epic/feature context" -ForegroundColor Cyan
.\agile_bot\bots\story_bot\src\story_io\story-io.ps1 add-user `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -StoryName "Request Base Templates" `
    -UserName "System" `
    -EpicName "Build Animation from Components" `
    -FeatureName "Assemble Animation from Base Templates" `
    -Output "demo/mm3e_animations/docs/story-map-outline-with-system-user.drawio"

Write-Host "`nAll add-user examples completed!" -ForegroundColor Green
