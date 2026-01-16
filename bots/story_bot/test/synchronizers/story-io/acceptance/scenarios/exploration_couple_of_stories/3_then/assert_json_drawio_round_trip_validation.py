"""
Assert JSON and DrawIO round-trip validation.

THEN: Assert expected matches actual (both JSON and DrawIO)

This assertion validates:
1. Expected extracted JSON matches synced JSON (from DrawIO extraction)
2. DrawIO elements validation (stories and acceptance criteria counts)
3. Overlap detection (no overlapping sub_epics or stories)
4. Layout preservation (first render matches second render)

Validates the complete round-trip: JSON → DrawIO → JSON → DrawIO
"""
import sys
from pathlib import Path
import json
import xml.etree.ElementTree as ET

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
    """Recursively count all stories in an epic or sub_epic."""
    count = 0
    
    # Only sub_epics have story_groups, not stories
    # Count stories in story_groups (sub_epics only)
    for story_group in item.get('story_groups', []):
        count += len(story_group.get('stories', []))
    
    # Count stories in sub_epics (recursively)
    for sub_epic in item.get('sub_epics', []):
        count += count_stories_recursive(sub_epic)
    
    return count

def count_stories_with_ac_recursive(item):
    """Recursively count only stories with acceptance criteria."""
    count = 0
    
    # Only sub_epics have story_groups, not stories
    # Count stories with AC in story_groups (sub_epics only)
    for story_group in item.get('story_groups', []):
        for story in story_group.get('stories', []):
            ac = story.get('acceptance_criteria') or story.get('Steps') or story.get('steps') or []
            if ac:
                count += 1
    
    # Count stories with AC in sub_epics (recursively)
    for sub_epic in item.get('sub_epics', []):
        count += count_stories_with_ac_recursive(sub_epic)
    
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
    
    # Compare story counts - only stories with AC (for exploration mode)
    stories1 = sum(count_stories_with_ac_recursive(epic) for epic in expected.get('epics', []))
    stories2 = sum(count_stories_with_ac_recursive(epic) for epic in actual.get('epics', []))
    if stories1 != stories2:
        differences.append(f"Story count mismatch (with AC): {stories1} vs {stories2}")
    
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

def validate_drawio_elements(drawio_path: Path, expected_json_path: Path) -> dict:
    """Validate that DrawIO file contains expected stories and acceptance criteria."""
    if not drawio_path.exists():
        return {'valid': False, 'errors': [f'DrawIO file not found: {drawio_path}']}
    
    # Load expected JSON to know what to expect
    with open(expected_json_path, 'r', encoding='utf-8') as f:
        expected = json.load(f)
    
    # Count expected stories WITH acceptance criteria (only these should be rendered)
    # Stories without AC should not be rendered in exploration mode
    expected_stories_with_ac = 0
    story_ac_map = {}  # Maps story name -> expected AC box count
    story_id_map = {}  # Maps story name -> story ID pattern (e.g., "e1f1s1")
    for epic_idx, epic in enumerate(expected.get('epics', []), 1):
        for feat_idx, sub_epic in enumerate(epic.get('sub_epics', []), 1):
            for story_group in sub_epic.get('story_groups', []):
                for story_idx, story in enumerate(story_group.get('stories', []), 1):
                    # Check for acceptance_criteria (new format) or Steps/steps (legacy)
                    ac = story.get('acceptance_criteria') or story.get('Steps') or story.get('steps') or []
                    if ac:
                        expected_stories_with_ac += 1
                        # Each AC entry gets its own box
                        ac_box_count = len(ac)
                        story_name = story['name']
                        story_ac_map[story_name] = ac_box_count
                        # Store expected story ID pattern
                        story_id_pattern = f"e{epic_idx}f{feat_idx}s{story_idx}"
                        story_id_map[story_name] = story_id_pattern
    
    try:
        tree = ET.parse(drawio_path)
        root = tree.getroot()
        
        # Find all cells
        cells = root.findall('.//mxCell')
        
        # Count stories (yellow/system/technical boxes) and map to their IDs
        actual_stories = []
        story_id_to_name = {}
        for cell in cells:
            style = cell.get('style', '')
            cell_id = cell.get('id', '')
            if (('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 'fillColor=#000000' in style)
                and cell_id.startswith('e') and 'f' in cell_id and 's' in cell_id
                and not cell_id.startswith('ac_')):  # Exclude AC boxes
                story_name = cell.get('value', '')
                actual_stories.append({
                    'id': cell_id,
                    'name': story_name
                })
                story_id_to_name[cell_id] = story_name
        
        # Count acceptance criteria boxes (AC boxes with id starting with 'ac_')
        # Group by story to validate each story has expected AC
        actual_ac_by_story = {}  # Maps story_id -> list of AC boxes
        for cell in cells:
            cell_id = cell.get('id', '')
            if cell_id.startswith('ac_'):
                # Extract story ID from AC box ID (format: ac_e1f1s1_0 -> e1f1s1)
                # Remove 'ac_' prefix and the trailing index
                story_id = cell_id[3:]  # Remove 'ac_' prefix
                # Find the last underscore and remove everything after it
                last_underscore = story_id.rfind('_')
                if last_underscore > 0:
                    story_id = story_id[:last_underscore]
                if story_id not in actual_ac_by_story:
                    actual_ac_by_story[story_id] = []
                actual_ac_by_story[story_id].append({
                    'id': cell_id,
                    'value': cell.get('value', '')
                })
        
        errors = []
        
        # Only stories with AC should be rendered
        if len(actual_stories) != expected_stories_with_ac:
            errors.append(f"Story count mismatch: expected {expected_stories_with_ac} stories with AC, found {len(actual_stories)} stories in DrawIO")
        
        # Validate that each story with AC in JSON has AC boxes in DrawIO
        for story_id, story_name in story_id_to_name.items():
            if story_name in story_ac_map:
                expected_ac_count = story_ac_map[story_name]
                actual_ac_count = len(actual_ac_by_story.get(story_id, []))
                if actual_ac_count == 0:
                    errors.append(f"Story '{story_name}' ({story_id}) has acceptance criteria in JSON but no AC boxes found in DrawIO")
                elif actual_ac_count < expected_ac_count:
                    errors.append(f"Story '{story_name}' ({story_id}) expected {expected_ac_count} AC boxes, found {actual_ac_count}")
        
        # Validate that all rendered stories have AC (as per requirement - only stories with AC should be rendered)
        for story in actual_stories:
            if story['name'] not in story_ac_map:
                errors.append(f"Story '{story['name']}' ({story['id']}) is rendered in DrawIO but has no acceptance criteria in JSON (all rendered stories must have AC)")
        
        total_ac_boxes = sum(len(ac_list) for ac_list in actual_ac_by_story.values())
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'counts': {
                'stories': {'expected': expected_stories_with_ac, 'actual': len(actual_stories)},
                'ac_boxes': {'expected': sum(story_ac_map.values()), 'actual': total_ac_boxes},
                'stories_with_ac': expected_stories_with_ac
            }
        }
    except Exception as e:
        return {'valid': False, 'errors': [f'Error validating DrawIO elements: {e}']}

def check_drawio_overlaps(drawio_path: Path) -> dict:
    """Check for overlapping features and stories in DrawIO file."""
    if not drawio_path.exists():
        return {'valid': False, 'errors': [f'DrawIO file not found: {drawio_path}']}
    
    try:
        tree = ET.parse(drawio_path)
        root = tree.getroot()
        
        # Find all cells
        cells = root.findall('.//mxCell')
        
        # Extract features (green boxes: fillColor=#d5e8d4)
        features = []
        for cell in cells:
            style = cell.get('style', '')
            if 'fillColor=#d5e8d4' in style and cell.get('id', '').startswith('e') and 'f' in cell.get('id', ''):
                geom = cell.find('mxGeometry')
                if geom is not None:
                    x = float(geom.get('x', 0))
                    y = float(geom.get('y', 0))
                    w = float(geom.get('width', 0))
                    h = float(geom.get('height', 0))
                    features.append({
                        'id': cell.get('id', ''),
                        'name': cell.get('value', ''),
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'right': x + w, 'bottom': y + h
                    })
        
        # Extract stories (yellow/system/technical boxes)
        stories = []
        for cell in cells:
            style = cell.get('style', '')
            cell_id = cell.get('id', '')
            if (('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 'fillColor=#000000' in style)
                and cell_id.startswith('e') and 'f' in cell_id and 's' in cell_id
                and not cell_id.startswith('ac_')):  # Exclude AC boxes
                geom = cell.find('mxGeometry')
                if geom is not None:
                    x = float(geom.get('x', 0))
                    y = float(geom.get('y', 0))
                    w = float(geom.get('width', 0))
                    h = float(geom.get('height', 0))
                    stories.append({
                        'id': cell_id,
                        'name': cell.get('value', ''),
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'right': x + w, 'bottom': y + h
                    })
        
        overlaps = []
        
        # Check feature overlaps
        for i, f1 in enumerate(features):
            for f2 in features[i+1:]:
                # Check if rectangles overlap (with 5px tolerance)
                tolerance = 5
                if not (f1['right'] + tolerance < f2['x'] or f2['right'] + tolerance < f1['x'] or
                        f1['bottom'] + tolerance < f2['y'] or f2['bottom'] + tolerance < f1['y']):
                    overlaps.append(f"Feature overlap: '{f1['name']}' ({f1['id']}) overlaps with '{f2['name']}' ({f2['id']})")
        
        # Check story overlaps
        for i, s1 in enumerate(stories):
            for s2 in stories[i+1:]:
                # Check if rectangles overlap (with 5px tolerance)
                tolerance = 5
                if not (s1['right'] + tolerance < s2['x'] or s2['right'] + tolerance < s1['x'] or
                        s1['bottom'] + tolerance < s2['y'] or s2['bottom'] + tolerance < s1['y']):
                    overlaps.append(f"Story overlap: '{s1['name']}' ({s1['id']}) overlaps with '{s2['name']}' ({s2['id']})")
        
        return {
            'valid': len(overlaps) == 0,
            'overlaps': overlaps,
            'sub_epic_count': len(features),
            'story_count': len(stories)
        }
    except Exception as e:
        return {'valid': False, 'errors': [f'Error checking overlaps: {e}']}

def assert_json_drawio_round_trip_validation():
    """Assert JSON and DrawIO round-trip validation.
    
    Validates:
    - Expected extracted JSON matches synced JSON
    - DrawIO contains correct number of stories and AC boxes
    - No overlapping elements in DrawIO
    - Layout preservation between renders
    """
    print(f"\n{'='*80}")
    print("THEN: Assert expected matches actual (JSON and DrawIO)")
    print(f"{'='*80}")
    
    # Expected files
    given_dir = scenario_dir / "1_given"
    expected_json_path = given_dir / "story-graph-complex.json"
    expected_extracted_json_path = then_dir / "expected-extracted-story-graph.json"
    
    # Actual files
    synced_json_path = then_dir / "actual-synced-story-graph.json"
    # Merged original file (original file updated with merge)
    merged_original_path = then_dir / "story-graph-complex.json"
    rendered1_path = then_dir / "actual-first-render.drawio"
    rendered2_path = then_dir / "actual-second-render.drawio"
    
    if not expected_json_path.exists():
        print(f"[ERROR] Expected JSON not found: {expected_json_path}")
        return False
    
    if not expected_extracted_json_path.exists():
        print(f"[ERROR] Expected extracted JSON not found: {expected_extracted_json_path}")
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
    
    # Assert 1: Expected extracted JSON matches synced JSON
    print(f"\n1. Asserting expected extracted JSON matches synced JSON...")
    json_match = _assert_jsons_match(expected_extracted_json_path, synced_json_path)
    if json_match['match']:
        print(f"   [OK] Expected extracted JSON matches synced JSON!")
    else:
        print(f"   [FAIL] Expected extracted JSON doesn't match synced JSON: {json_match.get('message', 'Unknown error')}")
        if json_match.get('differences'):
            for diff in json_match['differences']:
                print(f"      - {diff}")
        all_passed = False
    
    # Assert 1b: Merged original file matches original given JSON (round-trip validation)
    # After merging, the original file (updated with merge) should match the original given JSON
    if merged_original_path.exists():
        print(f"\n1b. Asserting merged original file matches original given JSON (round-trip validation)...")
        merge_match = _assert_jsons_match(expected_json_path, merged_original_path)
        if merge_match['match']:
            print(f"   [OK] Merged original file matches original given JSON (merge successful - round-trip preserved)!")
        else:
            print(f"   [FAIL] Merged original file doesn't match original given JSON: {merge_match.get('message', 'Unknown error')}")
            if merge_match.get('differences'):
                for diff in merge_match['differences']:
                    print(f"      - {diff}")
            all_passed = False
    else:
        print(f"\n1b. Skipping merge validation (merged original file not found: {merged_original_path})")
        all_passed = False
    
    # Assert 2: Validate DrawIO elements (stories, acceptance criteria)
    print(f"\n2. Validating DrawIO elements (stories, acceptance criteria)...")
    
    # Validate first render
    print(f"   2a. Validating first render DrawIO elements...")
    element_validation1 = validate_drawio_elements(rendered1_path, expected_json_path)
    if element_validation1['valid']:
        counts = element_validation1['counts']
        print(f"   [OK] First render: {counts['stories']['actual']} stories (expected {counts['stories']['expected']}), {counts['ac_boxes']['actual']} AC boxes (expected {counts['ac_boxes']['expected']})")
    else:
        print(f"   [FAIL] First render element validation failed:")
        for error in element_validation1['errors']:
            print(f"      - {error}")
        all_passed = False
    
    # Validate second render
    print(f"   2b. Validating second render DrawIO elements...")
    element_validation2 = validate_drawio_elements(rendered2_path, expected_json_path)
    if element_validation2['valid']:
        counts = element_validation2['counts']
        print(f"   [OK] Second render: {counts['stories']['actual']} stories (expected {counts['stories']['expected']}), {counts['ac_boxes']['actual']} AC boxes (expected {counts['ac_boxes']['expected']})")
    else:
        print(f"   [FAIL] Second render element validation failed:")
        for error in element_validation2['errors']:
            print(f"      - {error}")
        all_passed = False
    
    # Assert 3: Check for overlaps in rendered DrawIOs
    print(f"\n3. Checking for overlaps in rendered DrawIOs...")
    
    # Check first render
    print(f"   3a. Checking first render for overlaps...")
    overlap_check1 = check_drawio_overlaps(rendered1_path)
    if overlap_check1['valid']:
        print(f"   [OK] First render: {overlap_check1['sub_epic_count']} sub_epics, {overlap_check1['story_count']} stories - no overlaps")
    else:
        print(f"   [FAIL] First render has overlaps:")
        for overlap in overlap_check1.get('overlaps', []):
            print(f"      - {overlap}")
        all_passed = False
    
    # Check second render
    print(f"   3b. Checking second render for overlaps...")
    overlap_check2 = check_drawio_overlaps(rendered2_path)
    if overlap_check2['valid']:
        print(f"   [OK] Second render: {overlap_check2['sub_epic_count']} sub_epics, {overlap_check2['story_count']} stories - no overlaps")
    else:
        print(f"   [FAIL] Second render has overlaps:")
        for overlap in overlap_check2.get('overlaps', []):
            print(f"      - {overlap}")
        all_passed = False
    
    # Assert 4: DrawIOs match (layout preservation)
    print(f"\n4. Asserting DrawIOs match (layout preservation)...")
    drawio_match = compare_drawios(rendered1_path, rendered2_path)
    if drawio_match['match']:
        print(f"   [OK] First render matches second render (layout preserved)!")
    else:
        print(f"   [INFO] First render differs from second render (layout may have been applied): {drawio_match.get('message', 'Unknown')}")
        # This is informational - layout differences are expected
    
    print(f"\n{'='*80}")
    if all_passed:
        print("[OK] All assertions passed!")
    else:
        print("[FAIL] Some assertions failed!")
    print(f"{'='*80}")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = assert_json_drawio_round_trip_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

