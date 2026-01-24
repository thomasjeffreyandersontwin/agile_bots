# 📄 Display Help Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L273)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Get Help](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Display Help Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-help-command-shows-available-commands-all-channels"></a>
### Scenario: [Help command shows available commands (all channels)](#scenario-help-command-shows-available-commands-all-channels) (happy_path)  | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L285)

**Steps:**
```gherkin
GIVEN: CLI session active
WHEN: user enters 'help'
THEN: CLI displays list of available commands
```


<a id="scenario-help-with-command-name-shows-command-details-all-channels"></a>
### Scenario: [Help with command name shows command details (all channels)](#scenario-help-with-command-name-shows-command-details-all-channels) (happy_path)  | [Test](/test/invoke_bot/get_help/test_get_help_using_cli.py#L308)

**Steps:**
```gherkin
GIVEN: CLI session active
WHEN: user enters 'help status'
THEN: CLI displays help for 'status' command
```

