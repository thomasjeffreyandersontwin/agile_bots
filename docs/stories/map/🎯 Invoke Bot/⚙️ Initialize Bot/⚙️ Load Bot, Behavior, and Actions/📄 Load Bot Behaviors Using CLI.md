# 📄 Load Bot Behaviors Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L487)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 7.0
**Story Type:** user

## Story Description

Load Bot Behaviors Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-session-loads-behaviors-from-bot-config"></a>
### Scenario: [CLI session loads behaviors from bot config](#scenario-cli-session-loads-behaviors-from-bot-config) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L500)

**Steps:**
```gherkin
GIVEN: CLI session initialized
WHEN: Behaviors accessed
THEN: All behaviors loaded correctly
```


<a id="scenario-cli-session-sets-first-behavior-as-current"></a>
### Scenario: [CLI session sets first behavior as current](#scenario-cli-session-sets-first-behavior-as-current) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L521)

**Steps:**
```gherkin
GIVEN: CLI session initialized
WHEN: Current behavior accessed
THEN: First behavior is current
```


<a id="scenario-behavior-config-properties-accessible-via-cli-session"></a>
### Scenario: [Behavior config properties accessible via CLI session](#scenario-behavior-config-properties-accessible-via-cli-session) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L542)

**Steps:**
```gherkin
GIVEN: CLI session at prioritization behavior
WHEN: Behavior config properties accessed
THEN: All properties accessible with correct structure
```

