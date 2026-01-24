# 📄 Display Rules Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L155)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Use Rules In Prompt](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Display Rules Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-rules-action-shows-rules-digest-in-cli-output"></a>
### Scenario: [Rules action shows rules digest in CLI output](#scenario-rules-action-shows-rules-digest-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L168)

**Steps:**
```gherkin
GIVEN: CLI is at shape.validate (which shows rules)
WHEN: user navigates to shape.validate
THEN: CLI output contains formatted rules digest
```


<a id="scenario-validation-output-includes-rules-content"></a>
### Scenario: [Validation output includes rules content](#scenario-validation-output-includes-rules-content) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L201)

**Steps:**
```gherkin
GIVEN: CLI is at shape.validate
WHEN: user navigates to shape.validate
THEN: CLI output contains validation rules
```


<a id="scenario-user-gets-rules-instructions-for-behavior"></a>
### Scenario: [User gets rules instructions for behavior](#scenario-user-gets-rules-instructions-for-behavior) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-user-gets-rules-with-message-parameter"></a>
### Scenario: [User gets rules with message parameter](#scenario-user-gets-rules-with-message-parameter) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-user-gets-rules-without-message-parameter"></a>
### Scenario: [User gets rules without message parameter](#scenario-user-gets-rules-without-message-parameter) (happy_path)

**Steps:**
```gherkin

```

