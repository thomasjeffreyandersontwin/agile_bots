# 📄 Navigate Behavior Action Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.js#L422)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Navigate Behavior And Actions](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Navigate Behavior Action Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks back button

  **then** System  sets previous action as current

  **and** System displays previous action in-progress indicator

  **and** System reruns previous action details

- **When** User clicks next button

  **then** System sets next action as current

  **and** System displays next action in-progress indicator

  **and** System reruns next action details

- **When** User clicks current button

  **then** System reruns current action details

- **When** User is on the last operation of an action

  **then** System moves to the next action and selects its first operation

- **When** User is on the last action of a behavior

  **then** System moves to the next behavior and selects its first action and first operation

- **When** User is on the last behavior of a bot

  **then** System disables next behavior navigation

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays behavior hierarchy
And Bot is at shape.clarify
When User clicks on discovery.build action link
Then Bot navigates to discovery.build
And Panel refreshes to show new current position
And discovery.build is highlighted as current action
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.clarify
When User clicks next button
Then Bot navigates to shape.strategy
And Panel displays shape.strategy as current
And Panel displays shape.strategy in-progress indicator
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.strategy
When User clicks back button
Then Bot navigates to shape.clarify
And Panel displays shape.clarify as current
And Panel displays shape.clarify in-progress indicator
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at last action of last behavior
When User views next button
Then Next button is disabled
```

