# 📄 Display Story Hierarchy Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Edit Story Map](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Display Story Hierarchy Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User views story scope

  **then** System displays epic list collapsed

- **When** User clicks collapsed epic expand icon

  **and** epic has sub-epics

  **then** System expands epic showing sub-epics collapsed beneath it

- **When** User clicks epic name

  **and** matching epic folder exists

  **then** System opens epic folder in IDE explorer

- **When** Epic has test file

  **then** System displays test tube icon next to epic name

- **When** User clicks epic test link

  **then** System opens test file in editor

- **When** User clicks collapsed sub-epic expand icon

  **and** matching sub-epic has stories

  **then** System expands sub-epic showing stories collapsed beneath it

- **When** Sub-epic has test file

  **then** System displays test tube icon next to sub-epic name

- **When** User clicks sub-epic test link

  **then** System opens test file in editor

- **When** User clicks sub-epic name

  **then** System opens sub-epic folder in IDE explorer

- **When** User clicks collapsed story expand icon

  **and** matching sub-epic has stories

  **then** System expands story showing scenarios collapsed beneath it

- **When** User clicks story name

  **then** System opens story markdown file in editor

- **When** Story has test file

  **then** System displays test tube icon next to story name

- **When** User clicks story test link

  **then** System opens test file at test class

- **When** User clicks collapsed story expand icon

  **then** System expands story showing scenarios

- **When** User clicks scenario name

  **then** System opens story markdown file at scenario anchor

- **When** Scenario has test method

  **then** System displays test tube icon next to scenario name

- **When** User clicks scenario test link

  **then** System opens test file at scenario test method line

- **When** Test tube icon is displayed

  **then** System shows correct test tube image

- **When** User clicks epic or sub-epic or story name

  **then** System opens corresponding file or folder

## Scenarios

<a id="scenario-display-nested-epic-and-story-hierarchy"></a>
### Scenario: [Display nested epic and story hierarchy](#scenario-display-nested-epic-and-story-hierarchy) (happy_path)

**Steps:**
```gherkin
Given Story graph has epics with nested sub-epics
When User views scope section
Then Panel displays epic names (Invoke Bot)
When User expands Invoke Bot epic
Then Panel displays sub-epics (Invoke Bot Through Panel, Invoke Bot Through REPL)
When User expands Invoke Bot Through Panel sub-epic
Then Panel displays nested sub-epics (Manage Panel Session, Navigate Behaviors)
When User expands Manage Panel Session sub-epic
Then Panel displays stories (Open Panel, Display Session Status)
```


<a id="scenario-open-test-file-at-story-test-class"></a>
### Scenario: [Open test file at story test class](#scenario-open-test-file-at-story-test-class) (happy_path)

**Steps:**
```gherkin
Given Story has test link displayed
And Test file is test_manage_panel_session.spec.js
And Test class is TestOpenPanel
When User clicks test link for Open Panel story
Then VS Code opens test_manage_panel_session.spec.js file
And Editor scrolls to TestOpenPanel class
```


<a id="scenario-open-story-markdown-from-story-link"></a>
### Scenario: [Open story markdown from story link](#scenario-open-story-markdown-from-story-link) (happy_path)

**Steps:**
```gherkin
Given Story has story file link displayed
And Story file is Open Panel.md
When User clicks story link for Open Panel
Then VS Code opens Open Panel.md file in editor
```


<a id="scenario-display-error-for-missing-test-file"></a>
### Scenario: [Display error for missing test file](#scenario-display-error-for-missing-test-file) (error_path)

**Steps:**
```gherkin
Given Story has test link displayed
And Test file does not exist
When User clicks test link
Then Panel displays error message
And Error message indicates file not found
```


<a id="scenario-display-test-tube-icons-for-all-node-types"></a>
### Scenario: [Display test tube icons for all node types](#scenario-display-test-tube-icons-for-all-node-types) (happy_path)

**Steps:**
```gherkin
Given Epic has test file
And Sub-epic has test file
And Story has test class
And Scenario has test method
When Panel renders scope hierarchy
Then Test tube icon appears next to epic name
And Test tube icon appears next to sub-epic name
And Test tube icon appears next to story name
And Test tube icon appears next to scenario name
And All test tube icons show correct test_tube.png image
And Test tube icons are large enough to see clearly
```


<a id="scenario-reveal-epic-and-sub-epic-folders-in-explorer"></a>
### Scenario: [Reveal epic and sub-epic folders in explorer](#scenario-reveal-epic-and-sub-epic-folders-in-explorer) (happy_path)

**Steps:**
```gherkin
Given Panel displays scope hierarchy with epics and sub-epics
When User clicks epic name
Then VS Code reveals epic folder in explorer
When User clicks sub-epic name
Then VS Code reveals sub-epic folder in explorer
```


<a id="scenario-open-story-markdown-from-hierarchy"></a>
### Scenario: [Open story markdown from hierarchy](#scenario-open-story-markdown-from-hierarchy) (happy_path)

**Steps:**
```gherkin
Given Panel displays scope hierarchy with stories
And Story has matching markdown file
When User clicks story name
Then VS Code opens story markdown file in editor
```


<a id="scenario-open-test-file-at-scenario-test-method"></a>
### Scenario: [Open test file at scenario test method](#scenario-open-test-file-at-scenario-test-method) (happy_path)

**Steps:**
```gherkin
Given Story has scenarios with test methods
And Scenario test method is at line 145 in test file
When User clicks scenario test tube icon
Then VS Code opens test file
And Editor scrolls to line 145
And Test method definition is visible at cursor
```


<a id="scenario-scroll-to-scenario-anchor-in-story-file"></a>
### Scenario: [Scroll to scenario anchor in story file](#scenario-scroll-to-scenario-anchor-in-story-file) (happy_path)

**Steps:**
```gherkin
Given Story markdown file has scenario sections with anchors
And Scenario is named User expands collapsed section
When User clicks scenario name in panel
Then VS Code opens story markdown file
And Editor scrolls to scenario anchor
And Scenario section is visible with heading
```


<a id="scenario-reveal-folders-in-explorer-from-name-links"></a>
### Scenario: [Reveal folders in explorer from name links](#scenario-reveal-folders-in-explorer-from-name-links) (happy_path)

**Steps:**
```gherkin
Given Epic has matching folder in docs/stories/map
And Sub-epic has matching folder
When User clicks epic name link
Then VS Code reveals folder in explorer view
When User clicks sub-epic name link
Then VS Code reveals sub-epic folder in explorer view
```

