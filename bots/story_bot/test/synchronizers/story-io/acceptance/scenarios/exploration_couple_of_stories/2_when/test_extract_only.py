"""
Debug utility: Extract story graph from DrawIO file only.

This is a utility script for debugging extraction. It's not part of the main
test workflow but can be useful for troubleshooting extraction issues.

Usage: Run this script to extract JSON from a DrawIO file without running
the full render-sync-render workflow.
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
sys.path.insert(0, str(scenario_dir.parent))

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

def test_extract_only():
    """Extract story graph from DrawIO file."""
    # Paths
    then_dir = scenario_dir / "3_then"
    given_dir = scenario_dir / "1_given"
    
    # Input: first render DrawIO
    drawio_path = then_dir / "actual-first-render.drawio"
    original_path = given_dir / "story-graph-complex.json"
    
    # Output: synced JSON
    synced_json_path = when_dir / "synced-story-graph.json"
    
    print(f"\n{'='*80}")
    print("EXTRACT ONLY: Sync from DrawIO back to JSON")
    print(f"{'='*80}")
    print(f"DrawIO: {drawio_path}")
    print(f"Original: {original_path}")
    print(f"Output: {synced_json_path}")
    
    if not drawio_path.exists():
        print(f"[ERROR] DrawIO file not found: {drawio_path}")
        return False
    
    # Extract from DrawIO
    print(f"\nExtracting story graph from DrawIO...")
    diagram = StoryIODiagram(drawio_file=drawio_path)
    diagram.synchronize_outline(
        drawio_path=drawio_path,
        original_path=original_path,
        output_path=synced_json_path,
        generate_report=True
    )
    # Note: synchronize_outline already writes the file, so we don't need save_story_graph
    # (save_story_graph would overwrite with diagram.render() which uses internal structure)
    print(f"   [OK] Synced story graph saved to: {synced_json_path}")
    
    # Print summary
    import json
    with open(synced_json_path, 'r') as f:
        synced_data = json.load(f)
    
    print(f"\n{'='*80}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*80}")
    print(f"Epics: {len(synced_data.get('epics', []))}")
    for epic in synced_data.get('epics', []):
        print(f"  - {epic['name']}: {len(epic.get('sub_epics', []))} sub_epics")
        for sub_epic in epic.get('sub_epics', []):
            story_groups = sub_epic.get('story_groups', [])
            stories = sub_epic.get('stories', [])
            total_stories = sum(len(g.get('stories', [])) for g in story_groups) + len(stories)
            print(f"    - {sub_epic['name']}: {len(story_groups)} story_groups, {total_stories} stories")
    
    print(f"\n{'='*80}")
    print("[OK] Extraction completed")
    print(f"{'='*80}")
    
    return True

if __name__ == '__main__':
    try:
        success = test_extract_only()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

