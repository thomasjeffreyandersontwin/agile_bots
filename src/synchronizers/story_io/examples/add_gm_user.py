"""
Add user "GM" to "Load Power" story (which is the first story in the first feature).

This script:
1. Loads the story graph from demo/mm3e_animations/docs/story_graph.json
2. Finds the first story in the first feature
3. Adds "GM" user to it
4. Re-renders the DrawIO file
"""

import sys
import json
import argparse
from pathlib import Path

from ..story_io_diagram import StoryIODiagram

# Parse arguments
parser = argparse.ArgumentParser(description='Add GM user to first story and re-render')
parser.add_argument('--story_graph', help='Optional path to story_graph.json')
args = parser.parse_args()

from bots.base_bot.src.state.workspace import get_workspace_directory
workspace_root = get_workspace_directory()
if args.story_graph:
    story_graph_path = Path(args.story_graph)
else:
    story_graph_path = workspace_root / "demo" / "mm3e_animations" / "docs" / "story_graph.json"
output_path = story_graph_path.parent / "story-map-outline.drawio"

print(f"Loading story graph: {story_graph_path}")
diagram = StoryIODiagram.load_from_story_graph(story_graph_path)

# Find the first story in the first feature (which appears as "Load Power" in the rendered DrawIO)
# This is "Receive Power Characteristics" based on the JSON
if diagram.epics and diagram.epics[0].features and diagram.epics[0].features[0].stories:
    first_story = diagram.epics[0].features[0].stories[0]
    print(f"\nFound story: '{first_story.name}'")
    print(f"Current users: {first_story.users}")
    
    # Add "GM" user
    print(f"\nAdding 'GM' user to story...")
    first_story.add_user('GM')
    print(f"Story users after adding GM: {first_story.users}")
    
    # Re-render
    print(f"\nRe-rendering to: {output_path}")
    result = diagram.render_outline(output_path=output_path)
    
    print(f"\n[SUCCESS] Re-rendered with GM user!")
    print(f"Output: {output_path}")
    print(f"Epics: {result['summary'].get('epics', 0)}")
    print(f"\nThe 'GM' user should now appear above '{first_story.name}' in the DrawIO file.")
else:
    print("[ERROR] Could not find first story in first feature")

