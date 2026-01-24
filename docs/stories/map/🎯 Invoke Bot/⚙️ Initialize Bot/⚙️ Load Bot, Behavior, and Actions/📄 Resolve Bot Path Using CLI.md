# 📄 Resolve Bot Path Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L318)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Resolve Bot Path Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-session-resolves-bot-and-workspace-directories"></a>
### Scenario: [CLI session resolves bot and workspace directories](#scenario-cli-session-resolves-bot-and-workspace-directories) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L331)

**Steps:**
```gherkin
GIVEN: CLI session initialized
WHEN: Bot paths accessed via CLI
THEN: Directories resolved correctly
```


<a id="scenario-base-actions-directory-accessible-via-cli-session"></a>
### Scenario: [Base actions directory accessible via CLI session](#scenario-base-actions-directory-accessible-via-cli-session) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L355)

**Steps:**
```gherkin
GIVEN: CLI session initialized
WHEN: base_actions_directory accessed via CLI
THEN: Returns real agile_bots/base_actions path
```


<a id="scenario-python-workspace-root-accessible-via-cli-session"></a>
### Scenario: [Python workspace root accessible via CLI session](#scenario-python-workspace-root-accessible-via-cli-session) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L378)

**Steps:**
```gherkin
GIVEN: CLI session initialized
WHEN: python_workspace_root accessed via CLI
THEN: Returns Python workspace root path
```


<a id="scenario-find_repo_root-method-works-via-cli-session"></a>
### Scenario: [find_repo_root method works via CLI session](#scenario-find_repo_root-method-works-via-cli-session) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py#L401)

**Steps:**
```gherkin
GIVEN: CLI session initialized
WHEN: find_repo_root() called via CLI
THEN: Returns repository root path
```

