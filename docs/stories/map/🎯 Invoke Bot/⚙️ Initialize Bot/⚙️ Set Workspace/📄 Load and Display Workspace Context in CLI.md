# 📄 Load and Display Workspace Context in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_set_workspace.py#L143)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Set Workspace](.)  
**Sequential Order:** 0.0
**Story Type:** system

## Story Description

Load and Display Workspace Context in CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-loads-and-displays-workspace-context"></a>
### Scenario: [CLI loads and displays workspace context](#scenario-cli-loads-and-displays-workspace-context) ()

**Steps:**
```gherkin
GIVEN: Bot has workspace path
AND: workspace contains story-graph.json
WHEN: REPLSession initializes CLIBot
THEN: CLIBot loads workspace context from bot paths
```

