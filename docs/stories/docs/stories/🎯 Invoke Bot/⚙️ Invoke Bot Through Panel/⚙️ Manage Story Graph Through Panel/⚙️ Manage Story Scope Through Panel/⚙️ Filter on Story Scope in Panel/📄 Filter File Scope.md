# 📄 Filter File Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through Panel](..) / [⚙️ Manage Story Graph Through Panel](../..) / [⚙️ Manage Story Scope Through Panel](..) / [⚙️ Filter on Story Scope in Panel](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Filter File Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User types file pattern in filter

  **then** System displays filtered file list

  **and** System displays file list with monospace paths

## Scenarios

<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays scope section
When User types file:src/**/*.py in scope filter
Then Panel displays file scope mode
And Panel displays list of Python files in src directory
And File paths are displayed in monospace font
```


<a id="scenario-unnamed-scenario"></a>
### Scenario: [Unnamed Scenario](#scenario-unnamed-scenario) (happy_path)

**Steps:**
```gherkin
Given Panel displays scope section
When User types file:**/*.spec.js in scope filter
Then Panel displays all JavaScript test files
And Files are displayed with full relative paths
```

