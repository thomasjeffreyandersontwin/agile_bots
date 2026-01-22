# 📄 Persist Story Graph Changes

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Story Graph
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Domain](..) / [⚙️ Edit Story Graph](.)  
**Sequential Order:** 6.0
**Story Type:** user

## Story Description

Persist Story Graph Changes functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Story Graph structure is modified
  **then** Story Graph validates graph structure integrity
  **and** Story Graph persists changes to storage
  **and** Story Graph updates version metadata

- **When** Story Graph persists changes successfully
  **then** Story Graph writes updated graph to file
  **and** Story Graph verifies write successful

- **When** Story Graph persistence fails
  **then** Story Graph identifies write failure
  **and** Story Graph rolls back in-memory changes
  **and** returns error with failure details

- **When** Story Graph validates structure after modification
  **then** Story Graph checks all node references valid
  **and** Story Graph checks sequential order consistency

- **When** Story Graph identifies structure violations
  **then** Story Graph identifies violation details
  **and** Story Graph prevents persistence
  **and** returns error with violation specifics

## Scenarios

<a id="scenario-persist-valid-graph-modifications-successfully"></a>
### Scenario: [Persist valid graph modifications successfully](#scenario-persist-valid-graph-modifications-successfully) (happy_path)

**Steps:**
```gherkin
Given Story Graph is initialized
And Story Graph file is at "docs/stories/story-graph.json"
Given Story Graph has <initial_node_count> nodes
When Story Graph is modified with <modification_type>: <modification_details>
Then Story Graph validates structure integrity
And Story Graph persists changes to file
And file write is verified successful
And version metadata is updated
And persisted graph has <final_node_count> nodes
```

**Examples:**
| modification_type | modification_details | initial_node_count | final_node_count |
| --- | --- | --- | --- |
| add_node | Add SubEpic 'OAuth Flow' to Epic 'Authentication' | 50 | 51 |
| delete_node | Delete SubEpic 'Deprecated Feature' | 50 | 49 |
| move_node | Move SubEpic 'Login Flow' from Epic A to Epic B | 50 | 50 |
| rename_node | Rename Story 'User Login' to 'User Authentication' | 50 | 50 |


<a id="scenario-validate-structure-integrity-before-persistence"></a>
### Scenario: [Validate structure integrity before persistence](#scenario-validate-structure-integrity-before-persistence) (happy_path)

**Steps:**
```gherkin
Given Story Graph is initialized
Given Story Graph has valid structure with <node_count> nodes
When Story Graph is modified with <modification>
Then Story Graph validates all node references are valid
And Story Graph validates sequential order consistency
And Story Graph validates parent-child relationships
And validation result is: <validation_result>
```

**Examples:**
| node_count | modification | validation_result |
| --- | --- | --- |
| 50 | Add new Epic with valid structure | valid |
| 50 | Update existing node name to unique value | valid |
| 50 | Move node to valid parent | valid |


<a id="scenario-detect-structure-violations-and-prevent-persistence"></a>
### Scenario: [Detect structure violations and prevent persistence](#scenario-detect-structure-violations-and-prevent-persistence) (error_case)

**Steps:**
```gherkin
Given Story Graph is initialized
Given Story Graph has valid structure
When Story Graph is modified to create <violation_type>
Then Story Graph validates structure
And identifies violation: <violation_details>
And prevents persistence
And returns error "<error_message>"
And in-memory changes are rolled back
```

**Examples:**
| violation_type | violation_details | error_message |
| --- | --- | --- |
| invalid_reference | Node references non-existent parent | Structure violation: Invalid parent reference |
| duplicate_position | Two nodes have same sequential_order | Structure violation: Duplicate sequential order |
| broken_hierarchy | Story placed directly under Epic (missing SubEpic) | Structure violation: Invalid hierarchy - Story must be under SubEpic |
| circular_reference | Node is ancestor of itself | Structure violation: Circular reference detected |


<a id="scenario-handle-persistence-failures-and-rollback-changes"></a>
### Scenario: [Handle persistence failures and rollback changes](#scenario-handle-persistence-failures-and-rollback-changes) (error_case)

**Steps:**
```gherkin
Given Story Graph is initialized
And Story Graph file is at "docs/stories/story-graph.json"
Given Story Graph has valid structure with state: <initial_state>
And file write will fail with error: <write_error>
When Story Graph attempts to persist modifications
Then Story Graph identifies write failure
And rolls back in-memory changes to state: <initial_state>
And returns error "Persistence failed: <write_error>"
And Story Graph state is unchanged
```

**Examples:**
| initial_state | write_error |
| --- | --- |
| 50 nodes, version 1.2.3 | Permission denied - file is read-only |
| 50 nodes, version 1.2.3 | Disk full - cannot write file |
| 50 nodes, version 1.2.3 | File locked by another process |


<a id="scenario-update-version-metadata-on-successful-persistence"></a>
### Scenario: [Update version metadata on successful persistence](#scenario-update-version-metadata-on-successful-persistence) (happy_path)

**Steps:**
```gherkin
Given Story Graph is initialized
Given Story Graph has version: <initial_version>
And last modified timestamp: <initial_timestamp>
When Story Graph persists modifications successfully
Then version is incremented to: <new_version>
And last modified timestamp is updated to current time
And modification count is incremented
And metadata is persisted with graph
```

**Examples:**
| initial_version | initial_timestamp | new_version |
| --- | --- | --- |
| 1.0.0 | 2025-01-01T00:00:00Z | 1.0.1 |
| 1.2.5 | 2025-06-15T12:30:00Z | 1.2.6 |
| 2.0.0 | 2025-12-31T23:59:59Z | 2.0.1 |

