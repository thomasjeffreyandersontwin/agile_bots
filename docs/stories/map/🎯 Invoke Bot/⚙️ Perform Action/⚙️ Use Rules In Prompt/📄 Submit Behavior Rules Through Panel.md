# 📄 Submit Behavior Rules Through Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Use Rules In Prompt](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Submit Behavior Rules Through Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks Get Rules button for a behavior

  **then** System executes behavior.rules command

  **and** System submits rules digest to AI chat

  **and** Rules include formatted descriptions with DO/DON'T sections

  **and** Rules include file paths for each rule

  **and** All behavior rules are included in digest

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays behavior hierarchy
And Behavior has rules defined
When User clicks Get Rules button for behavior
Then System executes behavior.rules command via CLI
And System submits formatted rules digest to AI chat
And Rules digest includes descriptions, priorities, DO/DON'T sections
And Rules digest includes file paths for each rule
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays behavior hierarchy
And Behavior has rules defined
When User views behavior in hierarchy
Then Get Rules button is visible next to behavior name
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays behavior hierarchy
When User clicks Get Rules button
And Rules are successfully submitted to chat
Then System displays success confirmation message
And Message indicates rules were submitted to chat
```

