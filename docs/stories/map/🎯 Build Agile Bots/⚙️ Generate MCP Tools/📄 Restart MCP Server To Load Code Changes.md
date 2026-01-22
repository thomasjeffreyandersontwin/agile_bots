# 📄 Restart MCP Server To Load Code Changes

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** MCP Server Generator
**Path:** [🎯 Build Agile Bots](../..) / [⚙️ Generate MCP Tools](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Restart MCP Server To Load Code Changes functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot code changes are detected

  **then** MCP Server clears Python bytecode cache (__pycache__)

  **and** MCP Server restarts to load new code

  **and** Server restarts gracefully without losing state

  **and** Server re-registers with MCP Protocol Handler after restart

## Scenarios

<a id="scenario-clear-python-bytecode-cache"></a>
### Scenario: [Clear Python bytecode cache](#scenario-clear-python-bytecode-cache) ()

**Steps:**
```gherkin
Given __pycache__ directories exist with .pyc files
When clear_python_cache is called
Then All __pycache__ directories are removed
And All .pyc files are deleted
And Cache is cleared before server restart
```

