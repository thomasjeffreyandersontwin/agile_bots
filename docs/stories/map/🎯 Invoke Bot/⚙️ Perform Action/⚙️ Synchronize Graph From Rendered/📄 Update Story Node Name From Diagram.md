# 📄 Update Story Node Name From Diagram

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Synchronize Graph From Rendered](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Update Story Node Name From Diagram functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot's StoryMap reads batch of rename operations from Synchronizer
  **then** Bot's StoryMap updates node names to match diagram's StoryMap names
  **and** Bot's StoryMap validates no duplicate names at same hierarchy level
  **and** Bot's StoryMap updates all references to renamed nodes

- **When** Bot's StoryMap reads rename operation that creates duplicate name at same level
  **then** Bot's StoryMap identifies duplicate name
  **and** Bot's StoryMap reports error

## Scenarios

### Scenario: Update Story Node Name From Diagram (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
