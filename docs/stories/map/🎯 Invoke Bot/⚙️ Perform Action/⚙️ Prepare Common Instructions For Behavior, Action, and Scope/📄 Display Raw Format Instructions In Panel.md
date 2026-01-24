# 📄 Display Raw Format Instructions In Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Prepare Common Instructions For Behavior, Action, and Scope](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Display Raw Format Instructions In Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks action instruction in Behavior Action Hierarchy

  **then** System displays entire instructions exactly as it should be sent to the AI chat

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays formatted instructions
When User clicks raw format toggle button
Then Panel displays instructions in raw text format
And Instructions show exactly as they would be sent to AI
And Raw format is scrollable
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays instructions in raw format
When User clicks formatted view toggle button
Then Panel displays instructions in formatted view
And Instructions show with sections and styling
```

