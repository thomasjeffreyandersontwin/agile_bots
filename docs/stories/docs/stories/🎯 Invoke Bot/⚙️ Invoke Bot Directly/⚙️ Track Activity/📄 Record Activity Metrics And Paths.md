# 📄 Record Activity Metrics And Paths

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Directly](..) / [⚙️ Track Activity](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Record Activity Metrics And Paths functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Activity is tracked

  **then** Metrics include file counts and content types

  **and** Paths include file paths not content

  **and** Activity log captures metrics and paths

## Scenarios

### Scenario: Record Activity Metrics And Paths (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```
