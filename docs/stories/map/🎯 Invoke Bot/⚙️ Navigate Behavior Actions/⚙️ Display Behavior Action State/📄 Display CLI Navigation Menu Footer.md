# 📄 Display CLI Navigation Menu Footer

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Display Behavior Action State](.)  
**Sequential Order:** 3.0
**Story Type:** system

## Story Description

Display CLI Navigation Menu Footer functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** CLI displays status
  **then** CLI shows footer with available commands

- **When** displaying footer
  **then** CLI lists navigation commands
  **and** action commands

- **When** in terminal mode
  **then** CLI uses plain text formatting for footer

- **When** in piped mode
  **then** CLI uses markdown formatting for footer

## Scenarios

<a id="scenario-cli-displays-commands-menu-footer"></a>
### Scenario: [CLI displays commands menu footer](#scenario-cli-displays-commands-menu-footer) ()

**Steps:**
```gherkin
Given: CLI displays status
When: CLI renders commands menu footer
Then: CLI displays Commands section header
AND: CLI shows command list: status | back | current | next | path [dir] | scope [filter] | headless "msg" | help | exit
AND: CLI shows command usage example with echo syntax
AND: CLI shows behaviors list: shape | prioritization | discovery | exploration | scenarios | tests | code
AND: CLI shows actions list: clarify | strategy | build | validate | render
AND: CLI applies section separator after footer
```

