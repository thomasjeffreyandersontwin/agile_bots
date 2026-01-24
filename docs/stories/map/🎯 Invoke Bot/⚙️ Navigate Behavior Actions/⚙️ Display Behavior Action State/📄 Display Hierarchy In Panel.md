# 📄 Display Hierarchy In Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Display Behavior Action State](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Display Hierarchy In Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User views panel

  **then** System displays behavior list with actions

- **When** Action is current

  **then** System displays current action in-progress indicator

- **When** Action is completed

  **then** System displays completed indicator

- **When** Action is pending

  **then** System displays pending indicator

- **When** User clicks collapsed behavior

  **then** System expands behavior showing actions

- **When** User clicks expanded behavior

  **then** System collapses behavior hiding actions

- **When** User clicks collapsed action

  **then** System expands action showing operations

- **When** User clicks expanded action

  **then** System collapses action hiding operations

- **When** User views behavior list

  **then** System displays all behaviors expandable regardless of current position

- **When** User views behavior list

  **then** System displays behaviors in correct sequential order

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot has multiple behaviors with completed and pending actions
And Bot is currently at shape.clarify
When Panel renders hierarchy section
Then User sees behavior names (shape, discovery)
And User sees action names under behaviors
And Current action (clarify) shows in-progress indicator
And Completed actions show checkmark indicator
And Pending actions show empty indicator
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays collapsed behavior tree
When User clicks collapsed shape behavior
Then Shape behavior expands showing actions (clarify, strategy)
When User clicks expanded shape behavior again
Then Shape behavior collapses hiding actions
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Shape behavior is expanded showing actions
And Clarify action is collapsed
When User clicks collapsed clarify action
Then Clarify action expands showing operations (instructions, execute, confirm)
When User clicks expanded clarify action again
Then Clarify action collapses hiding operations
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays behavior tree
And Bot is currently at shape.clarify
When User clicks collapsed discovery behavior
Then Discovery behavior expands showing actions
And Discovery actions are visible even though bot is at shape
When User clicks collapsed scenarios behavior
Then Scenarios behavior expands showing actions
And Scenarios actions are visible even though bot is at shape
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot has behaviors with defined sequential order
When Panel renders behavior tree
Then Behaviors appear in order (shape, prioritization, discovery, exploration, scenarios, tests, code)
And Actions under each behavior appear in their configured order
And Order matches behavior configuration JSON
```

