"""
Exploration render with layout preservation workflow execution.

WHEN: Render diagram and syncing re-render diagram

UNIQUE TO THIS WORKFLOW:
- Executes exploration rendering workflow (render → sync → render with layout)
- Uses render_exploration_from_graph (exploration mode, only stories with Steps)
- Renders twice: first without layout (calculate positions), second with layout (preserve positions)
- Preserves layout when re-rendering in exploration mode
- Ensures acceptance criteria positioning in exploration mode
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
from story_graph_layout_helper import load_story_graph, load_layout_data, find_extracted_layout

def run_test():
    """Execute the exploration render workflow."""
    # Paths
    scenario_dir = when_dir.parent
    given_dir = scenario_dir / "1_given"
    then_dir = scenario_dir / "3_then"
    
    # Input files
    story_graph_path = given_dir / "story-graph-with-acceptance-criteria.json"
    layout_path = given_dir / "story-outline-stories-right-beside-each-other-layout.json"
    
    # Output files
    then_dir.mkdir(parents=True, exist_ok=True)
    first_render_path = then_dir / "actual-first-render-story-exploration.drawio"
    second_render_path = then_dir / "actual-second-render-story-exploration.drawio"
    
    print(f"\n{'='*80}")
    print("WHEN: Render diagram and syncing re-render diagram")
    print(f"{'='*80}")
    print(f"Story graph: {story_graph_path}")
    print(f"Layout: {layout_path}")
    
    # Load story graph
    story_graph = load_story_graph(story_graph_path)
    
    # Load layout data (provided layout, used as fallback if extraction fails)
    provided_layout_data = load_layout_data(layout_path)
    if provided_layout_data:
        print(f"   [OK] Loaded layout data from: {layout_path}")
    else:
        print(f"   [WARN] Layout file not found: {layout_path}")
    
    # Step 1: First render without layout (calculate positions from scratch)
    print(f"\n1. First render (without layout - calculate positions from scratch)...")
    render_result1 = StoryIODiagram.render_exploration_from_graph(
        story_graph=story_graph,
        output_path=first_render_path,
        layout_data=None,  # No layout for first render
        scope=None
    )
    print(f"   [OK] First render saved to: {first_render_path}")
    
    # Step 2: Sync from first render to extract layout
    print(f"\n2. Syncing from first render to extract layout...")
    temp_synced_path = then_dir / "temp-synced.json"
    
    diagram = StoryIODiagram(drawio_file=first_render_path)
    diagram.synchronize_outline(
        drawio_path=first_render_path,
        original_path=story_graph_path,
        output_path=temp_synced_path,
        generate_report=True
    )
    
    # Load extracted layout from first render
    extracted_layout_path = find_extracted_layout(temp_synced_path)
    extracted_layout_data = None
    if extracted_layout_path:
        extracted_layout_data = load_layout_data(extracted_layout_path)
        print(f"   [OK] Extracted layout from first render: {extracted_layout_path}")
    else:
        print(f"   [WARN] Could not extract layout from first render")
        # Use provided layout as fallback
        extracted_layout_data = provided_layout_data
    
    # Step 3: Second render with layout (preserve positions)
    print(f"\n3. Second render (with layout - preserve positions)...")
    render_result2 = StoryIODiagram.render_exploration_from_graph(
        story_graph=story_graph,
        output_path=second_render_path,
        layout_data=extracted_layout_data,  # Use extracted layout
        scope=None
    )
    print(f"   [OK] Second render saved to: {second_render_path}")
    
    # Cleanup temp files
    if temp_synced_path.exists():
        temp_synced_path.unlink()
    if extracted_layout_path.exists():
        extracted_layout_path.unlink()
    
    print(f"\n{'='*80}")
    print("[OK] Workflow execution completed")
    print(f"{'='*80}")
    print(f"First render:  {first_render_path}")
    print(f"Second render: {second_render_path}")

if __name__ == '__main__':
    try:
        run_test()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

