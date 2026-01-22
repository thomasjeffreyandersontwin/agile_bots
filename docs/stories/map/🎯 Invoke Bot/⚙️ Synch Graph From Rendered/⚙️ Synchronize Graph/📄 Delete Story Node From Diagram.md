# 📄 Delete Story Node From Diagram

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Synch Graph From Rendered](..) / [⚙️ Synchronize Graph](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Delete Story Node From Diagram functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot's StoryMap reads batch of delete operations from Synchronizer
  **then** Bot's StoryMap removes nodes from story_graph
  **and** Bot's StoryMap resequences remaining siblings after deletion
  **and** Bot's StoryMap handles cascade deletes (removing node removes all descendants)

- **When** Bot's StoryMap reads delete operation for node with children
  **then** Bot's StoryMap removes node and all descendants recursively
  **and** Bot's StoryMap logs all deleted nodes for audit trail

## Scenarios

### Scenario: Delete Story Node From Diagram (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
