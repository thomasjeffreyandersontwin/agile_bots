# 📄 Decide Strategy Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_decide_strategy.py#L157)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Decide Strategy](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Decide Strategy Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-strategy-action-shows-criteria-and-assumptions-in-cli-output"></a>
### Scenario: [Strategy action shows criteria and assumptions in CLI output](#scenario-strategy-action-shows-criteria-and-assumptions-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_decide_strategy.py#L170)

**Steps:**
```gherkin
GIVEN: CLI is at shape.strategy
WHEN: user navigates to shape.strategy
THEN: CLI output contains decision criteria and assumptions
```

