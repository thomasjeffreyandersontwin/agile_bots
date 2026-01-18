# 📄 Display Base Instructions

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Display Action Instructions Through Panel](.)  
**Sequential Order:** 1
**Story Type:** user

## Story Description

Display Base Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User views panel

  **then** System displays base instructions section

  **and** System displays behavior name

  **and** System displays action name

## Scenarios

<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Bot is at shape.clarify
When Panel displays instructions section
Then Panel displays base instructions
And Panel displays behavior name (shape)
And Panel displays action name (clarify)
And Instructions are scrollable
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays base instructions
When User clicks copy button
Then Instructions are copied to clipboard
And Panel displays confirmation message
```

