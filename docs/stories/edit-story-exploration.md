# Edit Story - Increment Exploration

**Navigation:** [📋 Story Map](story-map.txt) | [📊 Story Graph](story-graph.json)

**File Name**: `edit-story-exploration.md`
**Location**: `C:\dev\agile_bots\docs\stories\edit-story-exploration.md`

**Priority:** High
**Relative Size:** Large

## Increment Purpose

Developers and Bot Behaviors manipulate story graph structure programmatically, enabling dynamic story hierarchy management, node lifecycle operations, and scope-based action execution across three interaction modes (Direct API, Panel UI, CLI) so that teams can evolve their story maps throughout the development lifecycle.

---

## Domain AC (Increment Level)

### Core Domain Concepts

- **Story Graph**: Hierarchical structure containing Epics, Sub-Epics, Story Groups, Stories, Scenarios, Scenario Outlines, and Acceptance Criteria  
- **Story Graph Node**: Base abstraction for all graph elements with common operations (create, move, delete, rename, execute)  
- **Epic**: Top-level organizational unit containing Sub-Epics  
- **Sub-Epic**: Mid-level organizational unit that contains either Sub-Epics OR Story Groups (not both)  
- **Story Group**: Collection of Stories with grouping semantics (and/or/opt connectors)  
- **Story**: Work item containing Scenarios, Scenario Outlines, and Acceptance Criteria  
- **Scenario**: Test scenario with steps belonging to Story  
- **Scenario Outline**: Parameterized test scenario template with examples  
- **Acceptance Criteria**: Behavioral condition-outcome pairs defining story completion  

---

### Domain Behaviors

- **Story Graph Node creates child**: Adds new child node of appropriate type at specified or default position with sequential ordering  
- **Story Graph Node moves to parent**: Removes itself from current parent and adds to target parent with position adjustment and resequencing  
- **Story Graph Node deletes itself**: Removes from parent with options to preserve, move, or recursively delete children  
- **Story Graph Node renames itself**: Updates node name with validation for uniqueness and format rules  
- **Story Graph Node executes scoped action**: Invokes bot action with story scope context and validates resulting graph structure  
- **Story Graph persists changes**: Validates graph integrity, writes to storage, and handles rollback on failure  
- **Epic creates Sub-Epic child**: Adds Sub-Epic to children collection  
- **Sub-Epic creates Sub-Epic child**: Adds Sub-Epic to children only if no Story children exist  
- **Sub-Epic creates Story child**: Creates default Story Group if needed and adds Story to group  
- **Story creates Scenario child**: Adds to scenario collection (not acceptance criteria)  
- **Story creates Scenario Outline child**: Adds to scenario collection (not acceptance criteria)  
- **Story creates Acceptance Criteria child**: Adds to acceptance criteria collection (not scenario)  

---

### Domain Rules

- **Hierarchical Structure Constraint**: Epics → Sub-Epics → (Sub-Epics OR Stories) → Scenarios/Acceptance Criteria  
- **Sub-Epic Exclusivity Rule**: Sub-Epic cannot contain both Sub-Epics and Stories simultaneously  
- **Circular Reference Prevention**: Node cannot move to its own descendant  
- **Name Uniqueness Rule**: Sibling nodes must have unique names  
- **Sequential Order Consistency**: Children maintain sequential order within their collection, resequencing when nodes added/moved/deleted  
- **Position Adjustment Rule**: Invalid positions automatically adjust to last valid position  
- **Persistence Integrity Rule**: Graph structure must pass validation before persistence occurs  
- **Child Collection Separation**: Stories maintain separate collections for scenarios and acceptance criteria  
- **Story Group Requirement**: Stories must belong to Story Group within Sub-Epic  
- **Action Scope Validation**: Actions executed at node level must preserve graph structure validity  

---

## Stories (6 total - Direct API)

### 📝 Create Child Story Node

**Actor:** Story Graph Node

**Acceptance Criteria:**  
- **WHEN** Story Graph Node creates new child Node  
  **THEN** parent Story Node creates new child node of appropriate type with provided name  
  **AND** parent Story Node adds the child as the last child of its children  
  (Example: child = bot.story_graph.epics["epic name"].createChild("child name"))  
- **WHEN** Story Graph Node creates new child with position specified  
  **THEN** parent Story Node adds the child as the specified position  
  **AND** resequences all children at or after the position  
  (Example: child = bot.story_graph.epics["epic name"].createChild("child name", 2))  
- **WHEN** Story Graph Node creates new child with invalid position specified  
  **THEN** adjusts position to last if exceeds children count  
  **AND** creates new child node with provided data at adjusted position  
  (Example: child = bot.story_graph.epics["epic name"].createChild("child name", 9))  
- **WHEN** Story Graph Node creates new child with identical name as another child of Node  
  **THEN** Story Graph Node identifies duplicate name  
  **AND** returns error  
- **WHEN** Story Graph Node creates new child without a name  
  **THEN** System populates name with unique field (eg: Child1)  
  (Example: child = bot.story_graph.epics["epic name"].createChild())  
- **WHEN** Epic creates a child SubEpic  
  **THEN** Epic adds Sub-Epic to children  
  (Example: subEpic = bot.story_graph.epics["epic name"].createChild("sub epic name"))  
- **WHEN** SubEpic with no Story children creates a child SubEpic  
  **THEN** SubEpic adds SubEpic to children  
  (Example: subEpic = bot.story_graph.epics["sub epic name"].createChild("sub epic name"))  
- **WHEN** SubEpic creates Sub-Epic that has Stories children  
  **THEN** SubEpic identifies SubEpic already contains Stories  
  **AND** returns error indicating cannot create SubEpic under SubEpic with Stories  
  **BUT** prevents create operation  
- **WHEN** Sub-Epic with no SubEpic children creates a child Story  
  **THEN** Sub-Epic creates default StoryGroup under Sub-Epic  
  **AND** Sub-Epic adds Story to Story Group  
  (Example: story = bot.story_graph.epics["sub epic name"].createChild("story"))  
- **WHEN** SubEpic creates a child Story with existing Story children  
  **THEN** SubEpic adds Story to existing SubEpic's Story Group  
- **WHEN** SubEpic creates Story that has SubEpic children  
  **THEN** SubEpic identifies SubEpic already contains Sub-Epics  
  **AND** returns error indicating cannot create Story under SubEpic with Sub-Epics  
  **BUT** prevents operation  
- **WHEN** Story creates Scenario  
  **THEN** Story adds Scenario to common scenario child collection  
  **BUT** Story does not add Scenario to acceptance criteria child collection  
- **WHEN** Story creates ScenarioOutline  
  **THEN** Story adds ScenarioOutline to common scenario child collection  
  **BUT** Story does not add Scenario to acceptance criteria child collection  
- **WHEN** Story creates AcceptanceCriteria  
  **THEN** Story adds Acceptance Criteria to its own child collection  
  **BUT** Story does not add Acceptance Criteria to scenario child collection  

---

### 📝 Move Story Node To Parent

**Actor:** Story Graph Node

**Acceptance Criteria:**  
- **WHEN** Story Graph Node moves to new parent  
  **THEN** node removes itself from current parent  
  **AND** node adds itself to target parent as last child  
  **AND** resequences original siblings on or after original location  
  (Example (parent API): bot.story_graph.epics["target epic"].addChild(childNode); Example (child API): childNode.moveTo(bot.story_graph.epics["target epic"]))  
- **WHEN** Story Graph Node moves to new parent with position specified  
  **THEN** node removes itself from current parent  
  **AND** node adds itself to target parent at specified position  
  **AND** resequences all children at or after position in both locations  
  (Example (parent API): bot.story_graph.epics["target epic"].addChild(childNode, 2); Example (child API): childNode.moveTo(bot.story_graph.epics["target epic"], 2))  
- **WHEN** Story Graph Node moves with invalid position specified  
  **THEN** adjusts position to last if exceeds children count  
  **AND** moves node to adjusted position  
  (Example (parent API): bot.story_graph.epics["target epic"].addChild(childNode, 99); Example (child API): childNode.moveTo(bot.story_graph.epics["target epic"], 99))  
- **WHEN** Story Graph Node moves to same parent different position  
  **THEN** node removes itself from current position  
  **AND** node adds itself at new position  
  **AND** resequences siblings  
  (Example (child API): childNode.moveTo(currentParent, 3); Example (child API): childNode.position = 3 //property encapsulates logic)  
- **WHEN** Story Graph Node moves to parent where it already exists  
  **THEN** Story Graph Node identifies child already under parent  
  **AND** returns error  
- **WHEN** SubEpic moves to SubEpic that has Stories  
  **THEN** target SubEpic identifies it already contains Stories  
  **AND** returns error indicating cannot move SubEpic to SubEpic with Stories  
  **BUT** prevents move operation  
- **WHEN** Story moves to SubEpic that has SubEpic children  
  **THEN** target SubEpic identifies it already contains Sub-Epics  
  **AND** returns error indicating cannot move Story to SubEpic with Sub-Epics  
  **BUT** prevents move operation  
- **WHEN** Story Graph Node moves to create circular reference  
  **THEN** node identifies target parent is descendant of itself  
  **AND** returns error indicating circular reference  
  **BUT** prevents move operation  

---

### 📝 Delete Story Node

**Actor:** Story Graph Node

**Acceptance Criteria:**  
- **WHEN** Story Graph Node deletes itself without children  
  **THEN** node removes itself from parent  
  **AND** resequences remaining siblings  
  (Example: bot.story_graph.epics["epic name"].sub_epics["sub epic name"].delete())  
- **WHEN** Story Graph Node deletes itself with children  
  **THEN** node moves all children to node's parent as last children  
  **AND** removes itself from parent  
  **AND** resequences siblings  
  (Example: bot.story_graph.epics["epic name"].delete())  
- **WHEN** Story Graph Node deletes itself including children  
  **THEN** node recursively deletes all children  
  **AND** removes itself from parent  
  **AND** resequences siblings  
  (Example: bot.story_graph.epics["epic name"].deleteWithChildren())  

---

### 📝 Update Story Node Name

**Actor:** Story Graph Node

**Acceptance Criteria:**  
- **WHEN** Story Graph Node renames itself  
  **THEN** node validates name not empty  
  **AND** validates name unique among siblings  
  **AND** updates node name  
  (Example: bot.story_graph.epics["old name"].rename("new name"))  
- **WHEN** Story Graph Node renames itself with empty or whitespace-only name  
  **THEN** node identifies name is empty  
  **AND** returns error  
- **WHEN** Story Graph Node renames itself with duplicate sibling name  
  **THEN** node identifies duplicate name among siblings  
  **AND** returns error  
- **WHEN** Story Graph Node renames itself with valid special characters  
  **THEN** node validates name format  
  **AND** updates node name  
- **WHEN** Story Graph Node renames itself with invalid special characters  
  **THEN** node validates name format  
  **AND** identifies invalid characters  
  **AND** returns error  

---

### 📝 Execute Action Scoped To Story Node

**Actor:** Story Graph Node

**Acceptance Criteria:**  
- **WHEN** Story Graph Node executes action with valid parameters  
  **THEN** node validates action exists  
  **AND** node invokes bot to execute action with scope context  
  **AND** node validates graph structure remains valid after execution  
  (Example: bot.story_graph.epics["epic name"].executeAction("build", {"output": "docs/stories"}))  
- **WHEN** Story Graph Node executes action with invalid parameters  
  **THEN** node invokes bot to execute action with scope context  
  **AND** bot validates action parameters are invalid  
  **AND** returns error with parameter requirements  

---

### 📝 Persist Story Graph Changes

**Actor:** Story Graph

**Acceptance Criteria:**  
- **WHEN** Story Graph structure is modified  
  **THEN** Story Graph validates graph structure integrity  
  **AND** Story Graph persists changes to storage  
  **AND** Story Graph updates version metadata  
- **WHEN** Story Graph persists changes successfully  
  **THEN** Story Graph writes updated graph to file  
  **AND** Story Graph verifies write successful  
- **WHEN** Story Graph persistence fails  
  **THEN** Story Graph identifies write failure  
  **AND** Story Graph rolls back in-memory changes  
  **AND** returns error with failure details  
- **WHEN** Story Graph validates structure after modification  
  **THEN** Story Graph checks all node references valid  
  **AND** Story Graph checks sequential order consistency  
- **WHEN** Story Graph identifies structure violations  
  **THEN** Story Graph identifies violation details  
  **AND** Story Graph prevents persistence  
  **AND** returns error with violation specifics  

---

## Consolidation Decisions

### Reuse vs Split Criteria

**Same Logic Consolidated:**  
- Create child operations with and without position parameter consolidated into same story (Create Child Story Node) as they share core creation logic with position being optional parameter  
- Move operations with and without position consolidated into same story (Move Story Node To Parent) as they share movement logic with position variation  
- Rename operations with various validation scenarios consolidated into single story (Update Story Node Name) as they share name validation and update logic  

**Different Logic Kept Separate:**  
- Create vs Move vs Delete vs Rename kept as separate stories because each represents fundamentally different graph manipulation operation  
- Execute Action kept separate from other operations as it triggers bot behavior invocation rather than direct graph manipulation  
- Persist Changes kept separate as it represents cross-cutting concern triggered by other operations rather than user-initiated action  

**Type-Specific Behavior Consolidated:**  
- Epic/Sub-Epic/Story-specific child creation rules consolidated within Create Child Story Node as acceptance criteria variations rather than separate stories  
- Type compatibility rules for moves consolidated within Move Story Node To Parent rather than separate stories per type combination  

---

## Domain Rules Referenced

1. **Sub-Epic Exclusivity Rule** - Referenced in Create Child Story Node and Move Story Node To Parent stories for validation of Sub-Epic content constraints  
2. **Name Uniqueness Rule** - Referenced in Create Child Story Node and Update Story Node Name stories for sibling name validation  
3. **Sequential Order Consistency** - Referenced across Create, Move, and Delete stories for child collection ordering  
4. **Position Adjustment Rule** - Referenced in Create and Move stories for invalid position handling  
5. **Circular Reference Prevention** - Referenced in Move Story Node To Parent for parent-child relationship validation  
6. **Persistence Integrity Rule** - Referenced in Persist Story Graph Changes and Execute Action stories for validation before save  
7. **Child Collection Separation** - Referenced in Create Child Story Node for Stories' scenario vs acceptance criteria collections  
8. **Hierarchical Structure Constraint** - Implicit across all stories, explicitly referenced in Create and Move for type compatibility validation  

---

## Source Material

- **Story Graph JSON Schema**: `C:\dev\agile_bots\docs\stories\story-graph.json` - Complete graph structure with all node types and relationships
- **Story Map Text**: `C:\dev\agile_bots\docs\stories\story-map.txt` - Human-readable hierarchical representation of Edit Story increment across all three invocation modes (Direct, Panel, CLI)
- **Strategy Decisions**: `C:\dev\agile_bots\docs\stories\strategy.json` - Design decisions including object instantiation patterns and parent-child management approaches
- **Clarification Context**: `C:\dev\agile_bots\docs\stories\clarification.json` - Requirements and user context for scope definition

---

## Additional Implementation Modes

This exploration covers the **Direct API invocation mode** with programmatic access through Story Graph Node objects. The same six core stories are implemented with different interaction patterns in:

### Panel UI Mode
- Visual tree-based navigation with drag-and-drop for moves
- Inline editing with real-time validation feedback
- Context-sensitive action buttons based on node selection
- Confirmation dialogs for destructive operations
- Automatic refresh on external file changes

### CLI Mode
- Dot notation path resolution for node navigation (e.g., `cli.story_graph."Invoke Bot"."Manage Story Graph"`)
- Command-based operations with parameter parsing
- Position specification through `.at_position.N` suffix
- Informational messages for external modifications
- Error messages with valid path suggestions

Both modes delegate to the same underlying domain model, ensuring consistent behavior and validation rules across all interaction modes.
