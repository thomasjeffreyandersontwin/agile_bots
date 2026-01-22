# 📄 Move Story Node From Diagram

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Synch Graph From Rendered](..) / [⚙️ Synchronize Graph](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Move Story Node From Diagram functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot's StoryMap reads batch of move/reorder operations from Synchronizer
  **then** Bot's StoryMap removes nodes from old parent
  **and** Bot's StoryMap adds nodes to new parent at correct position
  **and** Bot's StoryMap updates sequential_order values to match diagram's StoryMap ordering
  **and** Bot's StoryMap resequences siblings in both old and new parent locations

- **When** Bot's StoryMap reads move operation to new parent with specified position
  **then** Bot's StoryMap inserts at specified position
  **and** Bot's StoryMap resequences existing siblings at or after position

## Scenarios

### Scenario: Move Story Node From Diagram (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
