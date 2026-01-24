# 📄 Load and Display Workspace Context in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Set Workspace](.)  
**Sequential Order:** 1.0
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

