# Story IO - Complete Documentation

Object-oriented story map domain model with DrawIO rendering and synchronization capabilities.

## Overview

Story IO provides a complete domain model for representing story maps (Epics, Sub-Epics, Stories, Users, Increments) with full CRUD operations, rendering to DrawIO XML format, and synchronizing from DrawIO files back to JSON. Designed following Domain-Driven Design principles with comprehensive BDD test coverage.

**Key Capabilities:**
- Render story graphs to DrawIO diagrams (outline or increments)
- Synchronize from DrawIO files back to story graphs
- Search and manipulate story map components
- Merge synchronized data with original graphs
- Full CRUD operations on all components
- MCP server integration for tool-based access

---

## Folder Structure

```
story_io/
├── __init__.py                    # Package exports (StoryIODiagram, Epic, Feature, etc.)
│
├── story_io_component.py          # Base class for all components
├── story_io_diagram.py            # Main diagram orchestrator
├── story_io_epic.py               # Epic domain component
├── story_io_feature.py            # Feature domain component
├── story_io_story.py              # Story domain component
├── story_io_user.py               # User domain component
├── story_io_increment.py          # Increment (release) component
├── story_io_position.py           # Position and Boundary types
│
├── story_io_renderer.py           # DrawIO rendering engine wrapper
├── story_io_synchronizer.py       # DrawIO synchronization engine wrapper
├── story_io_cli.py                # Command-line interface
├── story_io_mcp_server.py         # MCP server with tools
│
├── story_map_drawio_synchronizer.py  # Legacy synchronizer (internal)
│
├── cli/                           # PowerShell wrapper and examples
│   ├── story-io.ps1               # Main PowerShell CLI wrapper
│   ├── render-examples.ps1        # Rendering examples
│   ├── sync-examples.ps1          # Synchronization examples
│   ├── search-examples.ps1        # Search examples
│   ├── merge-examples.ps1         # Merge examples
│   └── complete-workflow.ps1      # End-to-end workflow example
│
├── examples/                      # Python code examples
│   ├── render_example.py          # Basic rendering
│   ├── load_and_render_example.py # Load and render pattern
│   ├── add_user_example.py        # Add user to story
│   └── *.ps1                      # PowerShell examples (duplicates of cli/)
│
├── test/                          # Unit tests (BDD with Mamba)
│   ├── test_story_io_component.py # Base component tests
│   ├── test_story_io_position.py  # Position/Boundary tests
│   ├── test_story_io_epic.py      # Epic tests
│   ├── test_story_io_feature.py   # Feature tests
│   ├── test_story_io_story.py     # Story tests
│   ├── test_story_io_user.py      # User tests
│   └── test_story_io_increment.py # Increment tests
│
└── acceptance/                    # Acceptance tests with real files
    ├── test_acceptance.py         # Acceptance test runner
    └── scenarios/                 # Test scenarios
        ├── simple/                # Minimal story graph
        ├── complex/               # Complex multi-epic graph
        ├── single_epic/           # Single epic scenario
        ├── multiple_users/        # Multiple user scenario
        └── with_increments/       # Increments scenario
```

---

## Quick Start

### CLI (PowerShell)

```powershell
# Render outline diagram
.\cli\story-io.ps1 render-outline `
    -StoryGraph "demo/mm3e_animations/docs/story_graph.json" `
    -Output "story-map-outline.drawio"

# Render with increments (requires increments in story graph JSON)
.\cli\story-io.ps1 render-increments `
    -StoryGraph "story_graph_with_increments.json" `
    -Output "story-map-increments.drawio"
# Shows release lanes with story counts in epic/feature boxes

# Render with acceptance criteria (automatic if stories have Steps)
.\cli\story-io.ps1 render-outline `
    -StoryGraph "story_graph.json" `
    -Output "story-map-outline.drawio"
# Note: If stories have "Steps" array, acceptance criteria boxes will automatically render below stories

# Synchronize from DrawIO (auto-detects type)
.\cli\story-io.ps1 synchronize `
    -DrawIOFile "story-map-outline.drawio" `
    -Original "original.json" `
    -Output "synced.json" `
    -GenerateReport

# Search for components
.\cli\story-io.ps1 search `
    -StoryGraph "story_graph.json" `
    -Query "Power" `
    -Type "story"

# Add user to story
.\cli\story-io.ps1 add-user `
    -StoryGraph "story_graph.json" `
    -StoryName "Receive Power Characteristics" `
    -UserName "GM"

# Merge synchronized data
.\cli\story-io.ps1 merge `
    -Extracted "synced.json" `
    -Original "original.json" `
    -Output "merged.json" `
    -ReportPath "merge_report.json"

# Working with Increments
# Increments are defined in the story graph JSON structure:
# {
#   "epics": [...],
#   "increments": [
#     {
#       "name": "MVP Release",
#       "priority": 1,
#       "epics": [
#         {
#           "name": "User Management",
#           "sub_epics": [
#             {
#               "name": "User Registration",
#               "stories": [...]
#             }
#           ]
#         }
#       ]
#     }
#   ]
# }
# Then render with: render-increments command
```

### Python Code (Equivalent)

```python
from pathlib import Path
from story_io import StoryIODiagram

# Render Outline
diagram = StoryIODiagram.load_from_story_graph("story_graph.json")
result = diagram.render_outline(output_path="story-map-outline.drawio")
print(f"Rendered: {result['output_path']}")

# Render Increments
result = diagram.render_increments(output_path="story-map.drawio")

# Static method (simpler)
result = StoryIODiagram.render_outline_from_graph(
    story_graph="story_graph.json",
    output_path="story-map-outline.drawio"
)

# Synchronize from DrawIO
diagram = StoryIODiagram.sync_from_drawio("story-map-outline.drawio")
diagram.save_story_graph("synced.json")

# With report
result = diagram.synchronize_outline(
    drawio_path="story-map-outline.drawio",
    original_path="original.json",
    generate_report=True
)

# Search
stories = diagram.search_for_stories("Power")
epics = diagram.search_for_epics("Create Character")

# Add user to story
story = diagram.add_user_to_story(
    story_name="Receive Power Characteristics",
    user_name="GM",
    epic_name="Epic Name",      # Optional: narrow search
    sub_epic_name="Sub-Epic Name" # Optional: narrow search
)

# Merge synchronized with original
merged = diagram.merge_story_graphs(
    extracted_path="synced.json",
    original_path="original.json",
    output_path="merged.json"
)
```

## MCP Tools

**Current Tools:**
- `render_outline` - Render story graph (JSON) as outline DrawIO
- `render_increments` - Render story graph (JSON) with increments to DrawIO
- `synchronize_outline` - Sync from DrawIO to JSON graph
- `synchronize_increments` - Sync from DrawIO with increments to JSON graph
- `search_story_map` - Search for components in JSON graph

**Workflow Distinction:**

**Sync and Merge work with JSON graphs (intermediate format):**
- **Sync**: DrawIO → extracts to JSON graph → can save JSON or render back to DrawIO
- **Merge**: JSON graph + JSON graph → merged JSON graph (works with JSON files)
- **Render**: JSON graph → DrawIO (we build DrawIO from graphs)

**Component Management works directly with DrawIO:**
- CRUD operations modify DrawIO XML directly
- No JSON conversion needed for management operations

**Component Management (To Be Created):**

Component CRUD operations should work directly with DrawIO files:
1. Load from DrawIO
2. Modify components in DrawIO XML
3. Save back to DrawIO

Each component (Epic, Feature, Story, Increment) should have:

```
create_{component}_in_drawio      - Create new component in DrawIO
read_{component}_from_drawio     - Get component by name/ID from DrawIO
update_{component}_in_drawio      - Update component properties in DrawIO
delete_{component}_from_drawio   - Remove component from DrawIO
move_{component}_in_drawio        - Move component (reorder, change parent) in DrawIO
search_{component}_children_in_drawio - Search children of component in DrawIO
create_{component}_child_in_drawio - Add child (e.g., create_feature_epic) in DrawIO
update_{component}_child_in_drawio - Update child properties in DrawIO
delete_{component}_child_in_drawio - Remove child from DrawIO
```

**Example Tool Definitions (DrawIO-focused):**

```python
@mcp.tool()
def create_epic_in_drawio(
    drawio_path: str,
    name: str,
    x: float,
    y: float,
    width: float = 200.0,
    height: float = 60.0
) -> str:
    """Create a new epic in the DrawIO file at specified position."""
    # Load DrawIO, add epic cell, save back to DrawIO
    
@mcp.tool()
def create_feature_in_drawio(
    drawio_path: str,
    epic_name: str,
    feature_name: str,
    x: float,
    y: float,
    width: float = 150.0,
    height: float = 60.0
) -> str:
    """Create a feature under an epic in the DrawIO file."""
    # Load DrawIO, find epic, add feature cell below epic, save back
    
@mcp.tool()
def create_story_in_drawio(
    drawio_path: str,
    epic_name: str,
    feature_name: str,
    story_name: str,
    x: float,
    y: float,
    story_type: str = "user"  # "user", "system", "technical"
) -> str:
    """Create a story under a feature in the DrawIO file."""
    # Load DrawIO, find feature, add story cell below feature, save back
    
@mcp.tool()
def move_story_in_drawio(
    drawio_path: str,
    story_name: str,
    new_x: float,
    new_y: float,
    target_epic: Optional[str] = None,
    target_feature: Optional[str] = None
) -> str:
    """Move a story to a different position or parent in DrawIO."""
    # Load DrawIO, find story cell, update position/parent, save back
    
@mcp.tool()
def delete_component_in_drawio(
    drawio_path: str,
    component_type: str,  # "epic", "feature", "story"
    component_name: str
) -> str:
    """Delete a component from the DrawIO file."""
    # Load DrawIO, find component cell, remove it and children, save back
    
@mcp.tool()
def update_story_type_in_drawio(
    drawio_path: str,
    story_name: str,
    story_type: str  # "user", "system", "technical"
) -> str:
    """Update story type (affects color in DrawIO)."""
    # Load DrawIO, find story cell, update fillColor/style, save back
    
@mcp.tool()
def add_user_to_story_in_drawio(
    drawio_path: str,
    story_name: str,
    user_name: str,
    x: float,
    y: float
) -> str:
    """Add a user label above a story in DrawIO."""
    # Load DrawIO, find story, add user cell above it, save back
```

**Key Principles for Component Management:**
- CRUD operations work directly with DrawIO XML files
- Changes are made to DrawIO cells (mxCell elements)
- Position and styling are managed in DrawIO coordinates
- No intermediate JSON conversion needed for management operations

**Note:** Sync and Merge operations still use JSON graphs as intermediate format:
- Sync: DrawIO → extracts to JSON graph → can save JSON or render back to DrawIO
- Merge: JSON graph + JSON graph → merged JSON graph
- Render: JSON graph → DrawIO (we build DrawIO from graphs)
- Tests should verify DrawIO XML structure, not JSON structure

**Start MCP Server:**

```bash
python -m story_io.story_io_mcp_server
```

---

## Usage Guides

### Rendering

**Render Outline (Epics → Sub-Epics → Stories):**

```python
# Method 1: Static method
result = StoryIODiagram.render_outline_from_graph(
    story_graph="story_graph.json",
    output_path="outline.drawio"
)

# Method 2: Instance method
diagram = StoryIODiagram.load_from_story_graph("story_graph.json")
result = diagram.render_outline(output_path="outline.drawio")

# Method 3: With layout data
layout = {"epics": [{"name": "Epic1", "x": 100, "y": 100}]}
result = diagram.render_outline(output_path="outline.drawio", layout_data=layout)
```

**Render Increments (Releases with stories):**

```python
result = StoryIODiagram.render_increments_from_graph(
    story_graph="story_graph.json",
    output_path="increments.drawio"
)

# Story graph must include increments array:
# {
#   "epics": [...],
#   "increments": [
#     {
#       "name": "MVP Release",
#       "priority": 1,
#       "epics": [
#         {
#           "name": "User Management",
#           "sub_epics": [
#             {
#               "name": "User Registration",
#               "stories": [...]
#             }
#           ]
#         }
#       ]
#     }
#   ]
# }
```

**Render with Acceptance Criteria (Exploration Mode):**

Acceptance criteria are automatically rendered when stories have a `Steps` array:

```python
# Automatic - outline mode detects Steps and renders acceptance criteria
result = StoryIODiagram.render_outline_from_graph(
    story_graph="story_graph.json",  # Stories with "Steps" array
    output_path="story-map-outline.drawio"
)

# Or explicitly render in exploration mode
diagram = StoryIODiagram.load_from_story_graph("story_graph.json")
result = diagram.render_exploration(output_path="exploration.drawio")
```

**Story Graph Structure with Acceptance Criteria:**

```json
{
  "epics": [{
    "features": [{
      "stories": [{
        "name": "User creates account",
        "Steps": [
          "Customer enters credit card number",
          "Customer enters expiration date",
          "System validates card information"
        ]
      }]
    }]
  }]
}
```

**Increments Structure:**

Increments represent marketable releases. They reference epics, sub-epics, and stories that are part of that release:

```json
{
  "epics": [
    {
      "name": "User Management",
      "features": [
        {
          "name": "User Registration",
          "stories": [
            {
              "name": "User creates account",
              "sequential_order": 1
            }
          ]
        },
        {
          "name": "User Authentication",
          "stories": [
            {
              "name": "User logs in",
              "sequential_order": 1
            }
          ]
        }
      ]
    }
  ],
  "increments": [
    {
      "name": "MVP Release",
      "priority": 1,
      "epics": [
        {
          "name": "User Management",
          "features": [
            {
              "name": "User Registration",
              "stories": [
                {
                  "name": "User creates account"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "Feature Release",
      "priority": 2,
      "epics": [
        {
          "name": "User Management",
          "features": [
            {
              "name": "User Registration",
              "stories": [
                {
                  "name": "User creates account"
                }
              ]
            },
            {
              "name": "User Authentication",
              "stories": [
                {
                  "name": "User logs in"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Key Points:**
- Increments reference epics/sub-epics/stories by name (they must exist in the `epics` array)
- Each increment defines which stories are included in that release
- Increments are rendered as separate lanes with story counts displayed in top-right of epic/feature boxes
- Priority determines ordering (1 = first, 2 = second, etc.)

### Synchronization

**Sync from DrawIO (Auto-detect Type):**

```python
# Auto-detects outline vs increments from filename or content
diagram = StoryIODiagram.sync_from_drawio("story-map-outline.drawio")
diagram.save_story_graph("synced.json")

# With original for comparison
result = diagram.synchronize_outline(
    drawio_path="outline.drawio",
    original_path="original.json",
    generate_report=True
)
print(result['report'])  # Detailed sync report
```

**Sync Report:**

Reports include:
- Before/after counts (epics, features, stories)
- Component changes (added, removed, modified)
- Comparison with original (if provided)

### Merging

**Merge Synchronized Data with Original:**

```python
# Generate merge report first
report = diagram.generate_merge_report(
    extracted_path="synced.json",
    original_path="original.json"
)

# Apply merge (preserves Steps, metadata from original)
merged = diagram.merge_story_graphs(
    extracted_path="synced.json",
    original_path="original.json",
    output_path="merged.json"
)
```

**Merge Report Structure:**

```json
{
  "extracted": {...},
  "original": {...},
  "changes": {
    "stories_added": [...],
    "stories_removed": [...],
    "stories_modified": [...]
  },
  "preserved_from_original": {
    "steps": [...],
    "metadata": {...}
  }
}
```

### Searching

**Search Components:**

```python
# Search any component type
results = diagram.search_for_any("Power")

# Search specific types
epics = diagram.search_for_epics("Create")
sub_epics = diagram.search_for_features("Identity")  # Returns Feature objects representing sub-epics
stories = diagram.search_for_stories("User enters")

# Search returns list of component objects
for story in stories:
    print(f"{story.name} in {story.parent.name}")
```

### Component Manipulation

**Add User to Story:**

```python
story = diagram.add_user_to_story(
    story_name="Receive Power",
    user_name="GM",
    epic_name="Power Management",      # Optional: narrow search
    sub_epic_name="Load Powers"         # Optional: narrow search
)
```

**Move Components:**

```python
# Move story before another story
story.move_before(target_story)

# Change parent (e.g., sub-epic to new epic)
sub_epic.change_parent(new_epic, target_sub_epic)  # Optional: insert before target

# Reorder siblings
epic.move_before(target_epic)
```

---

## Domain Model

### Component Hierarchy

```
StoryIODiagram
├── Epic
│   ├── Sub-Epic (Feature class)
│   │   ├── Story
│   │   │   └── User (bidirectional relationship)
│   │   └── Story...
│   └── Sub-Epic (Feature class)...
└── Increment
    ├── Epic (references)
    ├── Sub-Epic (references)
    └── Story (references by name)
```

### Core Classes

**StoryIOComponent** (Base Class)
- Properties: `name`, `sequential_order`, `position`, `boundary`, `parent`, `children`
- Methods: `move_before()`, `change_parent()`, `search_for_all_children()`, `determine_children()`
- Abstract: `synchronize()`, `render()`, `compare()`

**StoryIODiagram**
- Main orchestrator for entire story map
- Manages epics, sub-epics, stories, increments
- Provides rendering and synchronization entry points
- Methods: `render_outline()`, `render_increments()`, `synchronize_outline()`, `synchronize_increments()`, `search_for_*()`, `add_user_to_story()`, `merge_story_graphs()`

**Epic**
- Contains sub-epics and stories
- Methods: `add_sub_epic()`, `remove_sub_epic()`, `sub_epics`, `stories`

**Feature** (represents Sub-Epic)
- Contains stories
- Tracks `story_count`
- Methods: `stories`

**Story**
- Associates with users (bidirectional)
- Contains `steps` (list of story steps)
- Properties: `users`, `vertical_order`, `flag`, `story_type` ("user", "system", "technical")
- Methods: `add_user()`, `remove_user()`, `make_optional_to()`

**User**
- Bidirectional relationship with stories
- Methods: `add_story()`, `remove_story()`

**Increment**
- Represents marketable release
- Contains references to epics, sub-epics, stories
- Properties: `priority` (can be "NOW", "LATER", "SOON" or int), `story_names` (list of story names), `relative_size`, `approach`, `focus`
- Stories stored by name reference (not objects)

**Position & Boundary** (Dataclasses)
- `Position(x, y)` - Immutable position
- `Boundary(x, y, width, height)` - Immutable rectangle
- Methods: `distance()`, `contains()`, `overlaps()`

### Component Properties Summary

| Component | Key Properties | Key Methods |
|-----------|---------------|-------------|
| **StoryIODiagram** | `epics`, `increments` | `render_outline()`, `sync_from_drawio()`, `search_for_*()` |
| **Epic** | `features` (sub-epics), `stories` | `add_feature()`, `remove_feature()` |
| **Feature** (Sub-Epic) | `stories`, `story_count` | - |
| **Story** | `users`, `steps`, `vertical_order` | `add_user()`, `remove_user()` |
| **User** | `stories` | `add_story()`, `remove_story()` |
| **Increment** | `priority`, `story_names` | - |

---

## Testing

### Running Tests

**Unit Tests (BDD with Mamba):**

```bash
# Run all unit tests
python -m mamba.cli agile_bot/bots/story_bot/src/story_io/test/

# Run specific test file
python -m mamba.cli agile_bot/bots/story_bot/src/story_io/test/test_story_io_component.py

# With verbose output
python -m mamba.cli --verbose agile_bot/bots/story_bot/src/story_io/test/
```

**Test Structure (BDD Pattern):**

```python
from expects import expect, be_true, equal
from mamba import description, context, it

with description("StoryIOComponent"):
    with context("when creating a component"):
        with it("should have a name"):
            component = StoryIOComponent("Test")
            expect(component.name).to(equal("Test"))
```

**Test Files:**
- `test_story_io_component.py` - Base component (hierarchy, search, position)
- `test_story_io_position.py` - Position/Boundary math
- `test_story_io_epic.py` - Epic operations (add/remove sub-epics)
- `test_story_io_feature.py` - Sub-epic operations (Feature class)
- `test_story_io_story.py` - Story operations (users, steps)
- `test_story_io_user.py` - User-story relationships
- `test_story_io_increment.py` - Increment (priority, story references)

**Testing DrawIO Management:**
- Tests for DrawIO component management should verify DrawIO XML structure
- Test that components are correctly added/removed/modified in DrawIO cells
- Verify positions, styling, and relationships in DrawIO XML
- Test round-trip: DrawIO → modify → DrawIO (preserve layout)

**Example Unit Test:**

```python
from expects import expect, equal
from mamba import description, context, it
from story_io import Epic, Feature

with description("Epic"):
    with context("when adding a feature"):
        with it("should add feature to children"):
            epic = Epic("Test Epic")
            feature = Feature("Test Sub-Epic")  # Feature class represents sub-epic
            epic.add_feature(feature)
            expect(len(epic.features)).to(equal(1))
            expect(feature.parent).to(equal(epic))
```

### Acceptance Tests

**Run Acceptance Tests:**

```bash
cd agile_bot/bots/story_bot/src/story_io/acceptance
python test_acceptance.py
```

**What They Do:**
1. Load scenario JSON from `scenarios/` directory
2. Render to DrawIO file
3. Sync back from DrawIO
4. Generate comparison report
5. Output files for visual verification

**Test Scenarios:**
- `simple/` - Minimal story graph (one epic, one feature, one story)
- `complex/` - Multiple epics, sub-epics, stories
- `single_epic/` - Single epic with multiple sub-epics
- `multiple_users/` - Stories with multiple users
- `with_increments/` - Story graph with increment definitions

**Output Files:**
- `acceptance/outputs/` directory contains (flat structure with prefixed names):
  - `{scenario}_rendered.drawio` - Generated DrawIO file (open in DrawIO)
  - `{scenario}_synced.json` - Synced back story graph
  - `{scenario}_comparison.json` - Before/after comparison
  - `{scenario}_layout.json` - Layout data (for round-trip rendering)
  - `{scenario}_round_trip_rendered.drawio` - Second render using layout (verifies position preservation)

**Example Acceptance Test Output:**

```
Running Scenario: simple
Loading story graph: scenarios/simple/story_graph.json
Rendering to: outputs/simple/rendered.drawio
Syncing from: outputs/simple/rendered.drawio
Comparison:
  Epics: 1 → 1 (match)
  Sub-Epics: 1 → 1 (match)
  Stories: 1 → 1 (match)
[PASS] All components match
```

**Visual Verification:**
1. Open `outputs/{scenario}/rendered.drawio` in DrawIO
2. Verify layout, positions, labels
3. Check `comparison_report.json` for data integrity
4. Open `synced.json` to verify round-trip data preservation

---

## Additional Resources

- **PowerShell Examples**: `cli/*.ps1` - Complete workflow examples
- **Python Examples**: `examples/*.py` - Code patterns and recipes
- **CLI Reference**: Run `.\cli\story-io.ps1` without arguments for help
- **Python CLI**: Run `python -m story_io.story_io_cli --help` for options
