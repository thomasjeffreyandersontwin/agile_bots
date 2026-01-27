# 📄 Execute Actions With Scope Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L415)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Execute Actions With Scope Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-execution-uses-active-scope-via-cli"></a>
### Scenario: [Action execution uses active scope via CLI](#scenario-action-execution-uses-active-scope-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L428)

**Steps:**
```gherkin
GIVEN: CLI session with scope set
WHEN: action executed
THEN: Action operates within scope
```

