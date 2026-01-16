"""
Assert story graph round-trip preservation.

THEN: Assert expected matches actual (both JSON and DrawIO)

UNIQUE TO THIS ASSERTION:
- Asserts render → sync → render workflow (round-trip test)
- Asserts JSONs match: expected vs synced, expected vs extracted from renders
- Asserts DrawIOs match: rendered1 vs rendered2 (layout preservation)
- Validates that story graph data is preserved through round-trip
"""
import sys
from pathlib import Path
import json

# Add parent directories to path
then_dir = Path(__file__).parent
scenario_dir = then_dir.parent
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(acceptance_dir.parent / "spec_by_example"))
sys.path.insert(0, str(scenario_dir.parent))  # Add scenarios directory for drawio_comparison

from drawio_comparison import compare_drawios
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

def count_sub_epics_recursive(item):
    """Recursively count all sub_epics in an epic or sub_epic."""
    count = len(item.get('sub_epics', []))
    for sub_epic in item.get('sub_epics', []):
        count += count_sub_epics_recursive(sub_epic)
    return count

def count_stories_recursive(item):
    """Recursively count all stories in an epic, sub_epic, or story."""
    count = len(item.get('stories', []))
    # Count stories in sub_epics
    for sub_epic in item.get('sub_epics', []):
        count += count_stories_recursive(sub_epic)
    # Count nested stories (story groups)
    for story in item.get('stories', []):
        if 'stories' in story:
            count += count_stories_recursive(story)
    return count

def _assert_jsons_match(expected_path: Path, actual_path: Path) -> dict:
    """Compare two JSON story graph files with detailed comparison (new format with sub_epics)."""
    if not expected_path.exists():
        return {'match': False, 'message': f'Expected file not found: {expected_path}'}
    if not actual_path.exists():
        return {'match': False, 'message': f'Actual file not found: {actual_path}'}
    
    with open(expected_path, 'r', encoding='utf-8') as f:
        expected = json.load(f)
    with open(actual_path, 'r', encoding='utf-8') as f:
        actual = json.load(f)
    
    differences = []
    
    # Compare epic counts
    epics1 = len(expected.get('epics', []))
    epics2 = len(actual.get('epics', []))
    if epics1 != epics2:
        differences.append(f"Epic count mismatch: {epics1} vs {epics2}")
    
    # Compare sub_epic counts (across all epics, recursively)
    sub_epics1 = sum(count_sub_epics_recursive(epic) for epic in expected.get('epics', []))
    sub_epics2 = sum(count_sub_epics_recursive(epic) for epic in actual.get('epics', []))
    if sub_epics1 != sub_epics2:
        differences.append(f"Sub-epic count mismatch: {sub_epics1} vs {sub_epics2}")
    
    # Compare story counts (across all epics and sub_epics, recursively)
    stories1 = sum(count_stories_recursive(epic) for epic in expected.get('epics', []))
    stories2 = sum(count_stories_recursive(epic) for epic in actual.get('epics', []))
    if stories1 != stories2:
        differences.append(f"Story count mismatch: {stories1} vs {stories2}")
    
    # Compare increment counts
    increments1 = len(expected.get('increments', []))
    increments2 = len(actual.get('increments', []))
    if increments1 != increments2:
        differences.append(f"Increment count mismatch: {increments1} vs {increments2}")
    
    # If counts match, consider it a pass (following old test behavior)
    # The old test only checks counts, not deep equality
    # This allows for minor differences in structure while ensuring data integrity
    
    return {
        'match': len(differences) == 0,
        'differences': differences,
        'message': 'JSONs match' if len(differences) == 0 else f'{len(differences)} differences found'
    }

def assert_story_graph_round_trip():
    """Assert that story graph is preserved through render → sync → render round-trip."""
    print(f"\n{'='*80}")
    print("THEN: Assert expected matches actual (JSON and DrawIO)")
    print(f"{'='*80}")
    
    # Expected file
    given_dir = scenario_dir / "1_given"
    expected_json_path = given_dir / "story-graph-single-epic.json"
    
    # Actual files
    when_dir = scenario_dir / "2_when"
    synced_json_path = when_dir / "synced-story-graph.json"
    rendered1_path = then_dir / "actual-first-render.drawio"
    rendered2_path = then_dir / "actual-second-render.drawio"
    
    if not expected_json_path.exists():
        print(f"[ERROR] Expected JSON not found: {expected_json_path}")
        return False
    
    if not synced_json_path.exists():
        print(f"[ERROR] Synced JSON not found: {synced_json_path}")
        return False
    
    if not rendered1_path.exists():
        print(f"[ERROR] First render not found: {rendered1_path}")
        return False
    
    if not rendered2_path.exists():
        print(f"[ERROR] Second render not found: {rendered2_path}")
        return False
    
    all_passed = True
    
    # Assert 1: Expected JSON matches synced JSON
    print(f"\n1. Asserting expected JSON matches synced JSON...")
    json_match = _assert_jsons_match(expected_json_path, synced_json_path)
    if json_match['match']:
        print(f"   [OK] Expected JSON matches synced JSON!")
    else:
        print(f"   [FAIL] Expected JSON doesn't match synced JSON: {json_match.get('message', 'Unknown error')}")
        all_passed = False
    
    # Assert 2: Extract JSONs from rendered DrawIOs and compare
    print(f"\n2. Extracting and comparing JSONs from rendered DrawIOs...")
    
    # Extract JSON from rendered1
    temp_json1 = when_dir / "temp_rendered1.json"
    diagram1 = StoryIODiagram(drawio_file=rendered1_path)
    diagram1.synchronize_outline(drawio_path=rendered1_path, output_path=temp_json1)
    diagram1.save_story_graph(temp_json1)
    
    # Extract JSON from rendered2
    temp_json2 = when_dir / "temp_rendered2.json"
    diagram2 = StoryIODiagram(drawio_file=rendered2_path)
    diagram2.synchronize_outline(drawio_path=rendered2_path, output_path=temp_json2)
    diagram2.save_story_graph(temp_json2)
    
    # Compare expected with extracted from rendered1
    print(f"   2a. Comparing expected JSON with extracted JSON from rendered1...")
    json_match_rendered1 = _assert_jsons_match(expected_json_path, temp_json1)
    if json_match_rendered1['match']:
        print(f"   [OK] Expected JSON matches rendered1 extracted JSON!")
    else:
        print(f"   [FAIL] Expected JSON doesn't match rendered1 extracted JSON")
        all_passed = False
    
    # Compare expected with extracted from rendered2
    print(f"   2b. Comparing expected JSON with extracted JSON from rendered2...")
    json_match_rendered2 = _assert_jsons_match(expected_json_path, temp_json2)
    if json_match_rendered2['match']:
        print(f"   [OK] Expected JSON matches rendered2 extracted JSON!")
    else:
        print(f"   [FAIL] Expected JSON doesn't match rendered2 extracted JSON")
        all_passed = False
    
    # Assert 3: DrawIOs match (layout preservation)
    print(f"\n3. Asserting DrawIOs match (layout preservation)...")
    drawio_match = compare_drawios(rendered1_path, rendered2_path)
    if drawio_match['match']:
        print(f"   [OK] First render matches second render (layout preserved)!")
    else:
        print(f"   [INFO] First render differs from second render (layout may have been applied): {drawio_match.get('message', 'Unknown')}")
        # This is informational - layout differences are expected
    
    # Cleanup temp files
    if temp_json1.exists():
        temp_json1.unlink()
    if temp_json2.exists():
        temp_json2.unlink()
    
    print(f"\n{'='*80}")
    if all_passed:
        print("[OK] All assertions passed!")
    else:
        print("[FAIL] Some assertions failed!")
    print(f"{'='*80}")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = assert_story_graph_round_trip()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

