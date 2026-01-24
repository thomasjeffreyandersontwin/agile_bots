# 📄 Resolve Bot Path

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L23)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Resolve Bot Path functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-botpath-resolves-directories-from-environment-variables"></a>
### Scenario: [BotPath resolves directories from environment variables](#scenario-botpath-resolves-directories-from-environment-variables) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L25)

**Steps:**
```gherkin
Given BOT_DIRECTORY and WORKING_AREA environment variables set
When BotPath accessed from bot
Then Both directory properties return paths from environment
```


<a id="scenario-botpathbase_actions_directory-returns-real-agile_bot-base_actions"></a>
### Scenario: [BotPath.base_actions_directory returns real agile_bot base_actions](#scenario-botpathbase_actions_directory-returns-real-agile_bot-base_actions) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L43)

**Steps:**
```gherkin
Given BotPath instantiated
When base_actions_directory property accessed
Then Returns real agile_bot/base_actions path (not test directory)
Then Note: base_actions_directory always returns the real agile_bot/base_actions path,
Then not the test directory. This is by design - see get_base_actions_directory() in workspace.py.
```


<a id="scenario-botpathpython_workspace_root-property-returns-python-workspace-root"></a>
### Scenario: [BotPath.python_workspace_root property returns Python workspace root.](#scenario-botpathpython_workspace_root-property-returns-python-workspace-root) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L60)

**Steps:**
```gherkin

```


<a id="scenario-botpathfind_repo_root-method-returns-repository-root"></a>
### Scenario: [BotPath.find_repo_root() method returns repository root.](#scenario-botpathfind_repo_root-method-returns-repository-root) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L68)

**Steps:**
```gherkin

```


<a id="scenario-botpath-raises-error-when-environment-variables-not-set"></a>
### Scenario: [BotPath raises error when environment variables not set](#scenario-botpath-raises-error-when-environment-variables-not-set) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L79)

**Steps:**
```gherkin
Given No BOT_DIRECTORY or WORKING_AREA environment variables
When BotPath instantiated
Then Raises RuntimeError
```

