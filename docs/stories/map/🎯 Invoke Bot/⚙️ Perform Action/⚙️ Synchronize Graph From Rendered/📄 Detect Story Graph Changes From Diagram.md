# 📄 Detect Story Graph Changes From Diagram

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Synchronize Graph From Rendered](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Detect Story Graph Changes From Diagram functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User makes changes to StoryOutput diagram
  **then** the StoryMap hanging off StoryOutput reflects those changes in its object model
  **and** the changes are visible when accessing the StoryMap directly via API
  **and** the StoryRenderedNodes maintain parent/child relationships matching the modified structure

- **When** User hits synchronize button
  **then** Synchronizer compares StoryOutput's StoryMap against Bot's story_graph
  **and** Synchronizer identifies all differences (added nodes, deleted nodes, renamed nodes, moved nodes)
  **and** Synchronizer generates batch of change operations grouped by change type
  **and** Synchronizer calculates dependencies between changes (e.g., must create parent before child)

## Scenarios

### Scenario: Detect Story Graph Changes From Diagram (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
