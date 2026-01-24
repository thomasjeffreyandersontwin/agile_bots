# 📄 Open Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Initialize Bot Interface](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Open Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User activates panel command

  **then** System displays bot name

  **and** System displays workspace path

  **and** System displays bot path

  **and** System displays available botss

  **and** System displays behavior action section

  **and** System displays scope section

  **and** System displays instructions section

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given VS Code workspace with bot installed
When User executes 'Open Status Panel' command
Then Panel webview appears
And Panel displays bot name
And Panel displays workspace path
And Panel displays behavior action section
And Panel displays scope section
And Panel displays instructions section
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is already open in VS Code
When User executes 'Open Status Panel' command again
Then Existing panel is brought to front
And No duplicate panel is created
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given VS Code workspace with no bots installed
When User executes 'Open Status Panel' command
Then Panel displays error message
And Error message indicates no bots found
```

