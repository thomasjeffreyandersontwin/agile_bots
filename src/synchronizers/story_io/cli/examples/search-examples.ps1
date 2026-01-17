# Search Examples - Story IO CLI
# Examples showing how to search for components in story graphs

# Example 1: Search for any component with "Power"
Write-Host "Example 1: Search for any component with 'Power'" -ForegroundColor Cyan
.\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Power"

# Example 2: Search for epics only
Write-Host "`nExample 2: Search for epics only" -ForegroundColor Cyan
.\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Animation" `
    -Type "epic"

# Example 3: Search for features only
Write-Host "`nExample 3: Search for features only" -ForegroundColor Cyan
.\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Trigger" `
    -Type "feature"

# Example 4: Search for stories only
Write-Host "`nExample 4: Search for stories only" -ForegroundColor Cyan
.\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Receive" `
    -Type "story"

# Example 5: Search for specific story name
Write-Host "`nExample 5: Search for specific story name" -ForegroundColor Cyan
.\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "Receive Power Characteristics" `
    -Type "story"

# Example 6: Case-insensitive partial match search
Write-Host "`nExample 6: Case-insensitive partial match search" -ForegroundColor Cyan
.\story-io.ps1 search `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Query "template" `
    -Type "story"

Write-Host "`nAll search examples completed!" -ForegroundColor Green

