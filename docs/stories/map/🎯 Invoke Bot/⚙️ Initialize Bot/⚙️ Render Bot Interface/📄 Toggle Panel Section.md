# 📄 Toggle Panel Section

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Render Bot Interface](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Toggle Panel Section functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks section header

  **then** System expands or collapses section

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is open with behaviors section collapsed
When User clicks behaviors section header
Then Behaviors section expands
And User sees behavior tree content
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is open with instructions section expanded
When User clicks instructions section header
Then Instructions section collapses
And User no longer sees instructions content
```

