"""
Render diagram from story graph.

WHEN: Story graph is rendered to DrawIO

WHAT THIS TEST DOES:
- Loads story graph from given data
- Renders DrawIO diagram from the story graph
- Outputs actual DrawIO for comparison with expected
- Simple test: render and compare - how close is it to expected?
"""
import sys
from pathlib import Path

# Add parent directories to path
when_dir = Path(__file__).parent
scenario_dir = when_dir.parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))
sys.path.insert(0, str(scenario_dir.parent))  # Add scenarios directory for story_graph_layout_helper

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram
from story_graph_layout_helper import load_story_graph

# Import from given folder
given_dir = scenario_dir / "1_given"
sys.path.insert(0, str(given_dir))
import importlib.util
spec = importlib.util.spec_from_file_location("load_story_graph_and_drawio_data", given_dir / "load_story_graph_and_drawio_data.py")
given_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(given_data)

def render_diagram_from_story_graph():
    """Render DrawIO diagram from story graph."""
    # Paths
    given_dir = scenario_dir / "1_given"
    then_dir = scenario_dir / "3_then"
    
    # Get input files from given
    story_graph_path = given_data.get_story_graph_path()
    
    # Output files
    then_dir.mkdir(parents=True, exist_ok=True)
    rendered_drawio_path = then_dir / "actual-story-outline.drawio"
    
    print(f"\n{'='*80}")
    print("WHEN: Story graph is rendered to DrawIO")
    print(f"{'='*80}")
    print(f"Story graph: {story_graph_path}")
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    # Load story graph
    print(f"\n1. Loading story graph...")
    story_graph = load_story_graph(story_graph_path)
    print(f"   [OK] Story graph loaded")
    
    # Render DrawIO from story graph
    print(f"\n2. Rendering DrawIO diagram...")
    StoryIODiagram.render_outline_from_graph(
        story_graph=story_graph,
        output_path=rendered_drawio_path
    )
    print(f"   [OK] Rendered DrawIO saved to: {rendered_drawio_path}")
    
    print(f"\n{'='*80}")
    print("[OK] Diagram rendered successfully")
    print(f"{'='*80}")
    print(f"Rendered: {rendered_drawio_path}")
    print(f"\nNext step: Compare with expected diagram in 3_then/")
    
    return True

if __name__ == '__main__':
    try:
        success = render_diagram_from_story_graph()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Rendering failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

