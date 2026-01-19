# Design Model

## Object-Oriented Design Patterns

### Domain Concepts with Responsibilities

## Epic: Invoke Bot Through Panel

### PanelView (Base)

**Module:** panel

**Instantiated with:** 

**Responsibilities:**
- Wraps JSON data: JSON
- Spawns subprocess: CLI, Python Process
- Sends command to CLI: Command, Stdin
- Receives JSON from CLI: Stdout
- Parses JSON: String, Dict
- Provides element ID: String
- Renders to HTML: HTML, JSON

**Ownership:**
- Has: 
- References: 

### SectionView : PanelView (Base)

**Module:** panel

**Instantiated with:** 

**Responsibilities:**
- Renders section header: PanelHeader
- Toggles collapsed state: State
- May contain subsections: SubSectionView

**Ownership:**
- Has: 
- References: 

### SubSectionView : PanelView

**Module:** panel

**Instantiated with:** 

**Responsibilities:**
- Toggles collapsed state: State

**Ownership:**
- Has: 
- References: 

### PanelHeader

**Module:** panel

**Instantiated with:** 

**Responsibilities:**
- Displays header image: Image
- Displays title: String

**Ownership:**
- Has: 
- References: 

### StoryMapView : PanelView

**Module:** story_graph.story_map

**Instantiated with:** StoryGraph, PanelView

**Responsibilities:**
- Wraps story map JSON: StoryMap JSON
- Renders story graph as tree hierarchy: StoryNode, HTML
- Displays epic hierarchy: EpicView, Epic JSON
- Shows context-appropriate action buttons: StoryNode, ButtonSet
- Refreshes tree display: StoryGraph, DOM
- Searches stories: Filter, StoryGraph JSON
- Opens story graph file: CLI, File JSON
- Opens story map file: CLI, File JSON
- Delegates to InlineNameEditor: InlineNameEditor, StoryNode
- Delegates to StoryNodeDragDropManager: StoryNodeDragDropManager, StoryNode

**Ownership:**
- Has: InlineNameEditor, StoryNodeDragDropManager, ValidationMessageDisplay
- References: StoryGraph, StoryNode

### InlineNameEditor

**Module:** story_graph.nodes

**Instantiated with:** StoryNode

**Responsibilities:**
- Enables inline editing mode: DOM Element, Input Field
- Validates name in real-time: StoryNode, Siblings Collection
- Saves name on blur or Enter: StoryNode, Event
- Cancels on Escape: Event, Original Value
- Shows validation messages: ValidationMessageDisplay, Message

**Ownership:**
- Has: ValidationMessageDisplay
- References: StoryNode

### ValidationMessageDisplay

**Module:** story_graph.nodes

**Instantiated with:** 

**Responsibilities:**
- Shows warning message: Message Text, DOM Element
- Hides message: DOM Element
- Applies message styling: CSS Class, Message Type

**Ownership:**
- Has: 
- References: 

### StoryNodeDragDropManager

**Module:** story_graph.story_map

**Instantiated with:** StoryGraph

**Responsibilities:**
- Shows drag cursor with icon: Cursor Style, Node Icon
- Validates drop target compatibility at UI level: Source Node Type, Target Parent Type
- Shows no-drop cursor for incompatible targets: Cursor Style
- Highlights valid drop target: Target Element, CSS Class
- Delegates move to StoryNode domain operation: StoryNode, Target Parent, Position
- Returns node to original on invalid drop: Original Position, Animation

**Ownership:**
- Has: 
- References: StoryGraph, StoryNode

### ConfirmationDialog

**Module:** panel

**Instantiated with:** Message, Callback

**Responsibilities:**
- Shows confirmation inline: Message, DOM Element
- Shows confirm and cancel buttons: Button Set
- Invokes callback on confirm: Callback Function
- Hides confirmation on cancel: DOM Element

**Ownership:**
- Has: 
- References: 

## Epic: Invoke Bot Through REPL

### DotNotationParser

**Module:** story_graph.story_map

**Instantiated with:** StoryGraph

**Responsibilities:**
- Parses dot notation to node path: Dot Notation String, Path Segments
- Resolves node from path: StoryGraph, Path Segments, StoryNode
- Formats navigation error with valid paths: Error Message, Valid Paths List

**Ownership:**
- Has: 
- References: StoryGraph, StoryNode

### FileModificationMonitor

**Module:** story_graph.story_map

**Instantiated with:** File Path

**Responsibilities:**
- Detects file modification: File System, Last Modified Timestamp
- Delegates reload to StoryGraph: StoryGraph, File Path
- Triggers panel refresh: StoryMapView, DOM
- Shows validation error notification: Error Message, Panel Display
- Retains previous valid graph on error: Previous Graph, StoryGraph

**Ownership:**
- Has: 
- References: StoryGraph, StoryMapView

