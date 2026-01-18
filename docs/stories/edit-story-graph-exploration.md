# Edit Story Graph - Increment Exploration

---

## Stories (18 total across 3 channels)

### Channel 1: Invoke Bot Directly - Edit Story Graph

### 📝 Add Child Story Node To Parent

**Acceptance Criteria:**
- **When** Bot Behavior submits valid parent node identifier AND valid child node data, **then** System validates parent node exists in graph AND System validates child node structure matches schema AND System adds child node to parent node AND System assigns sequential order to child node
- **When** Bot Behavior submits parent node identifier for non-existent node, **then** System identifies parent node does not exist AND System returns error with parent node identifier
- **When** Bot Behavior submits invalid child node data structure, **then** System validates child node structure AND System identifies structure violations AND System returns error with validation details
- **When** Bot Behavior submits child node with duplicate name under same parent, **then** System checks existing child nodes under parent AND System identifies duplicate name AND System returns error with duplicate node name
- **When** Bot Behavior adds child to parent with existing children, **then** System retrieves existing children count AND System assigns next sequential order to new child AND System preserves existing children order
- **When** Bot Behavior adds child node with missing required fields, **then** System validates required fields present AND System identifies missing fields AND System returns error with missing field names

---

### 📝 Delete Story Node From Parent

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier to delete, **then** System validates node exists in graph AND System validates node has parent AND System removes node from parent AND System resequences remaining sibling nodes
- **When** Bot Behavior submits node identifier for non-existent node, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior deletes node with child nodes, **then** System checks for child nodes AND System recursively removes child nodes AND System removes parent node
- **When** Bot Behavior deletes node from parent with multiple children, **then** System removes target node AND System resequences remaining children AND System preserves sibling node order

---

### 📝 Update Story Node name

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier AND new node name, **then** System validates node exists in graph AND System validates new name not empty AND System validates new name unique among siblings AND System updates node name
- **When** Bot Behavior submits node identifier for non-existent node, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior submits empty or whitespace-only name, **then** System validates name not empty AND System returns error indicating invalid name
- **When** Bot Behavior submits name that duplicates sibling node name, **then** System checks sibling node names AND System identifies duplicate name AND System returns error with duplicate node name
- **When** Bot Behavior updates name with special characters, **then** System validates name format AND System updates node name if valid AND System returns error if name contains invalid characters

---

### 📝 Move Story Node

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier AND new parent identifier AND new position, **then** System validates source node exists AND System validates target parent exists AND System validates position within bounds AND System removes node from current parent AND System inserts node at new position under new parent AND System resequences nodes in both locations
- **When** Bot Behavior moves node to same parent different position, **then** System removes node from current position AND System inserts node at new position AND System resequences sibling nodes
- **When** Bot Behavior submits non-existent node identifier, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior submits non-existent target parent identifier, **then** System identifies parent does not exist AND System returns error with parent identifier
- **When** Bot Behavior moves node to position exceeding sibling count, **then** System validates position AND System returns error with valid position range
- **When** Bot Behavior moves node to create circular reference, **then** System validates target parent not descendant of source node AND System returns error indicating circular reference

---

### 📝 Submit Action Scoped To Story Scope

**Acceptance Criteria:**
- **When** Bot Behavior submits valid action name AND story scope identifier, **then** System validates action exists AND System validates story scope exists in graph AND System resolves story scope path AND System executes action with story scope context
- **When** Bot Behavior submits non-existent action name, **then** System identifies action does not exist AND System returns error with available action names
- **When** Bot Behavior submits non-existent story scope identifier, **then** System identifies story scope does not exist AND System returns error with scope identifier
- **When** Bot Behavior submits action with invalid parameters for story scope, **then** System validates action parameters AND System identifies parameter violations AND System returns error with parameter requirements
- **When** Bot Behavior submits action that requires additional context, **then** System identifies missing context AND System requests additional context from behavior
- **When** Action execution modifies story graph, **then** System applies modifications within story scope AND System validates graph structure remains valid

---

### 📝 Update Story Graph Changes

**Acceptance Criteria:**
- **When** System modifies story graph structure, **then** System validates graph structure integrity AND System persists changes to storage AND System updates graph version metadata
- **When** System persists changes to storage, **then** System writes updated graph AND System verifies write successful
- **When** Storage write fails, **then** System identifies write failure AND System rolls back in-memory changes AND System returns error with failure details
- **When** System validates graph structure after modification, **then** System checks all node references valid AND System checks sequential order consistency AND System returns validation results
- **When** Validation identifies graph structure violations, **then** System identifies violation details AND System prevents persistence AND System returns error with violation specifics

---

### Channel 2: Invoke Bot Through Panel - Edit Story Graph In Panel

### 📝 Add Child Story Node To Parent

**Acceptance Criteria:**
- **When** Bot Behavior submits valid parent node identifier AND valid child node data, **then** System validates parent node exists in graph AND System validates child node structure matches schema AND System adds child node to parent node AND System assigns sequential order to child node
- **When** Bot Behavior submits parent node identifier for non-existent node, **then** System identifies parent node does not exist AND System returns error with parent node identifier
- **When** Bot Behavior submits invalid child node data structure, **then** System validates child node structure AND System identifies structure violations AND System returns error with validation details
- **When** Bot Behavior submits child node with duplicate name under same parent, **then** System checks existing child nodes under parent AND System identifies duplicate name AND System returns error with duplicate node name
- **When** Bot Behavior adds child to parent with existing children, **then** System retrieves existing children count AND System assigns next sequential order to new child AND System preserves existing children order
- **When** Bot Behavior adds child node with missing required fields, **then** System validates required fields present AND System identifies missing fields AND System returns error with missing field names

---

### 📝 Delete Story Node From Parent

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier to delete, **then** System validates node exists in graph AND System validates node has parent AND System removes node from parent AND System resequences remaining sibling nodes
- **When** Bot Behavior submits node identifier for non-existent node, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior deletes node with child nodes, **then** System checks for child nodes AND System recursively removes child nodes AND System removes parent node
- **When** Bot Behavior deletes node from parent with multiple children, **then** System removes target node AND System resequences remaining children AND System preserves sibling node order

---

### 📝 Update Story Node name

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier AND new node name, **then** System validates node exists in graph AND System validates new name not empty AND System validates new name unique among siblings AND System updates node name
- **When** Bot Behavior submits node identifier for non-existent node, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior submits empty or whitespace-only name, **then** System validates name not empty AND System returns error indicating invalid name
- **When** Bot Behavior submits name that duplicates sibling node name, **then** System checks sibling node names AND System identifies duplicate name AND System returns error with duplicate node name
- **When** Bot Behavior updates name with special characters, **then** System validates name format AND System updates node name if valid AND System returns error if name contains invalid characters

---

### 📝 Move Story Node

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier AND new parent identifier AND new position, **then** System validates source node exists AND System validates target parent exists AND System validates position within bounds AND System removes node from current parent AND System inserts node at new position under new parent AND System resequences nodes in both locations
- **When** Bot Behavior moves node to same parent different position, **then** System removes node from current position AND System inserts node at new position AND System resequences sibling nodes
- **When** Bot Behavior submits non-existent node identifier, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior submits non-existent target parent identifier, **then** System identifies parent does not exist AND System returns error with parent identifier
- **When** Bot Behavior moves node to position exceeding sibling count, **then** System validates position AND System returns error with valid position range
- **When** Bot Behavior moves node to create circular reference, **then** System validates target parent not descendant of source node AND System returns error indicating circular reference

---

### 📝 Submit Action Scoped To Story Scope

**Acceptance Criteria:**
- **When** Bot Behavior submits valid action name AND story scope identifier, **then** System validates action exists AND System validates story scope exists in graph AND System resolves story scope path AND System executes action with story scope context
- **When** Bot Behavior submits non-existent action name, **then** System identifies action does not exist AND System returns error with available action names
- **When** Bot Behavior submits non-existent story scope identifier, **then** System identifies story scope does not exist AND System returns error with scope identifier
- **When** Bot Behavior submits action with invalid parameters for story scope, **then** System validates action parameters AND System identifies parameter violations AND System returns error with parameter requirements
- **When** Bot Behavior submits action that requires additional context, **then** System identifies missing context AND System requests additional context from behavior
- **When** Action execution modifies story graph, **then** System applies modifications within story scope AND System validates graph structure remains valid

---

### 📝 Automatically Refresh Story Graph Changes

**Acceptance Criteria:**
- **When** System detects story graph file modification, **then** System reads updated graph structure AND System validates graph structure integrity AND System notifies Panel to refresh display
- **When** Panel receives refresh notification, **then** Panel reloads story graph data AND Panel updates visible story structure AND Panel preserves current navigation state if possible
- **When** System detects invalid graph structure after modification, **then** System identifies structure violations AND System displays error notification in Panel AND System retains previous valid graph state
- **When** Multiple rapid changes occur to story graph, **then** System debounces refresh requests AND System waits for stable state AND System performs single refresh after stabilization

---

### Channel 3: Invoke Bot Through REPL - Edit Story Graph In CLI

### 📝 Add Child Story Node To Parent

**Acceptance Criteria:**
- **When** Bot Behavior submits valid parent node identifier AND valid child node data, **then** System validates parent node exists in graph AND System validates child node structure matches schema AND System adds child node to parent node AND System assigns sequential order to child node
- **When** Bot Behavior submits parent node identifier for non-existent node, **then** System identifies parent node does not exist AND System returns error with parent node identifier
- **When** Bot Behavior submits invalid child node data structure, **then** System validates child node structure AND System identifies structure violations AND System returns error with validation details
- **When** Bot Behavior submits child node with duplicate name under same parent, **then** System checks existing child nodes under parent AND System identifies duplicate name AND System returns error with duplicate node name
- **When** Bot Behavior adds child to parent with existing children, **then** System retrieves existing children count AND System assigns next sequential order to new child AND System preserves existing children order
- **When** Bot Behavior adds child node with missing required fields, **then** System validates required fields present AND System identifies missing fields AND System returns error with missing field names

---

### 📝 Delete Story Node From Parent

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier to delete, **then** System validates node exists in graph AND System validates node has parent AND System removes node from parent AND System resequences remaining sibling nodes
- **When** Bot Behavior submits node identifier for non-existent node, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior deletes node with child nodes, **then** System checks for child nodes AND System recursively removes child nodes AND System removes parent node
- **When** Bot Behavior deletes node from parent with multiple children, **then** System removes target node AND System resequences remaining children AND System preserves sibling node order

---

### 📝 Update Story Node name

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier AND new node name, **then** System validates node exists in graph AND System validates new name not empty AND System validates new name unique among siblings AND System updates node name
- **When** Bot Behavior submits node identifier for non-existent node, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior submits empty or whitespace-only name, **then** System validates name not empty AND System returns error indicating invalid name
- **When** Bot Behavior submits name that duplicates sibling node name, **then** System checks sibling node names AND System identifies duplicate name AND System returns error with duplicate node name
- **When** Bot Behavior updates name with special characters, **then** System validates name format AND System updates node name if valid AND System returns error if name contains invalid characters

---

### 📝 Move Story Node

**Acceptance Criteria:**
- **When** Bot Behavior submits valid node identifier AND new parent identifier AND new position, **then** System validates source node exists AND System validates target parent exists AND System validates position within bounds AND System removes node from current parent AND System inserts node at new position under new parent AND System resequences nodes in both locations
- **When** Bot Behavior moves node to same parent different position, **then** System removes node from current position AND System inserts node at new position AND System resequences sibling nodes
- **When** Bot Behavior submits non-existent node identifier, **then** System identifies node does not exist AND System returns error with node identifier
- **When** Bot Behavior submits non-existent target parent identifier, **then** System identifies parent does not exist AND System returns error with parent identifier
- **When** Bot Behavior moves node to position exceeding sibling count, **then** System validates position AND System returns error with valid position range
- **When** Bot Behavior moves node to create circular reference, **then** System validates target parent not descendant of source node AND System returns error indicating circular reference

---

### 📝 Submit Action Scoped To Story Scope

**Acceptance Criteria:**
- **When** Bot Behavior submits valid action name AND story scope identifier, **then** System validates action exists AND System validates story scope exists in graph AND System resolves story scope path AND System executes action with story scope context
- **When** Bot Behavior submits non-existent action name, **then** System identifies action does not exist AND System returns error with available action names
- **When** Bot Behavior submits non-existent story scope identifier, **then** System identifies story scope does not exist AND System returns error with scope identifier
- **When** Bot Behavior submits action with invalid parameters for story scope, **then** System validates action parameters AND System identifies parameter violations AND System returns error with parameter requirements
- **When** Bot Behavior submits action that requires additional context, **then** System identifies missing context AND System requests additional context from behavior
- **When** Action execution modifies story graph, **then** System applies modifications within story scope AND System validates graph structure remains valid

---

### 📝 Automatically Refresh Story Graph Changes

**Acceptance Criteria:**
- **When** System detects story graph file modification, **then** System reads updated graph structure AND System validates graph structure integrity AND System notifies CLI to refresh display
- **When** CLI receives refresh notification, **then** CLI reloads story graph data AND CLI updates visible story structure AND CLI preserves current navigation state if possible
- **When** System detects invalid graph structure after modification, **then** System identifies structure violations AND System displays error notification in CLI AND System retains previous valid graph state
- **When** Multiple rapid changes occur to story graph, **then** System debounces refresh requests AND System waits for stable state AND System performs single refresh after stabilization

---

## Consolidation Decisions

### Channel Consolidation
- **Consolidated Across Channels**: Core edit operations (Add Child, Delete, Update Name, Move, Submit Action) use identical acceptance criteria across Direct, Panel, and CLI channels
- **Rationale**: Domain logic is channel-agnostic - the operations work the same way regardless of invocation method
- **Channel-Specific Stories**: Only the final story differs by channel:
  - **Direct**: "Update Story Graph Changes" (manual persistence)
  - **Panel**: "Automatically Refresh Story Graph Changes" (with Panel-specific notifications)
  - **CLI**: "Automatically Refresh Story Graph Changes" (with CLI-specific notifications)

### Validation Consolidation
- **Consolidated**: All node existence validation uses the same pattern across stories (validate node exists → return error if not found)
- **Rationale**: Same validation logic, different node types (parent, child, target) - consolidated into single validation behavior

### Error Handling Consolidation
- **Consolidated**: All error returns follow the same pattern (identify error → return error with details)
- **Rationale**: Same error handling logic, different error types - consolidated into single error handling behavior

### Sequential Ordering Consolidation
- **Consolidated**: Resequencing behavior is consistent across Add, Delete, and Move operations
- **Rationale**: Same resequencing logic regardless of the operation that triggered it

### Separation Decisions
- **Kept Separate**: Node validation vs. name validation vs. position validation
- **Rationale**: Different validation rules and formulas apply to each type
- **Kept Separate by Channel**: Refresh/persistence mechanisms differ by invocation channel (Direct uses manual persistence, Panel/CLI use automatic refresh)

---

## Domain Rules Referenced

1. **Parent-Child Referential Integrity**: Referenced in Add Child, Delete Node, Move Node
2. **Sibling Name Uniqueness**: Referenced in Add Child, Update Node Name
3. **Sequential Order Management**: Referenced in Add Child, Delete Node, Move Node
4. **Schema Compliance**: Referenced in Add Child, Update Story Graph Changes
5. **Circular Reference Prevention**: Referenced in Move Node
6. **Storage Transaction Consistency**: Referenced in Update Story Graph Changes

---

## Source Material

- Story Graph Schema: `C:/dev/agile_bots/docs/stories/story-graph.json`
- CRC Model: `C:/dev/agile_bots/docs/crc/crc-model-outline.md`
- Clarification Data: `C:/dev/agile_bots/docs/stories/clarification.json`
- Story Map: `C:/dev/agile_bots/docs/stories/story-map.txt`
