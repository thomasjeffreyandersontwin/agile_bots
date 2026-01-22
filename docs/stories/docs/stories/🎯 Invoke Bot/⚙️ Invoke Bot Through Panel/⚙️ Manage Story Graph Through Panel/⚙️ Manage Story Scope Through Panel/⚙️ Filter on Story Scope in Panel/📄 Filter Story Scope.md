# 📄 Filter Story Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Manage Story Graph Through Panel](../..) / [⚙️ Manage Story Scope Through Panel](..) / [⚙️ Filter on Story Scope in Panel](.)  
**Sequential Order:** 1
**Story Type:** user

## Story Description

Filter Story Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User types story name in filter

  **then** System refreshes story hierarchy based on new story scope

- **When** Filter matches epic

  **then** System displays epic with all sub-epics and stories collapsed beneath it

- **When** Filter matches sub-epic

  **then** System displays sub-epic with all stories collapsed beneath it

- **When** Filter matches story

  **then** System displays that story with its acceptance criteria

- **When** User clicks story with acceptance criteria

  **then** System expands story showing acceptance criteria list

- **When** Filter matches multiple items

  **then** System displays all matches in hierarchical format preserving parent-child relationships

- **When** User clicks clear filter button

  **then** System displays all stories

- **When** User sets scope filter

  **then** System persists scope filter value

- **When** Panel refreshes

  **then** System restores previously set scope filter

## Scenarios

<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays scope section with full story hierarchy
When User types Open Panel in scope filter
Then Panel displays filtered hierarchy showing Open Panel story
And Panel displays Open Panel parent sub-epic (Manage Panel Session)
And Panel displays parent epic (Invoke Bot Through Panel)
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays full story hierarchy
When User types Invoke Bot in scope filter
Then Panel displays Invoke Bot epic
And Panel displays all sub-epics under Invoke Bot
And Sub-epics are initially collapsed
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays filtered scope showing only Open Panel story
When User clicks clear filter button
Then Panel displays all stories in full hierarchy
And All epics are visible
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel is open
When User types Open Panel in scope filter
And Panel displays filtered hierarchy
And User refreshes panel
Then Panel displays same filtered hierarchy
And Scope filter input shows Open Panel
And Filter value was persisted and restored
```

