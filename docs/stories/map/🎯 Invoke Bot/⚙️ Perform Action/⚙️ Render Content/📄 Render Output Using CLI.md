# 📄 Render Output Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_render_content.py#L108)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Render Content](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Render Output Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-render-action-shows-render-configs-in-cli-output"></a>
### Scenario: [Render action shows render configs in CLI output](#scenario-render-action-shows-render-configs-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_render_content.py#L121)

**Steps:**
```gherkin
GIVEN: CLI is at shape.render
WHEN: user navigates to shape.render
THEN: CLI output contains render configurations
```


<a id="scenario-render-output-mentions-synchronizers-execution"></a>
### Scenario: [Render output mentions synchronizers execution](#scenario-render-output-mentions-synchronizers-execution) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_render_content.py#L149)

**Steps:**
```gherkin
GIVEN: CLI is at shape.render
WHEN: user navigates to shape.render
THEN: CLI output mentions synchronizers
```

