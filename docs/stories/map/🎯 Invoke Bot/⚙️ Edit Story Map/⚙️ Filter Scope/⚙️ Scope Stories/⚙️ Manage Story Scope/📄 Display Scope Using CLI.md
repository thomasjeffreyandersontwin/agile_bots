# 📄 Display Scope Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L120)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Display Scope Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-display-scope-shows-current-scope-via-cli"></a>
### Scenario: [Display scope shows current scope via CLI](#scenario-display-scope-shows-current-scope-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L132)

**Steps:**
```gherkin
GIVEN: CLI session with scope set
WHEN: scope displayed
THEN: Current scope shown in output
```

