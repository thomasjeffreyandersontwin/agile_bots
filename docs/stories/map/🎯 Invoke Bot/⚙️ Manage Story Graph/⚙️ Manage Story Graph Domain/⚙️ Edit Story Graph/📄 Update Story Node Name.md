# 📄 Update Story Node Name

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Story Graph Node
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Domain](..) / [⚙️ Edit Story Graph](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Update Story Node Name functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Story Graph Node renames itself
  **then** node validates name not empty
  **and** validates name unique among siblings
  **and** updates node name

- **When** Story Graph Node renames itself with empty or whitespace-only name
  **then** node identifies name is empty
  **and** returns error

- **When** Story Graph Node renames itself with duplicate sibling name
  **then** node identifies duplicate name among siblings
  **and** returns error

- **When** Story Graph Node renames itself with valid special characters
  **then** node validates name format
  **and** updates node name

- **When** Story Graph Node renames itself with invalid special characters
  **then** node validates name format
  **and** identifies invalid characters
  **and** returns error

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-rename-node-with-valid-name-across-hierarchy-levels"></a>
### Scenario: [Rename node with valid name across hierarchy levels](#scenario-rename-node-with-valid-name-across-hierarchy-levels) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<node_type>" named "<old_name>" under parent "<parent_name>"
When node "<old_name>" is renamed to "<new_name>"
Then node name is updated to "<new_name>"
And node is accessible by name "<new_name>"
And node is no longer accessible by name "<old_name>"
```

**Examples:**
| node_type | parent_name | old_name | new_name |
| --- | --- | --- | --- |
| Epic | root | User Management | User Administration |
| SubEpic | User Management | Authentication | User Authentication |
| Story | Authentication | Login Form | User Login Form |
| Scenario | Login Form | Valid Login | Successful User Login |


<a id="scenario-rename-node-with-empty-or-whitespace-name-returns-error"></a>
### Scenario: [Rename node with empty or whitespace name returns error](#scenario-rename-node-with-empty-or-whitespace-name-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has "<node_type>" named "<current_name>"
When node "<current_name>" is renamed to "<invalid_name>"
Then system identifies name is empty or whitespace-only
And returns error "<error_message>"
And node name remains "<current_name>"
```

**Examples:**
| node_type | current_name | invalid_name | error_message |
| --- | --- | --- | --- |
| Epic | User Management |  | Node name cannot be empty |
| SubEpic | Authentication |  | Node name cannot be whitespace-only |
| Story | Login Form |  | Node name cannot be whitespace-only |


<a id="scenario-rename-node-with-duplicate-sibling-name-returns-error"></a>
### Scenario: [Rename node with duplicate sibling name returns error](#scenario-rename-node-with-duplicate-sibling-name-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children: <existing_children>
And node "<node_name>" is one of the children
When node "<node_name>" is renamed to "<duplicate_name>"
Then system identifies duplicate name among siblings
And returns error "Name '<duplicate_name>' already exists among siblings"
And node name remains "<node_name>"
```

**Examples:**
| parent_type | parent_name | existing_children | node_name | duplicate_name |
| --- | --- | --- | --- | --- |
| Epic | User Management | Authentication, Authorization, Audit | Audit | Authentication |
| SubEpic | Authentication | Login Flow, Password Reset, OAuth | OAuth | Login Flow |
| Story | Login Form | Valid Login, Invalid Password, Account Locked | Account Locked | Valid Login |


<a id="scenario-rename-node-with-valid-special-characters"></a>
### Scenario: [Rename node with valid special characters](#scenario-rename-node-with-valid-special-characters) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<node_type>" named "<old_name>"
When node "<old_name>" is renamed to "<new_name_with_special_chars>"
Then bot validates name format
And node name is updated to "<new_name_with_special_chars>"
And special characters in name are preserved
```

**Examples:**
| node_type | old_name | new_name_with_special_chars |
| --- | --- | --- |
| Epic | User Management | User Management & Administration |
| SubEpic | Authentication | Authentication (OAuth 2.0) |
| Story | Login | Login - Username/Password |
| Scenario | Valid Login | Valid Login: Success Response |


<a id="scenario-rename-node-with-invalid-special-characters-returns-error"></a>
### Scenario: [Rename node with invalid special characters returns error](#scenario-rename-node-with-invalid-special-characters-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has "<node_type>" named "<current_name>"
When node "<current_name>" is renamed to "<invalid_name>"
Then bot validates name format
And identifies invalid characters: <invalid_chars>
And returns error "Name contains invalid characters: <invalid_chars>"
And node name remains "<current_name>"
```

**Examples:**
| node_type | current_name | invalid_name | invalid_chars |
| --- | --- | --- | --- |
| Epic | User Management | User<Admin> | <, > |
| SubEpic | Authentication | Auth\System | \ |
| Story | Login Form | Login|Form | | |
| Scenario | Valid Login | Valid*Login? | *, ? |

