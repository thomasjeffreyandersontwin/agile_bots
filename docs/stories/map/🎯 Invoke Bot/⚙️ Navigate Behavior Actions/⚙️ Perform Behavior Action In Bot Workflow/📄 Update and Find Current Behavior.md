# 📄 Update and Find Current Behavior

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Perform Behavior Action In Bot Workflow](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Update and Find Current Behavior functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-behaviors-current-property-returns-current-behavior"></a>
### Scenario: [Behaviors current property returns current behavior](#scenario-behaviors-current-property-returns-current-behavior) (happy_path)

**Steps:**
```gherkin
Given Behaviors collection with current behavior set
When current property accessed
Then Returns current Behavior object
```


<a id="scenario-behaviors-navigate-to-behavior-updates-current-behavior"></a>
### Scenario: [Behaviors navigate to behavior updates current behavior](#scenario-behaviors-navigate-to-behavior-updates-current-behavior) (happy_path)

**Steps:**
```gherkin
Given Behaviors collection
When navigate_to('discovery') called
Then Current behavior updated to 'discovery'
```


<a id="scenario-behaviors-close-current-marks-behavior-and-action-complete"></a>
### Scenario: [Behaviors close current marks behavior and action complete](#scenario-behaviors-close-current-marks-behavior-and-action-complete) (happy_path)

**Steps:**
```gherkin
Given Behaviors collection with current behavior and current action
When close_current() called
Then Current behavior marked complete and current action closed
```


<a id="scenario-behaviors-execute-current-executes-current-behavior"></a>
### Scenario: [Behaviors execute current executes current behavior](#scenario-behaviors-execute-current-executes-current-behavior) (happy_path)

**Steps:**
```gherkin
Given Behaviors collection with current behavior
When execute_current() called
Then Current behavior's execute() method called
```


<a id="scenario-behavior-can-be-found-by-name-when-it-exists"></a>
### Scenario: [Behavior can be found by name when it exists.](#scenario-behavior-can-be-found-by-name-when-it-exists) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-finding-behavior-by-name-returns-none-when-behavior-doesnt-exist"></a>
### Scenario: [Finding behavior by name returns None when behavior doesn't exist.](#scenario-finding-behavior-by-name-returns-none-when-behavior-doesnt-exist) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-all-behaviors-can-be-iterated"></a>
### Scenario: [All behaviors can be iterated.](#scenario-all-behaviors-can-be-iterated) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-can-check-if-a-behavior-exists"></a>
### Scenario: [Can check if a behavior exists.](#scenario-can-check-if-a-behavior-exists) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-action-can-be-found-by-name-when-it-exists"></a>
### Scenario: [Action can be found by name when it exists.](#scenario-action-can-be-found-by-name-when-it-exists) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-finding-action-by-name-returns-none-when-action-doesnt-exist"></a>
### Scenario: [Finding action by name returns None when action doesn't exist.](#scenario-finding-action-by-name-returns-none-when-action-doesnt-exist) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-action-can-be-found-by-order-when-it-exists"></a>
### Scenario: [Action can be found by order when it exists.](#scenario-action-can-be-found-by-order-when-it-exists) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-all-actions-can-be-iterated"></a>
### Scenario: [All actions can be iterated.](#scenario-all-actions-can-be-iterated) (happy_path)

**Steps:**
```gherkin

```

