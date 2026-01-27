# 📄 Automatically Refresh Story Graph Changes  CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.js#L1735)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Edit Story Map](.)  
**Sequential Order:** 20.0
**Story Type:** user

## Story Description

Automatically Refresh Story Graph Changes  CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** CLI detects file modification before next command
  **then** CLI reads updated graph
  **and** validates structure
  **and** CLI displays "Story graph updated from external source"
  **and** CLI executes command with updated graph

- **When** System detects invalid structure
  **then** System identifies violations
  **and** displays error notification
  **and** retains previous valid state

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized in CLI
```

## Scenarios

<a id="scenario-cli-detects-file-modification-before-command-and-refreshes-with-valid-structure"></a>
### Scenario: [CLI detects file modification before command and refreshes with valid structure](#scenario-cli-detects-file-modification-before-command-and-refreshes-with-valid-structure) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And file monitor is watching story-graph.json
And external process modifies story-graph.json by adding SubEpic "New Feature"
And CLI detects file modification before next command
When User executes CLI command: story_graph."Invoke Bot".list
Then CLI reads updated story-graph.json
And CLI validates graph structure
And CLI displays notification: "Story graph updated from external source"
And CLI executes command with updated graph
And CLI outputs list showing: "Manage Bot", "New Feature"
```


<a id="scenario-cli-detects-invalid-structure-and-displays-error-retaining-previous-state"></a>
### Scenario: [CLI detects invalid structure and displays error retaining previous state](#scenario-cli-detects-invalid-structure-and-displays-error-retaining-previous-state) (error_case)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And CLI has valid graph state loaded
And file monitor is watching story-graph.json
And external process modifies story-graph.json with invalid JSON syntax
And CLI detects file modification before next command
When User executes CLI command: story_graph."Invoke Bot".list
Then CLI reads updated story-graph.json
And CLI validates graph structure
And System identifies JSON parsing violations
And CLI displays error notification: "Story graph file contains invalid structure. Using previous valid state."
And CLI retains previous valid Story Graph state
And CLI executes command with previous valid graph
And CLI outputs list showing: "Manage Bot"
```

