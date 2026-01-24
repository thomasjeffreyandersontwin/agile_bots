# 📄 Filter Scope By Files Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_scope_files.py#L202)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Files](..) / [⚙️ Filter File Scope](.)  
**Sequential Order:** 6.0
**Story Type:** user

## Story Description

Filter Scope By Files Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-files-with-include-pattern-via-cli"></a>
### Scenario: [Scope files with include pattern via CLI](#scenario-scope-files-with-include-pattern-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_scope_files.py#L215)

**Steps:**
```gherkin
GIVEN: CLI session
WHEN: scope set to files with include pattern
THEN: Matching files in scope
```


<a id="scenario-scope-files-with-exclude-pattern-via-cli"></a>
### Scenario: [Scope files with exclude pattern via CLI](#scenario-scope-files-with-exclude-pattern-via-cli) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_scope_files.py#L239)

**Steps:**
```gherkin
GIVEN: CLI session
WHEN: scope set with exclude pattern
THEN: Excluded files not in scope
```

