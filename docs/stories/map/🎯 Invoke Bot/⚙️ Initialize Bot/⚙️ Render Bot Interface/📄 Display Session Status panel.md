# 📄 Display Session Status panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Render Bot Interface](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Display Session Status panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks refresh button

  **then** System displays bot name

  **and** System displays updated workspace path

  **and** System displays updated bot path

  **and** System displays updated available botss

  **and** System displays updated behavior action section

  **and** System displays updated scope section

  **and** System displays updated instructions section

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel is open displaying current bot status
And Bot state has changed since panel was opened
When User clicks refresh button
Then Panel displays updated bot name
And Panel displays updated workspace path
And Panel displays updated behavior action section
And Panel displays updated scope
And Panel displays updated instructions
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at behavior shape and action clarify
When Panel opens
Then Panel displays current bot name
And Panel displays current workspace path
And Panel displays shape.clarify as current action
```

