# 📄 Inject Context Into Instructions

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Prepare Common Instructions For Behavior, Action, and Scope](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Inject Context Into Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-loads-context-data-into-instructions"></a>
### Scenario: [Action Loads Context Data Into Instructions](#scenario-action-loads-context-data-into-instructions) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-next-behavior-reminder-is-not-injected-when-action-is-not-final"></a>
### Scenario: [Next behavior reminder is NOT injected when action is not final](#scenario-next-behavior-reminder-is-not-injected-when-action-is-not-final) (happy_path)

**Steps:**
```gherkin
Given validate is NOT the final action (render comes after)
When validate action executes
Then base_instructions do NOT include next behavior reminder
Then And bot_config.json defines behavior sequence
```


<a id="scenario-next-behavior-reminder-is-not-injected-when-current-behavior-is-last-in-sequence"></a>
### Scenario: [Next behavior reminder is NOT injected when current behavior is last in sequence](#scenario-next-behavior-reminder-is-not-injected-when-current-behavior-is-last-in-sequence) (happy_path)

**Steps:**
```gherkin
Given discovery is the last behavior in bot_config.json
When render action executes
Then base_instructions do NOT include next behavior reminder
Then And render is the final action
```

