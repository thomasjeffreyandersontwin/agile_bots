# 📄 Save Story Map Changes Asynchronously

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 16.0
**Story Type:** user

## Story Description

Save Story Map Changes Asynchronously functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User moves node in Panel
  **then** Panel moves node in DOM immediately
  **and** Panel displays spinner

- **When** User renames node in Panel
  **then** Panel updates name in DOM immediately
  **and** Panel displays spinner

- **When** User deletes node in Panel
  **then** Panel removes node from DOM immediately
  **and** Panel displays spinner

- **When** User creates node in Panel
  **then** Panel adds node to DOM immediately
  **and** Panel displays spinner

- **When** Panel updates DOM
  **then** Panel keeps UI responsive BUT does not refresh entire panel

- **When** User makes change
  **then** Panel enqueues save operation
  **and** Panel debounces for 500ms

- **When** User makes multiple rapid changes
  **then** Panel batches all operations in queue
  **and** Panel displays operation count

- **When** 500ms elapses after last change
  **then** Panel processes entire queue sequentially
  **and** Panel executes each command

- **When** Panel processes queue
  **then** Panel spawns Python process for each command BUT does not block UI

- **When** Panel executes command
  **then** Panel marks operation as optimistic
  **and** Panel skips panel refresh

- **When** Panel enqueues operation
  **then** Panel displays status indicator in header
  **and** Panel shows spinner icon
  **and** Panel shows operation count

- **When** Backend completes save successfully
  **then** Panel shows green checkmark
  **and** Panel shows 'Saved' message
  **and** Panel auto-hides after 2 seconds

- **When** Backend returns error
  **then** Panel shows red X icon
  **and** Panel shows 'Save failed' message
  **and** Panel makes indicator clickable BUT does not auto-hide

- **When** User clicks error indicator
  **then** Panel displays error dialog
  **and** Panel shows error message
  **and** Panel shows stack trace

- **When** Backend returns validation error
  **then** Panel restores original DOM state
  **and** Panel displays error indicator

- **When** Backend returns hierarchy error
  **then** Panel restores original node position
  **and** Panel displays error indicator

- **When** Backend fails operation in batch
  **then** Panel rolls back only failed operation
  **and** Panel keeps successful operations BUT does not roll back entire batch

- **When** Panel rolls back operation
  **then** Panel executes rollback function
  **and** Panel restores captured state
  **and** Panel updates DOM to match original

- **When** User initiates move
  **then** Panel captures original parent
  **and** Panel captures original position
  **and** Panel captures node reference

- **When** User initiates rename
  **then** Panel captures original name
  **and** Panel captures name element reference

- **When** User initiates delete
  **then** Panel captures entire node HTML
  **and** Panel captures parent element
  **and** Panel captures position index

- **When** Backend completes save successfully
  **then** Backend writes changes to story-graph.json
  **and** Backend persists all node changes

- **When** User reloads Panel after successful save
  **then** Panel loads story-graph.json
  **and** Panel displays all saved changes

## Scenarios

<a id="scenario-user-moves-node-and-sees-optimistic-update-with-async-save"></a>
### Scenario: [User moves node and sees optimistic update with async save](#scenario-user-moves-node-and-sees-optimistic-update-with-async-save) (happy_path)

**Steps:**
```gherkin
Given Story Map contains <parent_node_type> named <parent_node_name>
And <parent_node_type> contains <node_type> named <node_name> at position <original_position>
And Panel is displaying story map
When User drags <node_type> <node_name> to new position <target_position>
Then StoryMapView.handleMoveNode moves <node_type> <node_name> to position <target_position> in DOM immediately
And StoryMapView.SaveQueue displays <status_indicator> in header
And StoryMapView.SaveQueue shows operation count <operation_count>
When StoryMapView.SaveQueue waits <debounce_time> after last change
Then StoryMapView.SaveQueue executes move command to Backend
And Backend moves <node_type> <node_name> from position <original_position> to <target_position>
And Backend writes changes to story-graph.json
When Backend completes save successfully
Then Panel shows <success_indicator>
And Panel shows <success_message>
And Panel auto-hides status after <auto_hide_time>
When User reloads Panel
Then Panel loads story-graph.json
And Panel displays <node_type> <node_name> at position <target_position>
```

**Examples:**
| parent_node_type | parent_node_name | node_type | node_name | original_position | target_position | status_indicator | operation_count | debounce_time | success_indicator | success_message | auto_hide_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Epic | Invoke Bot | SubEpic | Edit Story Map | 1 | 3 | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| SubEpic | Edit Story Map | Story | Save Story Map Changes Asynchronously | 0 | 5 | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| Story | Save Story Map Changes Asynchronously | Scenario | User moves node and sees optimistic update | 0 | 2 | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |


<a id="scenario-user-renames-node-and-sees-optimistic-update-with-async-save"></a>
### Scenario: [User renames node and sees optimistic update with async save](#scenario-user-renames-node-and-sees-optimistic-update-with-async-save) (happy_path)

**Steps:**
```gherkin
Given Story Map contains <parent_node_type> named <parent_node_name>
And <parent_node_type> contains <node_type> named <original_name>
And Panel is displaying story map
When User renames <node_type> from <original_name> to <new_name>
Then StoryMapView.handleRenameNode updates <node_type> name to <new_name> in DOM immediately
And StoryMapView.SaveQueue displays <status_indicator> in header
And StoryMapView.SaveQueue shows operation count <operation_count>
When StoryMapView.SaveQueue waits <debounce_time> after last change
Then StoryMapView.SaveQueue executes rename command to Backend
And Backend renames <node_type> from <original_name> to <new_name>
And Backend writes changes to story-graph.json
When Backend completes save successfully
Then Panel shows <success_indicator>
And Panel shows <success_message>
And Panel auto-hides status after <auto_hide_time>
When User reloads Panel
Then Panel loads story-graph.json
And Panel displays <node_type> named <new_name>
```

**Examples:**
| parent_node_type | parent_node_name | node_type | original_name | new_name | status_indicator | operation_count | debounce_time | success_indicator | success_message | auto_hide_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Epic | Invoke Bot | SubEpic | Edit Story Map | Modify Story Map | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| SubEpic | Edit Story Map | Story | Save Story Map Changes Asynchronously | Persist Story Map Changes Async | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| Story | Save Story Map Changes Asynchronously | Scenario | User moves node | User drags and drops node to reorder | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |


<a id="scenario-user-deletes-node-and-sees-optimistic-update-with-async-save"></a>
### Scenario: [User deletes node and sees optimistic update with async save](#scenario-user-deletes-node-and-sees-optimistic-update-with-async-save) (happy_path)

**Steps:**
```gherkin
Given Story Map contains <parent_node_type> named <parent_node_name>
And <parent_node_type> contains <node_type> named <node_name> at position <node_position>
And Panel is displaying story map
When User clicks delete on <node_type> <node_name>
Then StoryMapView.handleDeleteNode removes <node_type> <node_name> from DOM immediately
And StoryMapView.SaveQueue displays <status_indicator> in header
And StoryMapView.SaveQueue shows operation count <operation_count>
When StoryMapView.SaveQueue waits <debounce_time> after last change
Then StoryMapView.SaveQueue executes delete command to Backend
And Backend deletes <node_type> <node_name> from <parent_node_type>
And Backend writes changes to story-graph.json
When Backend completes save successfully
Then Panel shows <success_indicator>
And Panel shows <success_message>
And Panel auto-hides status after <auto_hide_time>
When User reloads Panel
Then Panel loads story-graph.json
And Panel confirms <node_type> <node_name> no longer exists
```

**Examples:**
| parent_node_type | parent_node_name | node_type | node_name | node_position | status_indicator | operation_count | debounce_time | success_indicator | success_message | auto_hide_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SubEpic | Edit Story Map | Story | Deprecated Story Example | 8 | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| Story | Save Story Map Changes Asynchronously | Scenario | Obsolete test scenario | 5 | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| Story | Save Story Map Changes Asynchronously | Acceptance Criterion | Outdated AC for feature | 15 | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |


<a id="scenario-user-creates-node-and-sees-optimistic-update-with-async-save"></a>
### Scenario: [User creates node and sees optimistic update with async save](#scenario-user-creates-node-and-sees-optimistic-update-with-async-save) (happy_path)

**Steps:**
```gherkin
Given Story Map contains <parent_node_type> named <parent_node_name>
And Panel is displaying story map
When User clicks create new <node_type> under <parent_node_type>
And User enters <node_type> name <new_node_name>
Then Panel adds <node_type> <new_node_name> to DOM immediately
And Panel displays <status_indicator> in header
And Panel shows operation count <operation_count>
When Panel waits <debounce_time> after last change
Then Panel executes create command to Backend
And Backend creates <node_type> <new_node_name> under <parent_node_type>
And Backend writes changes to story-graph.json
When Backend completes save successfully
Then Panel shows <success_indicator>
And Panel shows <success_message>
And Panel auto-hides status after <auto_hide_time>
When User reloads Panel
Then Panel loads story-graph.json
And Panel displays <node_type> <new_node_name> under <parent_node_type>
```

**Examples:**
| parent_node_type | parent_node_name | node_type | new_node_name | status_indicator | operation_count | debounce_time | success_indicator | success_message | auto_hide_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Epic | Invoke Bot | SubEpic | Export Story Map | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| SubEpic | Edit Story Map | Story | Undo Story Map Changes | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |
| Story | Save Story Map Changes Asynchronously | Scenario | User creates SubEpic and saves | spinner icon | 1 operation | 500ms | green checkmark | Saved | 2 seconds |


<a id="scenario-user-makes-multiple-rapid-changes-and-sees-batched-async-save"></a>
### Scenario: [User makes multiple rapid changes and sees batched async save](#scenario-user-makes-multiple-rapid-changes-and-sees-batched-async-save) (happy_path)

**Steps:**
```gherkin
Given Story Map contains Epic <epic_name> with SubEpic <sub_epic_name>
And SubEpic contains Story <story_name_a> at position <pos_a>
And SubEpic contains Story <story_name_b> at position <pos_b>
And SubEpic contains Story <story_name_c> at position <pos_c>
And Panel is displaying story map
When User moves <story_name_a> to position <new_pos_a>
And User renames <story_name_b> to <new_name_b> within <batch_window>
And User deletes <story_name_c> within <batch_window>
Then Panel updates all changes in DOM immediately
And Panel displays <status_indicator> in header
And Panel shows <batch_message>
When Panel waits <debounce_time> after last change
Then Panel executes <operation_count> commands sequentially to Backend
And Backend processes all operations
And Backend writes changes to story-graph.json
When Backend completes all saves successfully
Then Panel shows <success_indicator>
And Panel shows <success_message>
When User reloads Panel
Then Panel loads story-graph.json
And Panel displays <story_name_a> at position <new_pos_a>
And Panel displays Story named <new_name_b>
And Panel confirms <story_name_c> no longer exists
```

**Examples:**
| epic_name | sub_epic_name | story_name_a | pos_a | new_pos_a | story_name_b | new_name_b | pos_b | story_name_c | pos_c | batch_window | status_indicator | batch_message | debounce_time | operation_count | success_indicator | success_message |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Invoke Bot | Edit Story Map | Save Story Map Changes Asynchronously | 0 | 2 | Filter Scope | Apply Scope Filter | 1 | Deprecated Feature X | 3 | 500ms | spinner icon | Saving 3 changes... | 500ms | 3 | green checkmark | Saved |
| Invoke Bot | Navigate Behavior Actions | Display Current Behavior State | 0 | 1 | Navigate to Next Action | Advance to Next Action | 1 | Old Navigation Test | 2 | 500ms | spinner icon | Saving 3 changes... | 500ms | 3 | green checkmark | Saved |


<a id="scenario-user-sees-error-handling-when-async-save-fails"></a>
### Scenario: [User sees error handling when async save fails](#scenario-user-sees-error-handling-when-async-save-fails) (error_case)

**Steps:**
```gherkin
Given Story Map contains <parent_node_type> named <parent_node_name>
And <parent_node_type> contains <node_type> named <original_name>
And Panel is displaying story map
When User renames <node_type> to <invalid_name>
Then StoryMapView.handleRenameNode updates <node_type> name to <invalid_name> in DOM immediately
And StoryMapView.SaveQueue displays <status_indicator> in header
When StoryMapView.SaveQueue waits <debounce_time> after last change
Then StoryMapView.SaveQueue executes rename command to Backend
When Backend returns <error_type> error with message <error_message>
Then StoryMapView.SaveQueue shows <error_indicator>
And StoryMapView.SaveQueue shows <error_display_message>
And StoryMapView.SaveQueue makes error indicator clickable
And StoryMapView.SaveQueue does not auto-hide error
And StoryMapView.handleRenameNode rollback restores original name <original_name> in DOM
When User clicks error indicator
Then Panel displays error dialog
And Panel shows error details: <error_details>
```

**Examples:**
| parent_node_type | parent_node_name | node_type | original_name | invalid_name | status_indicator | debounce_time | error_type | error_message | error_indicator | error_display_message | error_details |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SubEpic | Edit Story Map | Story | Save Story Map Changes Asynchronously |  | spinner icon | 500ms | validation | Story name cannot be empty | red X icon | Save failed - click for details | ValidationError: Story name is required and cannot be empty string |
| Story | Save Story Map Changes Asynchronously | Scenario | User moves node | User moves node (contains 🎯 invalid emoji) | spinner icon | 500ms | validation | Scenario name contains invalid characters | red X icon | Save failed - click for details | ValidationError: Scenario name cannot contain emoji or special unicode characters |
| SubEpic | Edit Story Map | Story | Filter Scope | Navigate Behavior Actions | spinner icon | 500ms | hierarchy | Duplicate story name in parent SubEpic | red X icon | Save failed - click for details | HierarchyError: Story 'Navigate Behavior Actions' already exists in SubEpic 'Edit Story Map' |

