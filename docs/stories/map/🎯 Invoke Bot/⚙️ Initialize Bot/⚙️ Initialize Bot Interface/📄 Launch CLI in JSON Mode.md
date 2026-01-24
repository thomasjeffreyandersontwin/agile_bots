# 📄 Launch CLI in JSON Mode

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Web View, API Client
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Initialize Bot Interface](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Launch CLI in JSON Mode functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-launches-in-json-mode"></a>
### Scenario: [CLI launches in JSON mode](#scenario-cli-launches-in-json-mode) ()

**Steps:**
```gherkin
GIVEN: CLISession is configured for JSON mode (mode='json' set explicitly)
WHEN: commands are executed
THEN: CLISession creates session
AND: CLI can execute commands in JSON mode
AND: CLI uses JSON adapters for output
```


<a id="scenario-cli-displays-status-in-json-format"></a>
### Scenario: [CLI displays status in JSON format](#scenario-cli-displays-status-in-json-format) ()

**Steps:**
```gherkin
GIVEN: CLISession is initialized in JSON mode
WHEN: user executes 'status' command
THEN: CLI displays complete status output in JSON format
AND: Output is valid JSON with required fields (name, bot_directory, workspace_directory, behavior_names, current_behavior)
```


<a id="scenario-cli-displays-header-section-in-json"></a>
### Scenario: [CLI displays header section in JSON](#scenario-cli-displays-header-section-in-json) ()

**Steps:**
```gherkin
GIVEN: CLISession is initialized in JSON mode
WHEN: user executes 'status' command
THEN: CLI displays header section with JSON structure
AND: Output is valid JSON dictionary
```


<a id="scenario-cli-displays-bot-section-in-json"></a>
### Scenario: [CLI displays bot section in JSON](#scenario-cli-displays-bot-section-in-json) ()

**Steps:**
```gherkin
GIVEN: CLISession is initialized in JSON mode
WHEN: user executes 'status' command
THEN: CLI displays bot section with JSON structure
AND: JSON includes bot name and directory fields
```

