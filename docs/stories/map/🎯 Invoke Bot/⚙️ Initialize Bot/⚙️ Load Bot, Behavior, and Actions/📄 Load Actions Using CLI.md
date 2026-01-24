# 📄 Load Actions Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L574)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Load Actions Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-session-loads-actions-from-behavior-config"></a>
### Scenario: [CLI session loads actions from behavior config](#scenario-cli-session-loads-actions-from-behavior-config) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L587)

**Steps:**
```gherkin
GIVEN: CLI session at shape behavior
WHEN: Actions accessed
THEN: All actions loaded correctly
```


<a id="scenario-cli-session-sets-first-action-as-current"></a>
### Scenario: [CLI session sets first action as current](#scenario-cli-session-sets-first-action-as-current) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L615)

**Steps:**
```gherkin
GIVEN: CLI session at shape behavior
WHEN: Current action accessed
THEN: First action is current
```


<a id="scenario-action-instructions-accessible-via-cli-session"></a>
### Scenario: [Action instructions accessible via CLI session](#scenario-action-instructions-accessible-via-cli-session) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L639)

**Steps:**
```gherkin
GIVEN: CLI session at shape.clarify
WHEN: Action instructions accessed
THEN: Merged instructions from base and behavior available
```

