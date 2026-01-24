# 📄 Validate Rules Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L209)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Validate With Rules](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Validate Rules Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-validate-action-shows-rules-in-cli-output"></a>
### Scenario: [Validate action shows rules in CLI output](#scenario-validate-action-shows-rules-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L222)

**Steps:**
```gherkin
GIVEN: CLI is at shape.validate
AND: Story graph exists
WHEN: user navigates to shape.validate
THEN: CLI output contains rule descriptions and DO/DON'T sections
```


<a id="scenario-code-validate-action-shows-file-rules-in-cli-output"></a>
### Scenario: [Code validate action shows file rules in CLI output](#scenario-code-validate-action-shows-file-rules-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L256)

**Steps:**
```gherkin
GIVEN: CLI is at code.validate
AND: Story graph exists
WHEN: user navigates to code.validate
THEN: CLI output contains file validation rules
```

