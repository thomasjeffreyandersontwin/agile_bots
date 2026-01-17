"""Test full cycle: load -> render -> save -> reload to verify priority preservation"""
import sys
import json
from pathlib import Path

from .story_io_diagram import StoryIODiagram

# Load story graph
story_graph_path = Path("demo/mm3e_animations/docs/story_graph.json")
print(f"Loading: {story_graph_path}")
diagram = StoryIODiagram.load_from_story_graph(story_graph_path)

original_inc = diagram.increments[0]
print(f"\nOriginal increment:")
print(f"  Name: {original_inc.name}")
print(f"  Priority: {original_inc.priority} ({type(original_inc.priority).__name__})")
print(f"  Story names count: {len(original_inc.story_names)}")

# Render and save
rendered = diagram.render()
output_path = Path("demo/mm3e_animations/docs/story_graph_test.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(rendered, f, indent=2, ensure_ascii=False)

print(f"\nSaved rendered data to: {output_path}")

# Reload and verify
diagram2 = StoryIODiagram.load_from_story_graph(output_path)
reloaded_inc = diagram2.increments[0]

print(f"\nReloaded increment:")
print(f"  Name: {reloaded_inc.name}")
print(f"  Priority: {reloaded_inc.priority} ({type(reloaded_inc.priority).__name__})")
print(f"  Story names count: {len(reloaded_inc.story_names)}")

# Verify
if original_inc.priority == reloaded_inc.priority:
    print("\n[SUCCESS] Priority preserved correctly!")
else:
    print(f"\n[ERROR] Priority mismatch: {original_inc.priority} != {reloaded_inc.priority}")

if original_inc.story_names == reloaded_inc.story_names:
    print("[SUCCESS] Story names preserved correctly!")
else:
    print(f"[ERROR] Story names mismatch!")

# Clean up
output_path.unlink()
print(f"\nCleaned up test file: {output_path}")

