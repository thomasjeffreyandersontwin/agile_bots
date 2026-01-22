# 📄 Persist Story Graph Changes From Diagram

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Synch Graph From Rendered](..) / [⚙️ Synchronize Graph](.)  
**Sequential Order:** 6.0
**Story Type:** user

## Story Description

Persist Story Graph Changes From Diagram functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot's StoryMap completes reading and applying all batches successfully
  **then** Bot's StoryMap structure matches diagram's StoryMap structure
  **and** all node names, types, hierarchy, and ordering match
  **and** Bot's StoryMap logs summary (nodes added, deleted, renamed, moved)
  **and** Bot's StoryMap persists updated story_graph to file using save() method

- **When** Bot's StoryMap encounters errors during batch application
  **then** Bot's StoryMap identifies which operation failed and why
  **and** Bot's StoryMap rolls back incomplete batch to maintain consistency
  **and** Bot's StoryMap reports error details to user

## Scenarios

### Scenario: Persist Story Graph Changes From Diagram (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
