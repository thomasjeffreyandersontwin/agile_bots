# 📄 Display CLI Header

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Render Bot Interface](.)  
**Sequential Order:** 0.0
**Story Type:** system

## Story Description

Display CLI Header functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** CLI displays status
  **then** CLI shows header with bot name
  **and** workspace path

- **When** displaying header in terminal mode
  **then** CLI uses plain text formatting

- **When** displaying header in piped mode
  **then** CLI uses markdown formatting

- **When** header is displayed
  **then** CLI includes separator line after header

## Scenarios

<a id="scenario-cli-displays-cli-status-section-header-when-status-command-is-run"></a>
### Scenario: [CLI displays CLI STATUS section header when status command is run](#scenario-cli-displays-cli-status-section-header-when-status-command-is-run) ()

**Steps:**
```gherkin
Given: CLI is initialized
When: user enters 'status' command
Then: CLI displays CLI STATUS section header
AND: CLI shows section separator line
AND: CLI shows '*** CLI STATUS section ***' header text
AND: CLI shows description text explaining what the section contains
AND: CLI shows warning text: 'You MUST DISPLAY this entire section in your response to the user exactly as you see it'
AND: CLI shows subsection separator
AND: CLI shows section separator after header
```


<a id="scenario-cli-displays-bot-name-with-robot-emoji-in-header"></a>
### Scenario: [CLI displays bot name with robot emoji in header](#scenario-cli-displays-bot-name-with-robot-emoji-in-header) ()

**Steps:**
```gherkin
Given CLI is initialized with story_bot
And CLI is in piped mode
When CLI renders the dashboard header
Then output contains heading with robot emoji and bot name
And output shows Bot: story_bot
```


<a id="scenario-cli-displays-bot-path-in-code-block"></a>
### Scenario: [CLI displays bot path in code block](#scenario-cli-displays-bot-path-in-code-block) ()

**Steps:**
```gherkin
Given CLI is initialized with story_bot at path C:/dev/augmented-teams/agile_bot/bots/story_bot
When CLI renders the dashboard header
Then output contains '**Bot Path:**' label
And output shows code block with three backticks
And output shows the full bot directory path: 'C:\dev\augmented-teams\agile_bot\bots\story_bot'
And output closes code block with three backticks
```


<a id="scenario-cli-displays-workspace-name-and-path"></a>
### Scenario: [CLI displays workspace name and path](#scenario-cli-displays-workspace-name-and-path) ()

**Steps:**
```gherkin
Given CLI is initialized with workspace base_bot
And workspace path is C:/dev/augmented-teams/agile_bot/bots/base_bot
When CLI renders the dashboard header
Then output contains 'Ã°Å¸â€œâ€š **Workspace:** base_bot' with folder emoji
And output shows code block with three backticks
And output shows full workspace path: 'C:\dev\augmented-teams\agile_bot\bots\base_bot'
And output closes code block with three backticks
```


<a id="scenario-cli-displays-path-change-instructions"></a>
### Scenario: [CLI displays path change instructions](#scenario-cli-displays-path-change-instructions) ()

**Steps:**
```gherkin
Given CLI is in piped mode
When CLI renders the dashboard header
Then output contains 'To change path:' label
And output shows code block with three backticks
And output shows path command example: 'path demo/mob_minion              # Change to specific project'
And output shows path command example: 'path ../another_bot               # Change to relative path'
And output closes code block with three backticks
```


<a id="scenario-cli-applies-separator-after-header-section"></a>
### Scenario: [CLI applies separator after header section](#scenario-cli-applies-separator-after-header-section) ()

**Steps:**
```gherkin
Given CLI is in piped mode
When CLI renders the dashboard header
Then output ends with horizontal separator line (subsection separator)
```


<a id="scenario-cli-displays-headless-mode-section-when-configured"></a>
### Scenario: [CLI displays headless mode section when configured](#scenario-cli-displays-headless-mode-section-when-configured) ()

**Steps:**
```gherkin
Given: Headless mode is configured with API key
When: CLI renders status display
Then: CLI displays 'Headless Mode:' label
AND: CLI shows 'Status: Available (configured)'
AND: CLI shows API key prefix
AND: CLI shows Usage section with headless command format
AND: CLI shows Examples section with headless command examples
AND: CLI applies subsection separator after headless section
```


<a id="scenario-cli-displays-active-headless-session-when-running"></a>
### Scenario: [CLI displays active headless session when running](#scenario-cli-displays-active-headless-session-when-running) ()

**Steps:**
```gherkin
Given: Headless mode is configured
AND: Active headless session is running
When: CLI renders status display
Then: CLI displays 'Active Session:' section
AND: CLI shows Session ID
AND: CLI shows session Status (running)
AND: CLI shows Log file path
```


<a id="scenario-cli-displays-headless-mode-unavailable-when-not-configured"></a>
### Scenario: [CLI displays headless mode unavailable when not configured](#scenario-cli-displays-headless-mode-unavailable-when-not-configured) ()

**Steps:**
```gherkin
Given: Headless mode is not configured
When: CLI renders status display
Then: CLI displays 'Headless Mode:' label
AND: CLI shows 'Status: Unavailable (not configured)'
AND: CLI shows configuration instructions
```

