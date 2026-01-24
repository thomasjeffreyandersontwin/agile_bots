# 📄 Navigate Sequentially

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L355)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Navigate Behavior And Actions](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Navigate Sequentially functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-botnext-moves-to-next-action"></a>
### Scenario: [bot.next() moves to next action](#scenario-botnext-moves-to-next-action) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L357)

**Steps:**
```gherkin
Given Bot is at clarify action
When bot.next() is called
Then Bot moves to strategy (next action in workflow)
```


<a id="scenario-botnext-progresses-through-workflow-sequence"></a>
### Scenario: [bot.next() progresses through workflow sequence](#scenario-botnext-progresses-through-workflow-sequence) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L379)

**Steps:**
```gherkin
Given Bot is at first action
When bot.next() is called multiple times
Then Bot progresses through clarify -> strategy -> build -> validate -> render
```


<a id="scenario-botnext-at-final-action-advances-to-next-behavior"></a>
### Scenario: [bot.next() at final action advances to next behavior](#scenario-botnext-at-final-action-advances-to-next-behavior) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L404)

**Steps:**
```gherkin
Given Bot is at render (final action of shape)
When bot.next() is called
Then Bot advances to next behavior (discovery) first action (clarify)
```


<a id="scenario-botcurrent-returns-current-action-instructions"></a>
### Scenario: [bot.current() returns current action instructions](#scenario-botcurrent-returns-current-action-instructions) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L431)

**Steps:**
```gherkin
Given Bot is at a specific action
When bot.current() is called
Then Current action instructions object is returned
```


<a id="scenario-botnext-respects-behaviorjson-workflow-sequence"></a>
### Scenario: [bot.next() respects behavior.json workflow sequence](#scenario-botnext-respects-behaviorjson-workflow-sequence) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L458)

**Steps:**
```gherkin
Given Bot is at strategy (second action)
When bot.next() is called
Then Bot moves to build (third action), following behavior.json order
```


<a id="scenario-botnext-with-no-behavior-selected-starts-workflow"></a>
### Scenario: [bot.next() with no behavior selected starts workflow](#scenario-botnext-with-no-behavior-selected-starts-workflow) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L480)

**Steps:**
```gherkin
Given No behavior is selected
When bot.next() is called
Then Bot starts at first behavior (shape), first action (clarify)
Then NOTE: Currently bot.next() returns an error when no behavior is selected.
Then This test documents the DESIRED behavior - bot should be smart enough
Then to start at the beginning of the workflow automatically.
```


<a id="scenario-can-navigate-to-a-specific-behavior"></a>
### Scenario: [Can navigate to a specific behavior](#scenario-can-navigate-to-a-specific-behavior) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L505)

**Steps:**
```gherkin
Given Bot exists with multiple behaviors
When behaviors.navigate_to('discovery') called
Then Current behavior is set to discovery
```


<a id="scenario-next-behavior-in-sequence-can-be-retrieved"></a>
### Scenario: [Next behavior in sequence can be retrieved](#scenario-next-behavior-in-sequence-can-be-retrieved) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L516)

**Steps:**
```gherkin
Given Bot is at scenarios behavior
When behaviors.next() called
Then Returns next behavior (tests) with complete structure
```


<a id="scenario-getting-next-behavior-returns-none-when-at-last-behavior"></a>
### Scenario: [Getting next behavior returns None when at last behavior](#scenario-getting-next-behavior-returns-none-when-at-last-behavior) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L538)

**Steps:**
```gherkin
Given Bot is at last behavior in list
When behaviors.next() called
Then Returns None
```


<a id="scenario-can-navigate-to-a-specific-action"></a>
### Scenario: [Can navigate to a specific action](#scenario-can-navigate-to-a-specific-action) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L552)

**Steps:**
```gherkin
Given Bot is at a behavior with multiple actions
When actions.navigate_to('build') called
Then Current action is set to build
```


<a id="scenario-next-action-in-sequence-can-be-retrieved"></a>
### Scenario: [Next action in sequence can be retrieved](#scenario-next-action-in-sequence-can-be-retrieved) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L564)

**Steps:**
```gherkin
Given Bot is at clarify action (first action)
When actions.next() called
Then Returns strategy action (second action)
```


<a id="scenario-getting-next-action-returns-none-when-at-last-action"></a>
### Scenario: [Getting next action returns None when at last action](#scenario-getting-next-action-returns-none-when-at-last-action) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L579)

**Steps:**
```gherkin
Given Bot is at last action in behavior
When actions.next() called
Then Returns None
```

