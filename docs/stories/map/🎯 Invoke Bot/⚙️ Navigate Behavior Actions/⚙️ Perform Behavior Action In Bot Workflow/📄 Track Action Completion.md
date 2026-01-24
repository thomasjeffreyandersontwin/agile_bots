# 📄 Track Action Completion

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Perform Behavior Action In Bot Workflow](.)  
**Sequential Order:** 6.0
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
### Scenario: [Action completion tracking](#scenario-action-completion-tracking) ()

**Steps:**
```gherkin
Given Action has executed
When Action completes
Then Completion is tracked in completed_actions
```

