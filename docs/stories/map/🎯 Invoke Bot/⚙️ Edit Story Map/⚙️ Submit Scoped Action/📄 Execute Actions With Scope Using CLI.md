# 📄 Execute Actions With Scope Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L609)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Submit Scoped Action](.)  
**Sequential Order:** 10.0
**Story Type:** user

## Story Description

Execute Actions With Scope Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-execution-uses-active-scope-via-cli"></a>
### Scenario: [Action execution uses active scope via CLI](#scenario-action-execution-uses-active-scope-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L622)

**Steps:**
```gherkin
GIVEN: CLI session with scope set
WHEN: action executed
THEN: Action operates within scope
```

