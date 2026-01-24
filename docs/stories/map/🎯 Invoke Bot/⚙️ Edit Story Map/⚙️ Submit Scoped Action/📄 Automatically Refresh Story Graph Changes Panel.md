# 📄 Automatically Refresh Story Graph Changes Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Submit Scoped Action](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Automatically Refresh Story Graph Changes Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Panel detects file modification
  **then** Panel reads updated graph
  **and** validates structure
  **and** Panel refreshes StoryGraph Tree
  **and** Panel preserves navigation state if possible

- **When** System detects invalid structure
  **then** System identifies violations
  **and** displays error notification
  **and** retains previous valid state

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is loaded in Panel
```

## Scenarios

<a id="scenario-panel-detects-file-modification-and-refreshes-with-valid-structure"></a>
### Scenario: [Panel detects file modification and refreshes with valid structure](#scenario-panel-detects-file-modification-and-refreshes-with-valid-structure) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" selected
And Panel is displaying Epic "Invoke Bot" details
And file monitor is watching story-graph.json
When external process modifies story-graph.json by adding SubEpic "New Feature"
And Panel detects file modification
Then Panel reads updated story-graph.json
And Panel validates graph structure
And Panel refreshes Story Graph Tree
And Panel preserves navigation state showing Epic "Invoke Bot"
And Story Tree displays new SubEpic "New Feature"
```


<a id="scenario-panel-detects-invalid-structure-and-displays-error-retaining-previous-state"></a>
### Scenario: [Panel detects invalid structure and displays error retaining previous state](#scenario-panel-detects-invalid-structure-and-displays-error-retaining-previous-state) (error_case)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And Panel is displaying valid Story Graph Tree
And file monitor is watching story-graph.json
When external process modifies story-graph.json with invalid JSON syntax
And Panel detects file modification
And Panel reads updated story-graph.json
Then Panel validates graph structure
And System identifies JSON parsing violations
And Panel displays error notification "Story graph file contains invalid structure"
And Panel retains previous valid Story Graph state
And Story Tree still shows Epic "Invoke Bot" with SubEpic "Manage Bot"
```

