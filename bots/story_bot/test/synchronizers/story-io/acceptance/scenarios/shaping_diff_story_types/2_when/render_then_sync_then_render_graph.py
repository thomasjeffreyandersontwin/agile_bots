"""
Render then sync then render graph workflow execution.

WHEN: Story graph is rendered to DrawIO, synced back to JSON, then rendered again

UNIQUE TO THIS WORKFLOW:
- Executes render  sync  render workflow (round-trip test)
- Uses new format (sub_epics, connector, acceptance_criteria)
- Tests round-trip preservation of story graph data
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

# Import from given folder
scenario_dir = when_dir.parent
given_dir = scenario_dir / "1_given"

def render_then_sync_then_render_graph():
    """Render story graph to DrawIO, sync back to JSON, then render again."""
    # Paths
    then_dir = scenario_dir / "3_then"
    
    # Get input files from given
    story_graph_path = given_dir / "story-graph-different-story-types.json"
    
    # Output files - all actuals go to 3_then folder
    then_dir.mkdir(parents=True, exist_ok=True)
    rendered1_path = then_dir / "actual-first-render.drawio"
    synced_json_path = then_dir / "actual-synced-story-graph.json"
    rendered2_path = then_dir / "actual-second-render.drawio"
    
    print(f"\n{'='*80}")
    print("WHEN: Render story graph to DrawIO, sync back to JSON, then render again")
    print(f"{'='*80}")
    print(f"Story graph: {story_graph_path}")
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    # Step 1: Render story graph to DrawIO (first render, no layout)
    print(f"\n1. Rendering story graph to DrawIO (first render, no layout)...")
    import json
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    StoryIODiagram.render_outline_from_graph(
        story_graph=story_graph,
        output_path=rendered1_path,
        layout_data=None
    )
    print(f"   [OK] First render saved to: {rendered1_path}")
    
    # Step 2: Sync from DrawIO back to JSON
    print(f"\n2. Syncing from DrawIO back to JSON...")
    diagram = StoryIODiagram(drawio_file=rendered1_path)
    diagram.synchronize_outline(
        drawio_path=rendered1_path,
        original_path=story_graph_path,
        output_path=synced_json_path,
        generate_report=True
    )
    diagram.save_story_graph(synced_json_path)
    print(f"   [OK] Synced story graph saved to: {synced_json_path}")
    
    # Load extracted layout (layout file is generated during sync)
    # Layout file is saved in the same directory as synced_json_path
    from story_graph_layout_helper import find_extracted_layout, load_layout_data
    extracted_layout_path = synced_json_path.parent / f"{synced_json_path.stem}-layout.json"
    layout_data = None
    if extracted_layout_path:
        layout_data = load_layout_data(extracted_layout_path)
        print(f"   [OK] Extracted layout from: {extracted_layout_path}")
    else:
        print(f"   [WARN] Layout file not found, rendering without layout")
    
    # Step 3: Render synced JSON to DrawIO again (with layout)
    print(f"\n3. Rendering synced JSON to DrawIO again (with layout)...")
    with open(synced_json_path, 'r', encoding='utf-8') as f:
        synced_graph = json.load(f)
    StoryIODiagram.render_outline_from_graph(
        story_graph=synced_graph,
        output_path=rendered2_path,
        layout_data=layout_data
    )
    print(f"   [OK] Second render saved to: {rendered2_path}")
    
    print(f"\n{'='*80}")
    print("[OK] Workflow execution completed")
    print(f"{'='*80}")
    print(f"First render:  {rendered1_path}")
    print(f"Synced JSON:   {synced_json_path}")
    print(f"Second render: {rendered2_path}")
    
    return True

if __name__ == '__main__':
    import sys
    import traceback
    try:
        success = render_then_sync_then_render_graph()
        if not success:
            print("[ERROR] Workflow returned False", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Workflow execution failed: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
