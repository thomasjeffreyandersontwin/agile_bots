# 📄 Initialize CLI Session

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L72)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Initialize Bot Interface](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Initialize CLI Session functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-session-initializes-bot-all-channels"></a>
### Scenario: [CLI session initializes bot (all channels)](#scenario-cli-session-initializes-bot-all-channels) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L84)

**Steps:**
```gherkin
GIVEN: Bot and workspace configured
WHEN: CLISession is created
THEN: Session wraps bot
```


<a id="scenario-cli-session-loads-existing-state-all-channels"></a>
### Scenario: [CLI session loads existing state (all channels)](#scenario-cli-session-loads-existing-state-all-channels) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L106)

**Steps:**
```gherkin
GIVEN: Bot with saved state
WHEN: CLISession is created
THEN: Bot loads previous state
```


<a id="scenario-cli-session-can-execute-commands-all-channels"></a>
### Scenario: [CLI session can execute commands (all channels)](#scenario-cli-session-can-execute-commands-all-channels) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L129)

**Steps:**
```gherkin
GIVEN: Initialized CLI session
WHEN: Command is executed
THEN: Session returns response
```

