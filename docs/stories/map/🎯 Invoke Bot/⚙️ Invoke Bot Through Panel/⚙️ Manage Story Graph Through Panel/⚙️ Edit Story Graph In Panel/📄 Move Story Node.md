# 📄 Move Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Manage Story Graph Through Panel](..) / [⚙️ Edit Story Graph In Panel](.)  
**Sequential Order:** 4
**Story Type:** user

## Story Description

Move Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot Behavior submits valid node identifier AND new parent identifier AND new position
  **then** System validates source node exists
  **and** System validates target parent exists
  **and** System validates position within bounds
  **and** System removes node from current parent
  **and** System inserts node at new position under new parent
  **and** System resequences nodes in both locations

- **When** Bot Behavior moves node to same parent different position
  **then** System removes node from current position
  **and** System inserts node at new position
  **and** System resequences sibling nodes

- **When** Bot Behavior submits non-existent node identifier
  **then** System identifies node does not exist
  **and** System returns error with node identifier

- **When** Bot Behavior submits non-existent target parent identifier
  **then** System identifies parent does not exist
  **and** System returns error with parent identifier

- **When** Bot Behavior moves node to position exceeding sibling count
  **then** System validates position
  **and** System returns error with valid position range

- **When** Bot Behavior moves node to create circular reference
  **then** System validates target parent not descendant of source node
  **and** System returns error indicating circular reference

## Scenarios

### Scenario: Move Story Node (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
