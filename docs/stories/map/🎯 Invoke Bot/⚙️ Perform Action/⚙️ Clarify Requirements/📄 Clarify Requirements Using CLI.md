# 📄 Clarify Requirements Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_clarify_requirements.py#L193)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Clarify Requirements](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Clarify Requirements Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-clarify-action-shows-questions-and-evidence-in-cli-output"></a>
### Scenario: [Clarify action shows questions and evidence in CLI output](#scenario-clarify-action-shows-questions-and-evidence-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_clarify_requirements.py#L206)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify
WHEN: user navigates to shape.clarify
THEN: CLI output contains questions and evidence from guardrails
```

