# 📄 Display Validate Instructions

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Display Action Instructions Through Panel](.)  
**Sequential Order:** 5
**Story Type:** user

## Story Description

Display Validate Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Current action is validate

  **then** System displays rules list

- **When** User clicks rule file link

  **then** System opens rule file in editor

## Scenarios

<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Bot is at shape.validate
When Panel displays instructions section
Then Panel displays validation rules list
And Each rule has clickable file link
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays validate instructions with rules
When User clicks rule file link
Then VS Code opens validation rule file in editor
```

