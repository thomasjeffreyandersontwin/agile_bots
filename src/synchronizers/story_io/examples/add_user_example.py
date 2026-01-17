"""
Add user "GM" to "Load Power" story and re-render.

This script:
1. Loads the story graph
2. Finds the "Load Power" story (or similar)
3. Adds "GM" user to it
4. Re-renders the DrawIO file
"""

import sys
import json
import argparse
from pathlib import Path

from ..story_io_diagram import StoryIODiagram
from .render_example import adapt_story_graph

# Parse arguments
parser = argparse.ArgumentParser(description='Add GM user to a story and re-render')
parser.add_argument('story_graph_path', nargs='?', help='Optional path to story_graph.json')
args = parser.parse_args()

from bots.base_bot.src.state.workspace import get_workspace_directory
workspace_root = get_workspace_directory()
if args.story_graph_path:
    story_graph_path = Path(args.story_graph_path)
else:
    story_graph_path = workspace_root / "demo" / "mm3e_animations" / "docs" / "story_graph.json"

print(f"Loading: {story_graph_path}")

# Load the story graph
with open(story_graph_path, 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Adapt to our format
adapted_data = adapt_story_graph(original_data)

# Load into diagram
diagram = StoryIODiagram()
diagram._load_from_story_graph_format(adapted_data)

# Find "Load Power" story - search for it
load_power_story = None
for epic in diagram.epics:
    for feature in epic.features:
        for story in feature.stories:
            if 'load' in story.name.lower() and 'power' in story.name.lower():
                load_power_story = story
                print(f"Found story: {story.name}")
                break
        if load_power_story:
            break
    if load_power_story:
        break

# If not found, try "Receive Power Characteristics" (first story in first feature)
if not load_power_story:
    print("'Load Power' story not found, checking first story in first feature...")
    if diagram.epics:
        first_epic = diagram.epics[0]
        if first_epic.features:
            first_feature = first_epic.features[0]
            if first_feature.stories:
                load_power_story = first_feature.stories[0]
                print(f"Using first story: {load_power_story.name}")

if load_power_story:
    # Add "GM" user
    print(f"\nAdding 'GM' user to story: {load_power_story.name}")
    load_power_story.add_user('GM')
    print(f"Story users: {load_power_story.users}")
    
    # Re-render
    output_path = story_graph_path.parent / "story-map-outline.drawio"
    print(f"\nRe-rendering to: {output_path}")
    
    result = diagram.render_outline(output_path=output_path)
    
    print(f"\n[SUCCESS] Re-rendered with GM user!")
    print(f"Output: {output_path}")
    print(f"Epics: {result['summary'].get('epics', 0)}")
else:
    print("\n[ERROR] Could not find 'Load Power' story")
    print("Available stories:")
    for epic in diagram.epics:
        for feature in epic.features:
            for story in feature.stories:
                print(f"  - {story.name}")

