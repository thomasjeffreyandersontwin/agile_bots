# 📄 Get Help

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Get Bot Help](..) / [⚙️ Get Help](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Get Help functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-verify-actions-can-provide-instructions"></a>
### Scenario: [Verify actions can provide instructions](#scenario-verify-actions-can-provide-instructions) (happy_path)

**Steps:**
```gherkin
Given Bot has behavior with action
When Action is accessed
Then Action has method to get instructions
Then Domain focus: Action instructions method availability
```


<a id="scenario-action-provides-parameter-help-via-help-property"></a>
### Scenario: [Action provides parameter help via .help property](#scenario-action-provides-parameter-help-via-help-property) (happy_path)

**Steps:**
```gherkin
Given Bot has behavior with action
When Action.help is accessed
Then Returns dict with description and parameters list
Then Domain focus: Parameter help retrieval from Action.help
```


<a id="scenario-action-provides-command-examples"></a>
### Scenario: [Action provides command examples](#scenario-action-provides-command-examples) (happy_path)

**Steps:**
```gherkin
Given Bot has behavior with action
When Command examples are requested
Then Action returns usage examples
Then Domain focus: Command examples retrieval
```

