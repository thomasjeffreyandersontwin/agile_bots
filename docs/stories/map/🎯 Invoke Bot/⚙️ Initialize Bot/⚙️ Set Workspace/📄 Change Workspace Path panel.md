# 📄 Change Workspace Path panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Set Workspace](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Change Workspace Path panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User changes workspace path

  **then** System displays updated workspace path

  **and** System displays behavior action state of new workspace

- **When** User sets workspace path

  **then** System persists workspace path value

- **When** Panel refreshes

  **then** System restores previously set workspace path

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is open showing workspace at c:/dev/project_a
And Workspace at c:/dev/project_b exists with different bot state
When User changes workspace path to c:/dev/project_b
Then Panel displays c:/dev/project_b as current workspace
And Panel displays behavior action state from project_b
And Panel refreshes all sections with project_b data
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is open showing valid workspace
When User changes workspace path to non-existent directory
Then Panel displays error message
And Error message indicates directory not found
And Panel retains previous valid workspace
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is open showing default workspace c:/dev/project_a
When User changes workspace path to c:/dev/project_b
And Panel displays project_b workspace and state
And User refreshes panel
Then Panel displays c:/dev/project_b as current workspace
And Workspace path was persisted and restored
```

