# 📄 Set scope to selected story node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L214)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 7.0
**Story Type:** user

## Story Description

Set scope to selected story node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-sets-scope-to-selected-epic"></a>
### Scenario: [User sets scope to selected epic](#scenario-user-sets-scope-to-selected-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L216)

**Steps:**
```gherkin
Given User has selected an epic named Invoke Bot in the panel
When User clicks the Scope To button
Then System sets scope filter to Invoke Bot
And System refreshes the panel view
And Panel displays only story nodes matching Invoke Bot
```


<a id="scenario-user-sets-scope-to-selected-sub-epic"></a>
### Scenario: [User sets scope to selected sub-epic](#scenario-user-sets-scope-to-selected-sub-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L245)

**Steps:**
```gherkin
Given User has selected a sub-epic named Edit Story Map in the panel
When User clicks the Scope To button
Then System sets scope filter to Edit Story Map
And System refreshes the panel view
And Panel displays only story nodes matching Edit Story Map
```


<a id="scenario-user-sets-scope-to-selected-story"></a>
### Scenario: [User sets scope to selected story](#scenario-user-sets-scope-to-selected-story) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L270)

**Steps:**
```gherkin
Given User has selected a story named Display Story Hierarchy Panel in the panel
When User clicks the Scope To button
Then System sets scope filter to Display Story Hierarchy Panel
And System refreshes the panel view
And Panel displays only story nodes matching Display Story Hierarchy Panel
```


<a id="scenario-user-attempts-to-set-scope-without-selecting-a-node"></a>
### Scenario: [User attempts to set scope without selecting a node](#scenario-user-attempts-to-set-scope-without-selecting-a-node) (edge_case)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L295)

**Steps:**
```gherkin
Given User has not selected any story node in the panel
When User views the toolbar
Then Scope To button is hidden
```

