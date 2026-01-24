# 📄 Launch CLI in Interactive Mode

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Initialize Bot Interface](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Launch CLI in Interactive Mode functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-launches-in-interactive-mode"></a>
### Scenario: [CLI launches in interactive mode](#scenario-cli-launches-in-interactive-mode) ()

**Steps:**
```gherkin
GIVEN: CLISession is configured for interactive mode (TTY detected)
WHEN: user runs CLI
THEN: CLISession wraps Bot
AND: CLI can execute commands
AND: CLI uses TTY adapters for output
```


<a id="scenario-cli-loads-existing-behavior-action-state-on-launch"></a>
### Scenario: [CLI loads existing behavior action state on launch](#scenario-cli-loads-existing-behavior-action-state-on-launch) ()

**Steps:**
```gherkin
GIVEN: CLISession is configured for interactive mode
AND: behavior action state file exists
WHEN: user runs CLI
THEN: Bot loads stored behavior action state
```


<a id="scenario-cli-displays-status-on-launch"></a>
### Scenario: [CLI displays status on launch](#scenario-cli-displays-status-on-launch) ()

**Steps:**
```gherkin
GIVEN: CLISession is initialized in interactive mode
WHEN: user executes 'status' command
THEN: CLI displays complete status output with all required sections in correct order
AND: Output format matches TTY adapter format (hard-coded expectations)
```


<a id="scenario-cli-displays-header-section"></a>
### Scenario: [CLI displays header section](#scenario-cli-displays-header-section) ()

**Steps:**
```gherkin
GIVEN: CLISession is initialized
WHEN: user executes 'status' command
THEN: CLI displays header section with exact format
AND: Header includes separator lines, centered bold text, description, and warning
```


<a id="scenario-cli-displays-bot-section"></a>
### Scenario: [CLI displays bot section](#scenario-cli-displays-bot-section) ()

**Steps:**
```gherkin
GIVEN: CLISession is initialized
WHEN: user executes 'status' command
THEN: CLI displays bot section with exact format
AND: Bot section includes bot name, bot path, workspace path, and change path instructions
```

