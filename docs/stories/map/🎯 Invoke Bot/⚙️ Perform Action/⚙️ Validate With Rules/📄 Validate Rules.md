# 📄 Validate Rules

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L29)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Validate With Rules](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Validate Rules functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-story-graph-validation-includes-rule-content-in-instructions"></a>
### Scenario: [Story graph validation includes rule content in instructions](#scenario-story-graph-validation-includes-rule-content-in-instructions) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L32)

**Steps:**
```gherkin
Given Production story_bot with shape behavior (validates story graph)
When Validate action executes
Then Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files
Then And Story graph file exists
```


<a id="scenario-file-validation-includes-rule-content-in-instructions"></a>
### Scenario: [File validation includes rule content in instructions](#scenario-file-validation-includes-rule-content-in-instructions) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L60)

**Steps:**
```gherkin
Given Production story_bot with code behavior (validates files)
When Validate action executes
Then Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files
Then And Story graph file exists
```


<a id="scenario-story-graph-scanners-receive-scoped-story_graph-data"></a>
### Scenario: [Story graph scanners receive scoped story_graph data](#scenario-story-graph-scanners-receive-scoped-story_graph-data) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L88)

**Steps:**
```gherkin
Given Story graph with multiple epics ("Build Knowledge", "Epic B")
When Validate action executes with scope
Then Scanner receives filtered story graph (only "Build Knowledge" epic)
Then And Scope filtered to "Build Knowledge" epic
Then And Production story_bot with shape behavior
Then And Scanner executes successfully
Then And Instructions contain "Build Knowledge" in scope description
```


<a id="scenario-file-scanners-receive-scoped-file-paths"></a>
### Scenario: [File scanners receive scoped file paths](#scenario-file-scanners-receive-scoped-file-paths) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_validate_with_rules.py#L137)

**Steps:**
```gherkin
Given Multiple Python files (test_foo.py, test_bar.py, main.py)
When Validate action executes with scope
Then Scanner receives filtered files (only test_foo.py, test_bar.py)
Then And Scope filtered to test files only (**/test*.py)
Then And Production story_bot with code behavior
Then And Scanner executes successfully
Then And Instructions reference test file scope
```

