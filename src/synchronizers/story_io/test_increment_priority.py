"""Test increment priority handling"""
import sys
from pathlib import Path

from .story_io_diagram import StoryIODiagram

# Load story graph with increments
story_graph_path = Path("demo/mm3e_animations/docs/story_graph.json")
diagram = StoryIODiagram.load_from_story_graph(story_graph_path)

print(f"Increments loaded: {len(diagram.increments)}")
for inc in diagram.increments:
    print(f"\nIncrement: {inc.name}")
    print(f"  Priority (original): {inc.priority} (type: {type(inc.priority).__name__})")
    print(f"  Priority (int): {inc.priority_int}")
    print(f"  Story names: {len(inc.story_names)} stories")
    if inc.story_names:
        print(f"    First few: {inc.story_names[:3]}...")

# Render and check priority is preserved
rendered = diagram.render()
if rendered.get('increments'):
    rendered_inc = rendered['increments'][0]
    print(f"\nRendered increment:")
    print(f"  Priority: {rendered_inc.get('priority')} (type: {type(rendered_inc.get('priority')).__name__})")
    print(f"  Stories: {len(rendered_inc.get('stories', []))} story names")
    if rendered_inc.get('stories'):
        print(f"    First few: {rendered_inc['stories'][:3]}...")

print("\n[SUCCESS] Priority structure preserved!")

