# 📄 Track Action Completion

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Directly](..) / [⚙️ Track Activity](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Track Action Completion functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Action completes execution

  **then** Activity entry is updated with outputs and duration

  **and** Entry appended to activity_log.json

## Scenarios

<a id="scenario-action-completion-tracking"></a>
### Scenario: [Action completion tracking](#scenario-action-completion-tracking) (happy_path)

**Steps:**
```gherkin
Given Action has executed
When Action completes
Then Completion is tracked in completed_actions
```

