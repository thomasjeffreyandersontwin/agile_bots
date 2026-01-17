# Synchronize Examples - Story IO CLI
# Examples showing how to synchronize story graphs from DrawIO files

# Example 1: Basic outline sync (extract from DrawIO)
Write-Host "Example 1: Basic outline sync" -ForegroundColor Cyan
.\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Output "demo/mm3e_animations/docs/story_graph_synced.json"

# Example 2: Sync with original for comparison
Write-Host "`nExample 2: Sync with original for comparison" -ForegroundColor Cyan
.\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_synced.json"

# Example 3: Sync increments
Write-Host "`nExample 3: Sync increments" -ForegroundColor Cyan
.\story-io.ps1 sync-increments `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-increments.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_increments_synced.json"

# Example 4: Sync from edited DrawIO file
Write-Host "`nExample 4: Sync from edited DrawIO file" -ForegroundColor Cyan
# After manually editing the DrawIO file, sync changes back
.\story-io.ps1 sync-outline `
    -DrawIOFile "demo/mm3e_animations/docs/story-map-outline-edited.drawio" `
    -Original "demo/mm3e_animations/docs/story_graph.json" `
    -Output "demo/mm3e_animations/docs/story_graph_from_edit.json"

Write-Host "`nAll sync examples completed!" -ForegroundColor Green

