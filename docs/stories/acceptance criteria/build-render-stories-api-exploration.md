# Increment Exploration: Perform Action

Increment: Perform Action
User Goal: Enable bot behaviors to build, render, and synchronize story graphs using a pluggable adapter architecture that supports multiple backend formats (DrawIO, Markdown, JSON) with bidirectional synchronization.

## Stories

###  Render Story Graph using Story Graph API
Acceptance Criteria:
- WHEN a StoryAdapter renders an StoryOutput
  THEN the StoryAdapter retrieves the StoryMap from the Bot
  AND the StoryAdapter parses each node in StoryMap
  AND creates a matching StoryRenderedNode for each StoryNode in the StoryMap
  AND the StoryRenderedNode renders itself on the Diagram using the StoryAdapter
  USING formatting and positional rules associated with it's node type from the StoryAdapter
  AND the StoryRenderedNode iterates over it's node children to render themselves in turn
  AND every node in the StoryMap is represented in the Diagram
  AND the StoryRenderedNodes are saved as a StoryOutput file
  AND the StoryAdapter persists all positional data in a json file matching the rendered diagram


  When the StoryIODiagram is finished rendering
  Then all of the StoryRenderedNode are accessible using the same StoryMap API as the original object model
  AND the original StoryMap's parent/child relationship and all original data will be accessed exactly like the original
  And additional data will also be accessible, including formatting data, sizing and positional information

  When the bot, cli or another API makes a change to a StoryRenderedNode on the StoryOutput
  THEN the StoryRenderedNode will render itself again and update the StoryOutput as required

###  Build Story Graph Using API

Acceptance Criteria:

- WHEN Bot is called through StoryMap API
  THEN caller uses create_epic(), create_child(), create_story() for fine-grained construction
  AND caller validates each node during creation
  AND validation errors caught immediately before invalid structure created

- WHEN Bot is called with large story graph structures
  THEN caller uses create_epic_from_dict() for batch operations
  AND caller passes dictionary notation with epic/sub-epic/story hierarchy
  AND StoryMap converts dict notation to domain objects
  AND StoryMap validates entire structure before committing

- WHEN StoryMap uses save() method
  THEN StoryMap persists story_graph dict to JSON file
  AND file format matches existing story-graph.json structure
  AND all nodes converted to dict representation before saving

- WHEN StoryMap uses load() method
  THEN StoryMap reads JSON file
  AND StoryMap rebuilds domain model from JSON
  AND StoryMap reconstructs all Epic, SubEpic, Story objects with relationships

- WHEN fine-grained and batch APIs implement same interface
  THEN both validate hierarchy rules (no mixing sub-epics and stories)
  AND both handle positioning and resequencing
  AND both update story_graph dict representation
  AND interface enables incremental construction or bulk creation

### Build Story Graph With CLI

Acceptance Criteria:

- WHEN AI builds story graph through CLI
  THEN AI calls CLI commands instead of writing raw JSON
  AND AI uses create_epic, create_sub_epic, create_story commands for fine-grained construction
  AND each CLI command invokes corresponding StoryMap API method
  AND validation errors returned immediately to AI

- WHEN AI builds large story graph structures through CLI
  THEN AI uses create_from_json command for batch operations
  AND AI passes dictionary notation with epic/sub-epic/story hierarchy
  AND CLI accepts both inline JSON notation and file paths
  AND CLI invokes StoryMap.create_epic_from_dict() with provided data

- WHEN CLI wraps StoryMap API
  THEN CLI exposes create_epic, create_sub_epic, create_story commands
  AND CLI exposes create_from_json for batch operations
  AND CLI provides save command to persist changes
  AND CLI can be called from AI or human users

- WHEN AI completes building story graph
  THEN AI calls save command through CLI
  AND CLI invokes StoryMap.save() method
  AND story_graph persisted to file
  AND AI receives confirmation of successful save

###  Detect Story Graph Changes From Diagram

Acceptance Criteria:

- WHEN User makes changes to StoryOutput diagram
  THEN the StoryMap hanging off StoryOutput reflects those changes in its object model
  AND the changes are visible when accessing the StoryMap directly via API
  AND the StoryRenderedNodes maintain parent/child relationships matching the modified structure

- WHEN User hits synchronize button
  THEN Synchronizer compares StoryOutput's StoryMap against Bot's story_graph
  AND Synchronizer identifies all differences (added nodes, deleted nodes, renamed nodes, moved nodes)
  AND Synchronizer generates batch of change operations grouped by change type
  AND Synchronizer calculates dependencies between changes (e.g., must create parent before child)

### Create Child Story Node From Diagram

Acceptance Criteria:

- WHEN Bot's StoryMap reads batch of add operations from Synchronizer
  THEN Bot's StoryMap creates new child nodes at correct hierarchy positions
  AND new nodes include all properties from diagram's StoryMap (name, type, sequential order)
  AND Bot's StoryMap resequences existing siblings when inserting at specific positions
  AND parent-child relationships match diagram's StoryMap structure

- WHEN Bot's StoryMap reads Epic add child SubEpic operation
  THEN Bot's StoryMap adds Sub-Epic to Epic's children
  AND sequential order matches position from diagram's StoryMap

- WHEN Bot's StoryMap reads SubEpic add child SubEpic operation (no Story children)
  THEN Bot's StoryMap adds SubEpic to parent SubEpic's children

- WHEN Bot's StoryMap reads SubEpic add Story operation (no SubEpic children)
  THEN Bot's StoryMap creates default StoryGroup under Sub-Epic if needed
  AND Bot's StoryMap adds Story to Story Group
  AND story properties match diagram's StoryMap

- WHEN Bot's StoryMap reads SubEpic add SubEpic operation (has existing Story children)
  THEN Bot's StoryMap identifies SubEpic already contains Stories
  AND Bot's StoryMap reports error indicating cannot create SubEpic under SubEpic with Stories
  BUT Bot's StoryMap does not apply the invalid add operation

- WHEN Bot's StoryMap reads SubEpic add Story operation (has existing SubEpic children)
  THEN Bot's StoryMap identifies SubEpic already contains Sub-Epics
  AND Bot's StoryMap reports error indicating cannot create Story under SubEpic with Sub-Epics
  BUT Bot's StoryMap does not apply the invalid add operation

- WHEN both Bot's StoryMap and diagram's StoryMap implement same interface
  THEN both expose load() method
  AND both expose save() method
  AND both expose update() method
  AND interface enables bidirectional synchronization



### Delete Story Node From Diagram

Acceptance Criteria:

- WHEN Bot's StoryMap reads batch of delete operations from Synchronizer
  THEN Bot's StoryMap removes nodes from story_graph
  AND Bot's StoryMap resequences remaining siblings after deletion
  AND Bot's StoryMap handles cascade deletes (removing node removes all descendants)
  BUT Bot's StoryMap preserves scenarios and steps from deleted stories in archive/backup

- WHEN Bot's StoryMap reads delete operation for node with children
  THEN Bot's StoryMap removes node and all descendants recursively
  AND Bot's StoryMap logs all deleted nodes for audit trail

### Update Story Node Name From Diagram
Acceptance Criteria:

- WHEN Bot's StoryMap reads batch of rename operations from Synchronizer
  THEN Bot's StoryMap updates node names to match diagram's StoryMap names
  AND Bot's StoryMap validates no duplicate names at same hierarchy level
  AND Bot's StoryMap updates all references to renamed nodes

- WHEN Bot's StoryMap reads rename operation that creates duplicate name at same level
  THEN Bot's StoryMap identifies duplicate name
  AND Bot's StoryMap reports error
  BUT Bot's StoryMap does not apply conflicting rename

### Move Story Node From Diagram
Acceptance Criteria:

- WHEN Bot's StoryMap reads batch of move/reorder operations from Synchronizer
  THEN Bot's StoryMap removes nodes from old parent
  AND Bot's StoryMap adds nodes to new parent at correct position
  AND Bot's StoryMap updates sequential_order values to match diagram's StoryMap ordering
  AND Bot's StoryMap resequences siblings in both old and new parent locations

- WHEN Bot's StoryMap reads move operation to new parent with specified position
  THEN Bot's StoryMap inserts at specified position
  AND Bot's StoryMap resequences existing siblings at or after position

### Persist Story Graph Changes From Diagram

Acceptance Criteria:

- WHEN Bot's StoryMap completes reading and applying all batches successfully
  THEN Bot's StoryMap structure matches diagram's StoryMap structure
  AND all node names, types, hierarchy, and ordering match
  AND Bot's StoryMap logs summary (nodes added, deleted, renamed, moved)
  AND Bot's StoryMap persists updated story_graph to file using save() method

- WHEN Bot's StoryMap encounters errors during batch application
  THEN Bot's StoryMap identifies which operation failed and why
  AND Bot's StoryMap rolls back incomplete batch to maintain consistency
  AND Bot's StoryMap reports error details to user
  BUT Bot's StoryMap does not apply partial changes that leave story_graph in inconsistent state




