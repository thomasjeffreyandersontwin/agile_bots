"""Test that epics render on top of sub-epics with half height."""
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Add parent directories to path
test_dir = Path(__file__).parent
acceptance_dir = test_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

def main():
    """Test rendering with epic/sub-epic positioning."""
    then_dir = test_dir / "3_then"
    extracted_json = then_dir / "actual-extracted.json"
    rendered_drawio = then_dir / "test-rendered.drawio"
    
    if not extracted_json.exists():
        print(f"[ERROR] Extracted JSON not found: {extracted_json}")
        return False
    
    # Render from JSON
    print("Rendering from extracted JSON...")
    with open(extracted_json, 'r', encoding='utf-8') as f:
        import json
        story_graph = json.load(f)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=story_graph,
        output_path=rendered_drawio,
        layout_data=None
    )
    
    print(f"[OK] Rendered to: {rendered_drawio}")
    
    # Verify epic and feature positioning
    tree = ET.parse(rendered_drawio)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    epics = []
    features = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = cell.get('value', '')
        geom = cell.find('mxGeometry')
        
        if geom is None:
            continue
        
        x = float(geom.get('x', 0))
        y = float(geom.get('y', 0))
        height = float(geom.get('height', 0))
        
        # Check for epics (purple fill)
        if 'fillColor=#e1d5e7' in style:
            epics.append({
                'name': value,
                'id': cell_id,
                'x': x,
                'y': y,
                'height': height
            })
        
        # Check for features (green fill)
        if 'fillColor=#d5e8d4' in style:
            features.append({
                'name': value,
                'id': cell_id,
                'x': x,
                'y': y,
                'height': height
            })
    
    print(f"\nFound {len(epics)} epics and {len(features)} features")
    
    # Check epic heights (should be ~30)
    print("\nEpic heights:")
    for epic in epics[:5]:  # Show first 5
        print(f"  {epic['name']}: height={epic['height']}, y={epic['y']}")
        if epic['height'] != 30:
            print(f"    [WARNING] Expected height=30, got {epic['height']}")
    
    # Check feature positions (should be below epics)
    print("\nFeature positions (first 5):")
    for feature in features[:5]:
        print(f"  {feature['name']}: y={feature['y']}, height={feature['height']}")
    
    # Check if features are below epics
    if epics and features:
        first_epic = epics[0]
        first_feature = features[0]
        expected_feature_y = first_epic['y'] + first_epic['height']
        
        print(f"\nPositioning check:")
        print(f"  Epic '{first_epic['name']}': y={first_epic['y']}, height={first_epic['height']}")
        print(f"  Feature '{first_feature['name']}': y={first_feature['y']}")
        print(f"  Expected feature y: {expected_feature_y}")
        
        if abs(first_feature['y'] - expected_feature_y) < 5:  # 5px tolerance
            print(f"  [OK] Feature is positioned correctly below epic")
        else:
            print(f"  [FAIL] Feature should be at y={expected_feature_y}, but is at y={first_feature['y']}")
            return False
    
    print("\n[OK] Rendering test completed")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

