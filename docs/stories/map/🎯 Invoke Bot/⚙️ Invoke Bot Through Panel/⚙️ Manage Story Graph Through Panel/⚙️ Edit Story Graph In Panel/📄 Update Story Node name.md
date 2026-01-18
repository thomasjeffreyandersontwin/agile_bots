# 📄 Update Story Node name

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Manage Story Graph Through Panel](..) / [⚙️ Edit Story Graph In Panel](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Update Story Node name functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot Behavior submits valid node identifier AND new node name
  **then** System validates node exists in graph
  **and** System validates new name not empty
  **and** System validates new name unique among siblings
  **and** System updates node name

- **When** Bot Behavior submits node identifier for non-existent node
  **then** System identifies node does not exist
  **and** System returns error with node identifier

- **When** Bot Behavior submits empty or whitespace-only name
  **then** System validates name not empty
  **and** System returns error indicating invalid name

- **When** Bot Behavior submits name that duplicates sibling node name
  **then** System checks sibling node names
  **and** System identifies duplicate name
  **and** System returns error with duplicate node name

- **When** Bot Behavior updates name with special characters
  **then** System validates name format
  **and** System updates node name if valid
  **and** System returns error if name contains invalid characters

## Scenarios

### Scenario: Update Story Node name (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
