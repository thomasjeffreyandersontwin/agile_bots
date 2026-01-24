# 📄 Switch Bot panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Switch Bot panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User switches bot

  **then** System displays updated bot name

  **and** System displays behavior action section for new bot

  **and** System displays behavior action stateof workspace for new bot

## Scenarios

<a id="scenario-panel-shows-story_bot-and-multiple-bots-available"></a>
### Scenario: [Panel shows story_bot and multiple bots available](#scenario-panel-shows-story_bot-and-multiple-bots-available) (happy_path)

**Steps:**
```gherkin
Given Panel is open showing story_bot
And Multiple bots are available (story_bot, crc_bot)
When User selects crc_bot from bot selector dropdown
Then Panel displays crc_bot as current bot
And Panel displays crc_bot's behaviors
And Panel displays crc_bot's current action
And Panel refreshes all sections with crc_bot data
```


<a id="scenario-user-switches-to-crc_bot"></a>
### Scenario: [User switches to crc_bot](#scenario-user-switches-to-crc_bot) (happy_path)

**Steps:**
```gherkin
Given Panel is open with story_bot at workspace c:/dev/project_a
When User switches to crc_bot
Then Panel displays crc_bot
And Panel retains workspace c:/dev/project_a
And Panel displays crc_bot state for that workspace
```

