# 📄 Display Instructions In Raw Format

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Display Action Instructions Through Panel](.)  
**Sequential Order:** 7
**Story Type:** user

## Story Description

Display Instructions In Raw Format functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks action instruction in Behavior Action Hierarchy

  **then** System displays entire instructions exactly as it should be sent to the AI chat

## Scenarios

<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays formatted instructions
When User clicks raw format toggle button
Then Panel displays instructions in raw text format
And Instructions show exactly as they would be sent to AI
And Raw format is scrollable
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays instructions in raw format
When User clicks formatted view toggle button
Then Panel displays instructions in formatted view
And Instructions show with sections and styling
```

