# 📄 Create Scope Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L57)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Create Scope Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-set-with-different-parameter-combinations-via-cli"></a>
### Scenario: [Scope set with different parameter combinations via CLI](#scenario-scope-set-with-different-parameter-combinations-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L75)

**Steps:**
```gherkin
GIVEN: CLI session active
WHEN: user enters 'scope set <type> <value>'
THEN: CLI sets scope to specified type
```


<a id="scenario-scope-defaults-to-all-when-no-scope-set-via-cli"></a>
### Scenario: [Scope defaults to 'all' when no scope set via CLI](#scenario-scope-defaults-to-all-when-no-scope-set-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L101)

**Steps:**
```gherkin
GIVEN: CLI session with no scope set
WHEN: scope accessed
THEN: Default scope is 'all'
```

