"""
Render then sync then render graph workflow execution.

WHEN: Story graph is rendered to DrawIO, synced back to JSON (extracting layout), then rendered again with layout

UNIQUE TO THIS WORKFLOW:
- Executes render → sync → render workflow focused on layout preservation
- Uses render_outline_from_graph (outline mode, all stories)
- Renders twice: first without layout, second with extracted layout from sync
- Tests that layout extraction and re-application preserves the original layout
"""
import sys
import io
from pathlib import Path

# Fix encoding for Windows - ensure output is visible and unbuffered
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Set up logging to file
when_dir = Path(__file__).parent
log_file = when_dir / "workflow_output.log"
log_handle = open(log_file, 'w', encoding='utf-8', buffering=1)

class TeeOutput:
    """Tee output to both stdout and file."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except (ValueError, OSError):
                # File may be closed, ignore
                pass
    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except (ValueError, OSError):
                # File may be closed, ignore
                pass

sys.stdout = TeeOutput(sys.stdout, log_handle)
sys.stderr = TeeOutput(sys.stderr, log_handle)

# Add parent directories to path (when_dir already set above)
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
    
    # Output files - actuals go to then_dir, intermediate files to when_dir
    then_dir.mkdir(parents=True, exist_ok=True)
    rendered1_path = then_dir / "actual-first-render.drawio"
    synced_json_path = when_dir / "synced-story-graph.json"
    rendered2_path = then_dir / "actual-second-render.drawio"
    
    print(f"\n{'='*80}")
    print("WHEN: Render story graph to DrawIO, sync back to JSON (extract layout), then render again with layout")
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
    diagram.save_story_graph(synced_json_path)
    print(f"   [OK] Synced story graph saved to: {synced_json_path}")
    
    # Load extracted layout (layout file is generated during sync)
    extracted_layout_path = find_extracted_layout(synced_json_path)
    layout_data = None
    if extracted_layout_path:
        layout_data = load_layout_data(extracted_layout_path)
        print(f"   [OK] Extracted layout from: {extracted_layout_path}")
    else:
        print(f"   [WARN] Layout file not found, rendering without layout")
    
    # Step 3: Render synced JSON to DrawIO again (with layout)
    print(f"\n3. Rendering synced JSON to DrawIO again (with layout)...")
    synced_graph = load_story_graph(synced_json_path)
    
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
    success = False
    try:
        success = render_then_sync_then_render_graph()
    except Exception as e:
        print(f"\n[FAIL] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    finally:
        try:
            if 'log_handle' in globals() and log_handle:
                log_handle.close()
        except Exception:
            pass  # Ignore errors during cleanup
    sys.exit(0 if success else 1)
