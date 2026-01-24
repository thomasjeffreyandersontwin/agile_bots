# 📄 Get Help Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L178)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Get Help](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Get Help Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-instructions-are-shown-in-cli-output"></a>
### Scenario: [Action instructions are shown in CLI output](#scenario-action-instructions-are-shown-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L191)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify
WHEN: user navigates to action
THEN: CLI output shows action instructions
```


<a id="scenario-action-parameter-help-is-shown-in-cli-output"></a>
### Scenario: [Action parameter help is shown in CLI output](#scenario-action-parameter-help-is-shown-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L218)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify
WHEN: user navigates to action with parameters
THEN: CLI output shows parameter information
```


<a id="scenario-action-shows-usage-information-in-cli-output"></a>
### Scenario: [Action shows usage information in CLI output](#scenario-action-shows-usage-information-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L250)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify
WHEN: user navigates to action
THEN: CLI output shows how to use the action
```

