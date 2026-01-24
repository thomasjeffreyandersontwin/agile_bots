# 📄 Display Build Instructions Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Build Story Graph](.)  
**Sequential Order:** 7.0
**Story Type:** user

## Story Description

Display Build Instructions Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Current action is build

  **then** System displays knowledge graph section with template path link

  **and** System displays knowledge graph output file link

  **and** System displays knowledge graph directory path

  **and** System displays rules list with clickable rule file links

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.build
When Panel displays instructions section
Then Panel displays knowledge graph template link
And Panel displays knowledge graph output file link
And Panel displays rules list with clickable links
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays build instructions
When User clicks template path link
Then VS Code opens knowledge graph template file in editor
```

