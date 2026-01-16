"""
Test layout preservation during render-sync-render cycle.

This test:
1. Loads original DrawIO file
2. Syncs to extract story graph and layout
3. Renders back to DrawIO
4. Compares original vs rendered layouts
5. Identifies what was preserved and what wasn't
6. Iterates until layout preservation is fixed
"""

import json
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sys

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram


def extract_positions_from_drawio(drawio_path: Path) -> Dict[str, Dict[str, float]]:
    """Extract component positions from DrawIO file using same key format as layout system."""
    positions = {}
    
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    # Extract epics, features, stories using same logic as synchronizer
    epics = []
    features = []
    stories = []
    users = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = _get_cell_value(cell)
        geometry = cell.find('mxGeometry')
        
        if geometry is None:
            continue
        
        x = float(geometry.get('x', 0))
        y = float(geometry.get('y', 0))
        width = float(geometry.get('width', 0))
        height = float(geometry.get('height', 0))
        
        # Epics: purple boxes
        if 'fillColor=#e1d5e7' in style:
            match = re.match(r'epic(\d+)', cell_id)
            if match:
                epic_num = int(match.group(1))
                epics.append({
                    'num': epic_num,
                    'name': value,
                    'x': x, 'y': y, 'width': width, 'height': height
                })
        
        # Features: green boxes
        elif 'fillColor=#d5e8d4' in style:
            match = re.match(r'e(\d+)f(\d+)', cell_id)
            if match:
                epic_num = int(match.group(1))
                feat_num = int(match.group(2))
                features.append({
                    'epic_num': epic_num,
                    'feat_num': feat_num,
                    'name': value,
                    'x': x, 'y': y, 'width': width, 'height': height
                })
        
        # Stories: yellow/blue/black boxes
        elif ('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 
               'fillColor=#000000' in style or 'fillColor=#000' in style):
            match = re.match(r'e(\d+)f(\d+)s(\d+)', cell_id)
            if match:
                epic_num = int(match.group(1))
                feat_num = int(match.group(2))
                story_num = int(match.group(3))
                stories.append({
                    'epic_num': epic_num,
                    'feat_num': feat_num,
                    'story_num': story_num,
                    'name': value,
                    'x': x, 'y': y, 'width': width, 'height': height
                })
        
        # Users: light blue boxes
        elif 'fillColor=#dae8fc' in style:
            if value:
                users.append({
                    'name': value,
                    'x': x, 'y': y
                })
    
    # Build layout keys in same format as synchronizer
    # Sort epics by epic_num
    epics.sort(key=lambda e: e['num'])
    
    # Build epic keys
    for epic in epics:
        key = f"EPIC|{epic['name']}"
        positions[key] = {
            'x': epic['x'],
            'y': epic['y'],
            'width': epic['width'],
            'height': epic['height']
        }
    
    # Build feature keys (need epic names)
    epic_names = {e['num']: e['name'] for e in epics}
    for feature in features:
        epic_name = epic_names.get(feature['epic_num'], f"Epic{feature['epic_num']}")
        key = f"FEATURE|{epic_name}|{feature['name']}"
        positions[key] = {
            'x': feature['x'],
            'y': feature['y'],
            'width': feature['width'],
            'height': feature['height']
        }
    
    # Build story keys (need epic and feature names)
    feature_map = {}
    for feature in features:
        epic_name = epic_names.get(feature['epic_num'], f"Epic{feature['epic_num']}")
        feature_map[(feature['epic_num'], feature['feat_num'])] = feature['name']
    
    for story in stories:
        epic_name = epic_names.get(story['epic_num'], f"Epic{story['epic_num']}")
        feature_name = feature_map.get((story['epic_num'], story['feat_num']), f"Feature{story['feat_num']}")
        key = f"{epic_name}|{feature_name}|{story['name']}"
        positions[key] = {
            'x': story['x'],
            'y': story['y']
        }
    
    # Build user keys (need to find associated story)
    # Users are positioned near stories, so we'll store them separately
    for user in users:
        # User keys are stored as USER|epic|feature|story|user_name in layout
        # For now, just store by name and position
        key = f"USER|{user['name']}"
        positions[key] = {
            'x': user['x'],
            'y': user['y']
        }
    
    return positions


def _get_cell_value(cell) -> str:
    """Extract text value from a cell, handling HTML entities."""
    import re
    value = cell.get('value', '')
    value = value.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    value = re.sub(r'<[^>]+>', '', value)
    return value.strip()


def compare_layouts(original: Dict[str, Dict[str, float]], 
                   rendered: Dict[str, Dict[str, float]],
                   tolerance: float = 5.0) -> Dict[str, Any]:
    """Compare two layout dictionaries using exact key matching."""
    results = {
        'total_original': len(original),
        'total_rendered': len(rendered),
        'exact_matches': [],
        'position_diffs': [],
        'missing_in_rendered': [],
        'new_in_rendered': [],
        'tolerance': tolerance
    }
    
    # Compare by exact key match (layout keys should match exactly)
    all_keys = set(original.keys()) | set(rendered.keys())
    
    for key in all_keys:
        if key not in original:
            results['new_in_rendered'].append({
                'key': key,
                'position': rendered[key]
            })
            continue
        
        if key not in rendered:
            results['missing_in_rendered'].append({
                'key': key,
                'position': original[key]
            })
            continue
        
        # Both exist - compare positions
        orig_pos = original[key]
        rend_pos = rendered[key]
        
        # Handle both formats: {x, y} for stories/users or {x, y, width, height} for epics/features
        x1 = orig_pos.get('x', 0)
        y1 = orig_pos.get('y', 0)
        w1 = orig_pos.get('width', 0)
        h1 = orig_pos.get('height', 0)
        
        x2 = rend_pos.get('x', 0)
        y2 = rend_pos.get('y', 0)
        w2 = rend_pos.get('width', 0)
        h2 = rend_pos.get('height', 0)
        
        x_diff = abs(x1 - x2)
        y_diff = abs(y1 - y2)
        w_diff = abs(w1 - w2)
        h_diff = abs(h1 - h2)
        
        if x_diff <= tolerance and y_diff <= tolerance and w_diff <= tolerance and h_diff <= tolerance:
            results['exact_matches'].append({
                'key': key,
                'original_pos': orig_pos,
                'rendered_pos': rend_pos
            })
        else:
            results['position_diffs'].append({
                'key': key,
                'original_pos': orig_pos,
                'rendered_pos': rend_pos,
                'x_diff': x_diff,
                'y_diff': y_diff,
                'width_diff': w_diff,
                'height_diff': h_diff
            })
    
    return results


def _calculate_similarity(str1: str, str2: str) -> float:
    """Calculate simple string similarity (0.0 to 1.0)."""
    if not str1 or not str2:
        return 0.0
    
    # Remove HTML tags and normalize
    import re
    str1_clean = re.sub(r'<[^>]+>', '', str1).strip()
    str2_clean = re.sub(r'<[^>]+>', '', str2).strip()
    
    if str1_clean == str2_clean:
        return 1.0
    
    # Simple word overlap
    words1 = set(str1_clean.lower().split())
    words2 = set(str2_clean.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0


def test_layout_preservation():
    """
    Test that layout is preserved during real-world sync->render cycle.
    
    Real-world workflow:
    1. User has DrawIO file (from previous render or manual edits)
    2. User hits "sync" → extracts story graph JSON + layout coordinates file
    3. User (or something else) edits story graph JSON
    4. User hits "render" → loads story graph JSON + layout file → renders DrawIO
    5. Compare: original DrawIO positions vs rendered DrawIO positions
    """
    # Paths - use acceptance input directory
    acceptance_dir = Path(__file__).parent.parent / "acceptance"
    input_dir = acceptance_dir / "input"
    original_drawio = input_dir / "story-map-outline-original.drawio"
    
    if not original_drawio.exists():
        # Fallback to docs directory if not in acceptance input
        original_drawio = Path(__file__).parent.parent.parent.parent / "docs" / "stories" / "map" / "story-map-outline original.drawio"
    
    test_dir = acceptance_dir / "outputs" / "layout_preservation_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Files that will be created during workflow
    extracted_json = test_dir / "extracted.json"
    extracted_layout = test_dir / "extracted-layout.json"
    rendered_drawio = test_dir / "rendered.drawio"
    
    print("=" * 80)
    print("LAYOUT PRESERVATION TEST - REAL-WORLD WORKFLOW")
    print("=" * 80)
    
    # STEP 1: SYNC - Extract story graph and layout from original DrawIO
    print("\nSTEP 1: SYNC - Extracting story graph and layout from DrawIO...")
    print(f"   Input: {original_drawio}")
    
    diagram = StoryIODiagram.sync_from_drawio(original_drawio)
    sync_result = diagram.synchronize_outline(
        drawio_path=original_drawio,
        output_path=extracted_json,
        generate_report=False
    )
    
    # Get the layout file that was created during sync
    layout_file_path = None
    if 'layout_file' in sync_result:
        layout_file_path = Path(sync_result['layout_file'])
    else:
        # Try to find it - sync creates it next to extracted JSON
        possible_layout = extracted_json.parent / f"{extracted_json.stem}-layout.json"
        if possible_layout.exists():
            layout_file_path = possible_layout
    
    if not layout_file_path or not layout_file_path.exists():
        print("   ERROR: Layout file was not created during sync!")
        print(f"   Expected at: {extracted_json.parent / f'{extracted_json.stem}-layout.json'}")
        return None
    
    print(f"   Story graph saved to: {extracted_json}")
    print(f"   Layout file saved to: {layout_file_path}")
    
    # Load the layout file (this is what will be used in production)
    with open(layout_file_path, 'r', encoding='utf-8') as f:
        layout_data = json.load(f)
    print(f"   Layout has {len(layout_data)} coordinate entries")
    
    # STEP 2: RENDER - Load story graph JSON and render with layout file
    print("\nSTEP 2: RENDER - Loading story graph JSON and rendering with layout file...")
    print(f"   Story graph: {extracted_json}")
    print(f"   Layout file: {layout_file_path}")
    
    # Create a NEW diagram instance (simulating what happens in production)
    # Load from the extracted JSON file (not from DrawIO)
    render_diagram = StoryIODiagram.load_from_story_graph(extracted_json)
    
    # Render using the layout file
    render_result = render_diagram.render_outline(
        output_path=rendered_drawio,
        layout_data=layout_data  # Use the layout file that was created during sync
    )
    print(f"   Rendered DrawIO saved to: {rendered_drawio}")
    
    # STEP 3: SYNC RENDERED - Extract layout from rendered DrawIO (to compare)
    print("\nSTEP 3: SYNC RENDERED - Extracting layout from rendered DrawIO...")
    rendered_diagram = StoryIODiagram.sync_from_drawio(rendered_drawio)
    rendered_sync_result = rendered_diagram.synchronize_outline(
        drawio_path=rendered_drawio,
        output_path=test_dir / "rendered-extracted.json",
        generate_report=False
    )
    
    # Get the layout file from rendered sync
    rendered_layout_file_path = None
    if 'layout_file' in rendered_sync_result:
        rendered_layout_file_path = Path(rendered_sync_result['layout_file'])
    else:
        # Try to find it
        possible_rendered_layout = test_dir / "rendered-extracted-layout.json"
        if possible_rendered_layout.exists():
            rendered_layout_file_path = possible_rendered_layout
    
    if not rendered_layout_file_path or not rendered_layout_file_path.exists():
        print("   ERROR: Could not extract layout from rendered DrawIO!")
        return None
    
    # Load the rendered layout
    with open(rendered_layout_file_path, 'r', encoding='utf-8') as f:
        rendered_layout_data = json.load(f)
    print(f"   Rendered layout has {len(rendered_layout_data)} coordinate entries")
    
    # STEP 4: COMPARE - Compare the two layout files (original vs rendered)
    print("\nSTEP 4: COMPARE - Comparing original layout vs rendered layout...")
    print("   This shows what coordinates were preserved from sync → render cycle")
    comparison = compare_layouts(layout_data, rendered_layout_data, tolerance=5.0)
    
    # Step 6: Report results
    print("\n" + "=" * 80)
    print("LAYOUT COMPARISON RESULTS")
    print("=" * 80)
    print(f"Original components: {comparison['total_original']}")
    print(f"Rendered components: {comparison['total_rendered']}")
    print(f"Exact matches (within {comparison['tolerance']}px): {len(comparison['exact_matches'])}")
    print(f"Position differences: {len(comparison['position_diffs'])}")
    print(f"Missing in rendered: {len(comparison['missing_in_rendered'])}")
    print(f"New in rendered: {len(comparison['new_in_rendered'])}")
    
    # Show position differences
    if comparison['position_diffs']:
        print("\n" + "-" * 80)
        print("POSITION DIFFERENCES (Top 10):")
        print("-" * 80)
        for i, diff in enumerate(comparison['position_diffs'][:10], 1):
            print(f"\n{i}. {diff['key'][:80]}")
            print(f"   X diff: {diff['x_diff']:.1f}px, Y diff: {diff['y_diff']:.1f}px")
            print(f"   W diff: {diff['width_diff']:.1f}px, H diff: {diff['height_diff']:.1f}px")
            print(f"   Original: x={diff['original_pos'].get('x', 0):.1f}, y={diff['original_pos'].get('y', 0):.1f}")
            print(f"   Rendered: x={diff['rendered_pos'].get('x', 0):.1f}, y={diff['rendered_pos'].get('y', 0):.1f}")
    
    # Show missing components
    if comparison['missing_in_rendered']:
        print("\n" + "-" * 80)
        print(f"MISSING IN RENDERED (Top 20 of {len(comparison['missing_in_rendered'])}):")
        print("-" * 80)
        for i, missing in enumerate(comparison['missing_in_rendered'][:20], 1):
            pos = missing['position']
            print(f"{i}. {missing['key'][:80]}")
            print(f"    Position: x={pos.get('x', 0):.1f}, y={pos.get('y', 0):.1f}")
    
    # Show new components
    if comparison['new_in_rendered']:
        print("\n" + "-" * 80)
        print(f"NEW IN RENDERED (Top 20 of {len(comparison['new_in_rendered'])}):")
        print("-" * 80)
        for i, new in enumerate(comparison['new_in_rendered'][:20], 1):
            pos = new['position']
            print(f"{i}. {new['key'][:80]}")
            print(f"    Position: x={pos.get('x', 0):.1f}, y={pos.get('y', 0):.1f}")
    
    # Save detailed comparison report
    report_path = test_dir / "layout-comparison-report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Calculate preservation percentage
    total_comparable = len(comparison['exact_matches']) + len(comparison['position_diffs'])
    if total_comparable > 0:
        preservation_rate = len(comparison['exact_matches']) / total_comparable * 100
        print(f"\nLayout preservation rate: {preservation_rate:.1f}%")
        
        # Summary of issues
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Exact matches: {len(comparison['exact_matches'])}/{total_comparable} ({preservation_rate:.1f}%)")
        print(f"⚠️  Position differences: {len(comparison['position_diffs'])}")
        print(f"❌ Missing in rendered: {len(comparison['missing_in_rendered'])} (mostly user components)")
        print(f"➕ New in rendered: {len(comparison['new_in_rendered'])} (stories not in original)")
        
        if len(comparison['missing_in_rendered']) > 0:
            print("\n🔍 ISSUE: User components are in layout file but not being rendered.")
            print("   These users exist in the story graph but renderer isn't placing them.")
            print("   Check renderer logic for user placement.")
        
        if len(comparison['position_diffs']) > 0:
            print("\n🔍 ISSUE: Some components have position differences.")
            for diff in comparison['position_diffs']:
                print(f"   - {diff['key']}: width diff = {diff['width_diff']:.1f}px")
    else:
        print("\n⚠️  WARNING: No comparable components found!")
    
    return comparison


if __name__ == "__main__":
    test_layout_preservation()

