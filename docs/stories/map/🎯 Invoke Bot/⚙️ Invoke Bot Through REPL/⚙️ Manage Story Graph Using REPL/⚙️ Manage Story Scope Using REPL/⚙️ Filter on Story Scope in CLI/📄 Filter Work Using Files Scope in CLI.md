# 📄 Filter Work Using Files Scope in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Manage Story Graph Using REPL](../..) / [⚙️ Manage Story Scope Using REPL](..) / [⚙️ Filter on Story Scope in CLI](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Filter Work Using Files Scope in CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user sets files scope filter
  **then** CLI displays active scope filters

- **When** user executes validate with active files scope
  **then** CLI displays validation filtered to matched files

- **When** user provides glob pattern for files
  **then** CLI matches files using glob pattern

- **When** user clears files scope
  **then** CLI removes files filter
  **and** displays unfiltered content

## Scenarios

<a id="scenario-user-sets-files-scope-filter"></a>
### Scenario: [User sets files scope filter](#scenario-user-sets-files-scope-filter) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at code.validate.instructions
WHEN: user enters 'scope files="src/**/*.py"'
THEN: CLIScope parses files scope string
AND: REPLSession stores files filter in context
AND: CLI displays active scope filters
```


<a id="scenario-user-executes-validate-with-active-files-scope"></a>
### Scenario: [User executes validate with active files scope](#scenario-user-executes-validate-with-active-files-scope) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at code.validate.instructions
AND: active scope filter is files="src/**/*.py"
WHEN: user enters 'code.validate.instructions'
THEN: CLIAction passes files filter to action.get_instructions()
AND: CLI displays validation filtered to matched files
```

