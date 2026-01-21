# CRC Domain Model - Perform Action (Story Graph API)

## Stories Analyzed
1. **Render Story Graph using Story Graph API**
2. **Build Story Graph Using API**
3. **Build Story Graph With CLI**

## Bounded Context: Story Graph

---

## Core Domain Concepts

### 1. **StoryNode** (Abstract Base)
**Module:** `story_graph.nodes`  
**Inherits:** ABC

**Responsibilities:**
- Traverse children
- Accept visitor
- Rename node
- Delete node
- Move node
- Persist changes

**Collaborators:** StoryNode, StoryRenderVisitor, StoryMap, Parent

---

### 2. **Epic** → StoryNode
**Module:** `story_graph.nodes`

**Responsibilities:**
- Contain sub-epics
- Create sub-epic
- Accept visitor

**Collaborators:** SubEpic, StoryMap, StoryRenderVisitor

---

### 3. **SubEpic** → StoryNode
**Module:** `story_graph.nodes`

**Responsibilities:**
- Contain sub-epics
- Contain stories
- Create child
- Validate hierarchy

**Collaborators:** SubEpic, Story, StoryMap

---

### 4. **Story** → StoryNode
**Module:** `story_graph.nodes`

**Responsibilities:**
- Contain acceptance criteria
- Contain scenarios
- Accept visitor

**Collaborators:** Scenario, StoryRenderVisitor

---

### 5. **StoryMap** → StoryNode (Root Aggregate)
**Module:** `story_graph.nodes`

**Responsibilities:**
- Contain epics
- Create epic
- Create epic from dict (batch API)
- Save story graph
- Load story graph
- Accept visitor

**Collaborators:** Epic, SubEpic, Story, StoryRenderVisitor

---

## Visitor Pattern (Rendering)

### 6. **StoryRenderVisitor** (Abstract Visitor)
**Module:** `story_graph.renderers`  
**Inherits:** ABC

**Responsibilities:**
- Visit story map
- Visit epic
- Visit sub epic
- Visit story
- Traverse children

**Collaborators:** StoryMap, Epic, SubEpic, Story, RenderedNode

---

### 7. **DrawIORenderer** → StoryRenderVisitor
**Module:** `synchronizers.story_io.renderers`

**Responsibilities:**
- Initialize file
- Create epic shape
- Create sub epic shape
- Create story shape
- Persist positions

**Collaborators:** Epic, SubEpic, Story, Position

---

### 8. **MarkdownRenderer** → StoryRenderVisitor
**Module:** `story_graph.renderers`

**Responsibilities:**
- Render epic as heading
- Render sub epic as heading
- Render story as list item
- Write to file

**Collaborators:** Epic, SubEpic, Story

---

### 9. **TextRenderer** → StoryRenderVisitor
**Module:** `story_graph.renderers`

**Responsibilities:**
- Render with indentation
- Add node prefix
- Write to file

**Collaborators:** StoryNode

---

## Decorator Pattern (Rendering Metadata)

### 10. **RenderedNode** → StoryNode (Decorator)
**Module:** `story_graph.rendered`

**Responsibilities:**
- Delegate to wrapped node
- Store position data
- Store layout data
- Store formatting data
- Trigger re-render

**Collaborators:** StoryNode, Position, Layout, Format, StoryRenderVisitor

---

## Value Objects

### 11. **Position**
**Module:** `story_graph.layout`

**Responsibilities:**
- Calculate relative position
- Serialize to dict

**Collaborators:** Parent

---

### 12. **Layout**
**Module:** `story_graph.layout`

**Responsibilities:**
- Calculate node dimensions
- Calculate spacing

**Collaborators:** Parent, Siblings

---

## CLI Adapter

### 13. **CLIAdapter**
**Module:** `cli.story_graph_commands`

**Responsibilities:**
- Parse create epic command
- Parse create sub epic command
- Parse create story command
- Parse create from json command
- Parse save command
- Return validation errors

**Collaborators:** StoryMap, SubEpic, Story

---

## Domain Rules

1. **StoryNode provides abstract interface** - All node types must implement `accept(visitor)`
2. **Hierarchy rules enforced by SubEpic** - No mixing sub-epics and stories at same level
3. **StoryMap owns persistence** - Nodes trigger updates but don't directly save
4. **Visitor pattern enables multiple output formats** - Without modifying node classes
5. **RenderedNode uses decorator pattern** - Wraps existing nodes without changing interface
6. **Position and Layout are value objects** - Immutable and compared by value
7. **CLIAdapter translates syntax** - Delegates all logic to StoryMap API

---

## Design Patterns Applied

| Pattern | Concepts | Purpose |
|---------|----------|---------|
| **Composite** | StoryNode, Epic, SubEpic, Story | Tree structure with uniform interface |
| **Visitor** | StoryRenderVisitor, DrawIORenderer, MarkdownRenderer, TextRenderer | Multiple rendering formats without modifying nodes |
| **Decorator** | RenderedNode | Add layout/position metadata to existing nodes |
| **Adapter** | CLIAdapter | Translate CLI syntax to StoryMap API |
| **Value Object** | Position, Layout | Immutable data with value-based equality |
| **Aggregate Root** | StoryMap | Single entry point for persistence |

---

## Collaboration Map

```
StoryMap (Root)
    ├─> Epic[]
    │   └─> SubEpic[]
    │       ├─> SubEpic[] (nested)
    │       └─> Story[]
    │
    ├─> StoryRenderVisitor (accepts)
    │   ├─> DrawIORenderer
    │   ├─> MarkdownRenderer
    │   └─> TextRenderer
    │
    └─> save/load JSON

StoryRenderVisitor
    ├─> visit(StoryMap)
    ├─> visit(Epic)
    ├─> visit(SubEpic)
    └─> visit(Story)
        └─> creates RenderedNode
            └─> stores Position + Layout

CLIAdapter
    └─> wraps StoryMap API
        ├─> create_epic()
        ├─> create_sub_epic()
        ├─> create_story()
        ├─> create_epic_from_dict()
        └─> save()
```

---

## Module Organization

```
story_graph/
    nodes.py           - StoryNode, Epic, SubEpic, Story, StoryMap
    renderers.py       - StoryRenderVisitor, MarkdownRenderer, TextRenderer
    rendered.py        - RenderedNode
    layout.py          - Position, Layout

synchronizers/
    story_io/
        renderers.py   - DrawIORenderer

cli/
    story_graph_commands.py - CLIAdapter
```

---

## Key Architectural Decisions

1. **Common Node API**: All node types inherit from `StoryNode` with uniform traversal interface
2. **Visitor Pattern**: Enable multiple render formats (DrawIO, Markdown, Text) without modifying node classes
3. **Decorator Pattern**: `RenderedNode` wraps nodes to add layout data without changing original interface
4. **Separation of Concerns**: Nodes handle structure, Visitors handle rendering, Adapters handle CLI
5. **Aggregate Root**: `StoryMap` is single entry point for persistence operations
6. **Immutable Layout Data**: Position and Layout are value objects for predictable behavior
