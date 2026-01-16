"""
Render then sync then render graph workflow execution.

WHEN: Story graph is rendered to DrawIO, synced back to JSON, then rendered again

UNIQUE TO THIS WORKFLOW:
- Executes render → sync → render workflow (round-trip test)
- Uses render_outline_from_graph (outline mode, all stories)
- Renders twice: first without layout, second with extracted layout
- Tests round-trip preservation of story graph data
"""
import sys
import json
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

# Import from given folder
given_dir = scenario_dir / "1_given"
sys.path.insert(0, str(given_dir))
import importlib.util
spec = importlib.util.spec_from_file_location("load_story_graph_data", given_dir / "load_story_graph_data.py")
given_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(given_data)

def render_then_sync_then_render_graph():
    """Render story graph to DrawIO, sync back to JSON, then render again."""
    # Paths
    then_dir = scenario_dir / "3_then"
    
    # Get input files from given
    story_graph_path = given_data.get_story_graph_path()
    story_graph = given_data.get_story_graph()
    
    # Output files
    then_dir.mkdir(parents=True, exist_ok=True)
    rendered1_path = then_dir / "actual-first-render.drawio"
    synced_json_path = then_dir / "actual-synced-story-graph.json"
    rendered2_path = then_dir / "actual-second-render.drawio"
    merge_report_path = then_dir / "actual-synced-story-graph-merge-report.json"
    # Merge writes back to original file (as a copy in then_dir for testing)
    merged_original_path = then_dir / story_graph_path.name
    
    print(f"\n{'='*80}")
    print("WHEN: Render story graph to DrawIO, sync back to JSON, then render again")
    print(f"{'='*80}")
    print(f"Story graph: {story_graph_path}")
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph not found: {story_graph_path}")
        return False
    
    # Step 1: Render story graph to DrawIO (first render, no layout)
    print(f"\n1. Rendering story graph to DrawIO (first render, no layout)...")
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
    # Note: synchronize_outline already writes the file, so we don't need save_story_graph
    # (save_story_graph would overwrite with diagram.render() which uses internal structure)
    print(f"   [OK] Synced story graph saved to: {synced_json_path}")
    
    # Load extracted layout (layout file is generated during sync)
    extracted_layout_path = find_extracted_layout(synced_json_path)
    layout_data = None
    if extracted_layout_path:
        layout_data = load_layout_data(extracted_layout_path)
        print(f"   [OK] Extracted layout from: {extracted_layout_path}")
    else:
        print(f"   [WARN] Layout file not found, rendering without layout")
    
    # Step 3: Merge synced JSON with original given JSON
    # Merge alters the original file to reflect the merge
    print(f"\n3. Merging synced JSON with original given JSON (merge alters original file)...")
    if not merge_report_path.exists():
        print(f"   [ERROR] Merge report not found: {merge_report_path}")
        return False
    
    # Copy original to then_dir so we can merge into it (preserving given file)
    import shutil
    shutil.copy2(story_graph_path, merged_original_path)
    
    diagram = StoryIODiagram()
    merged_data = diagram.merge_story_graphs(
        extracted_path=synced_json_path,
        original_path=merged_original_path,  # Merge into the copy of original
        report_path=merge_report_path,
        output_path=merged_original_path  # Merge writes back to original file
    )
    print(f"   [OK] Merged story graph saved to: {merged_original_path} (original file updated with merge)")
    
    # Step 4: Render synced JSON to DrawIO again (with layout)
    print(f"\n4. Rendering synced JSON to DrawIO again (with layout)...")
    synced_graph = load_story_graph(synced_json_path)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=synced_graph,
        output_path=rendered2_path,
        layout_data=layout_data
    )
    print(f"   [OK] Second render saved to: {rendered2_path}")
    
    print(f"\n{'='*80}")
    print("[OK] Full round-trip workflow execution completed")
    print(f"{'='*80}")
    print(f"First render:  {rendered1_path}")
    print(f"Synced JSON:   {synced_json_path}")
    print(f"Merged original: {merged_original_path} (original file updated with merge)")
    print(f"Second render: {rendered2_path}")
    
    return True

if __name__ == '__main__':
    try:
        success = render_then_sync_then_render_graph()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

