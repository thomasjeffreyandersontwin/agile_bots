# 📄 Set scope to selected story node and submit

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L266)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Set scope to selected story node and submit functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-submits-scope-from-panel-to-start-work-on-epic"></a>
### Scenario: [User submits scope from panel to start work on epic](#scenario-user-submits-scope-from-panel-to-start-work-on-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L333)

**Steps:**
```gherkin
Given User has selected epic named Invoke Bot in the panel
And Panel displays all story nodes
When User clicks the Submit button
Then System sends selected epic Invoke Bot to bot for analysis
And System analyzes the epic and its children
And System determines appropriate behavior and action
And System sets bot to build mode
And CLI restores scope to previous state
And Panel preserves current view without changing scope filter
And Panel displays confirmation
```


<a id="scenario-user-submits-scope-via-cli-command"></a>
### Scenario: [User submits scope via CLI command](#scenario-user-submits-scope-via-cli-command) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L275)

**Steps:**
```gherkin
Given User has workspace with story graph
And CLI has current scope state
When User executes scope submit command with epic name Edit Story Map
Then System sends epic Edit Story Map to bot for analysis
And System analyzes the epic and its children
And System determines appropriate behavior and action
And System sets bot to build mode
And CLI restores scope to previous state
And CLI displays confirmation with determined behavior
```


<a id="scenario-bot-processes-scope-submission-at-domain-level"></a>
### Scenario: [Bot processes scope submission at domain level](#scenario-bot-processes-scope-submission-at-domain-level) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L302)

**Steps:**
```gherkin
Given Bot has story graph loaded
And Epic named Filter Scope exists in story graph
When Bot receives scope submission request for Filter Scope
Then Bot analyzes the epic and its children
And Bot determines appropriate behavior based on node state
And Bot sets current behavior to determined behavior
And Bot sets current action to build
And Bot state reflects submission was processed
```


<a id="scenario-bot-determines-shape-behavior-for-empty-epic"></a>
### Scenario: [Bot determines shape behavior for empty epic](#scenario-bot-determines-shape-behavior-for-empty-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L327)

**Steps:**
```gherkin
Given Epic named Product Management has no sub-epics
And Epic has no stories
When Bot analyzes the epic after scope submission
Then Bot determines behavior should be shape
And Bot sets current action to build
And Bot is ready to start shaping work
```


<a id="scenario-bot-determines-shape-behavior-for-empty-sub-epic"></a>
### Scenario: [Bot determines shape behavior for empty sub-epic](#scenario-bot-determines-shape-behavior-for-empty-sub-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L350)

**Steps:**
```gherkin
Given Sub-epic named User Management has no stories
And Sub-epic has no nested sub-epics
When Bot analyzes the sub-epic after scope submission
Then Bot determines behavior should be shape
And Bot sets current action to build
And Bot is ready to start shaping work
```


<a id="scenario-bot-determines-explore-behavior-when-stories-lack-acceptance-criteria"></a>
### Scenario: [Bot determines explore behavior when stories lack acceptance criteria](#scenario-bot-determines-explore-behavior-when-stories-lack-acceptance-criteria) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L373)

**Steps:**
```gherkin
Given Epic named Reporting contains three stories
And All stories have empty acceptance criteria
When Bot analyzes the epic after scope submission
Then Bot determines behavior should be explore
And Bot sets current action to build
And Bot is ready to start exploration work
```


<a id="scenario-bot-determines-scenarios-behavior-when-stories-lack-scenarios"></a>
### Scenario: [Bot determines scenarios behavior when stories lack scenarios](#scenario-bot-determines-scenarios-behavior-when-stories-lack-scenarios) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L396)

**Steps:**
```gherkin
Given Epic named Authentication contains two stories
And All stories have acceptance criteria
And All stories have empty scenarios
When Bot analyzes the epic after scope submission
Then Bot determines behavior should be scenarios
And Bot sets current action to build
And Bot is ready to start scenario writing work
```


<a id="scenario-bot-determines-tests-behavior-when-stories-lack-tests"></a>
### Scenario: [Bot determines tests behavior when stories lack tests](#scenario-bot-determines-tests-behavior-when-stories-lack-tests) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L420)

**Steps:**
```gherkin
Given Epic named Data Export contains two stories
And All stories have scenarios
And All stories have empty test methods
When Bot analyzes the epic after scope submission
Then Bot determines behavior should be tests
And Bot sets current action to build
And Bot is ready to start test writing work
```


<a id="scenario-bot-determines-code-behavior-when-tests-exist-but-fail"></a>
### Scenario: [Bot determines code behavior when tests exist but fail](#scenario-bot-determines-code-behavior-when-tests-exist-but-fail) (happy_path)

**Steps:**
```gherkin
Given Epic named File Upload contains one story
And Story has test methods defined
And Tests are failing
When Bot analyzes the epic after scope submission
Then Bot determines behavior should be code
And Bot sets current action to build
And Bot is ready to start code implementation work
```


<a id="scenario-bot-determines-code-behavior-when-tests-pass-but-code-not-implemented"></a>
### Scenario: [Bot determines code behavior when tests pass but code not implemented](#scenario-bot-determines-code-behavior-when-tests-pass-but-code-not-implemented) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L468)

**Steps:**
```gherkin
Given Epic named Search Feature contains one story
And Story has test methods defined
And Tests pass with mocked implementation
And Production code is not implemented
When Bot analyzes the epic after scope submission
Then Bot determines behavior should be code
And Bot sets current action to build
And Bot is ready to start code implementation work
```


<a id="scenario-user-attempts-to-submit-without-selecting-a-node"></a>
### Scenario: [User attempts to submit without selecting a node](#scenario-user-attempts-to-submit-without-selecting-a-node) (edge_case)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.js#L486)

**Steps:**
```gherkin
Given User has not selected any story node in the panel
When User views the toolbar
Then Submit button is hidden
```


<a id="scenario-submit-button-displays-behavior-specific-icon"></a>
### Scenario: [Submit button displays behavior-specific icon](#scenario-submit-button-displays-behavior-specific-icon) (happy_path)

**Steps:**
```gherkin
Given User has selected a <node_type> in the panel
And Node state indicates <behavior> behavior is needed
When Panel renders the submit button
Then Submit button displays <icon_file> icon indicating <behavior> behavior
```

**Examples:**
| node_type | behavior | icon_file | description |
| --- | --- | --- | --- |
| empty epic | shape | submit_subepic.png | Epic needs structure |
| empty sub-epic | shape | submit_subepic.png | Sub-epic needs structure |
| story without AC | explore | submit_story.png | Story needs exploration |
| story without scenarios | scenarios | submit_ac.png | Story needs scenarios |
| story without tests | tests | submit_tests.png | Story needs tests |
| story with failing tests | code | submit_code.png | Story needs code implementation |

