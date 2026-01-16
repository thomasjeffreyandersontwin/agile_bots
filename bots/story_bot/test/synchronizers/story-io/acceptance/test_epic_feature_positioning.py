"""
Test to validate epic width and feature positioning in rendered DrawIO diagrams.

This test specifically checks:
1. Features in outline mode stack vertically (different y positions)
2. Epic width is at least as wide as its widest feature
3. Features don't overlap each other
4. Epics don't overlap each other
"""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram


class PositioningValidator:
    """Validates epic and feature positioning in DrawIO diagrams."""
    
    def __init__(self, drawio_path: Path):
        """Load and parse DrawIO XML file."""
        self.drawio_path = drawio_path
        with open(drawio_path, 'r', encoding='utf-8') as f:
            self.xml_content = f.read()
        
        self.root = ET.fromstring(self.xml_content)
        self.ns = {'mx': 'http://www.w3.org/1999/xhtml'}
        
        # Extract all cells and their geometries
        self.epics = {}  # epic_id -> {x, y, width, height, name}
        self.features = {}  # feature_id -> {x, y, width, height, name, epic_id}
        self.stories = {}  # story_id -> {x, y, width, height, name}
        
        self._parse_elements()
    
    def _parse_elements(self):
        """Parse all epic, feature, and story elements from DrawIO XML."""
        # Find all mxCell elements
        for cell in self.root.findall('.//mxCell'):
            cell_id = cell.get('id', '')
            value = cell.get('value', '')
            style = cell.get('style', '')
            
            # Find geometry element
            geom = cell.find('mxGeometry')
            if geom is None:
                continue
            
            x = float(geom.get('x', 0))
            y = float(geom.get('y', 0))
            width = float(geom.get('width', 0))
            height = float(geom.get('height', 0))
            
            geometry = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'name': self._extract_name_from_value(value)
            }
            
            # Identify epics (purple fill color)
            if 'fillColor=#e1d5e7' in style or 'fillColor=#9673a6' in style:
                if cell_id.startswith('epic') or 'epic' in cell_id.lower():
                    self.epics[cell_id] = geometry
            
            # Identify features (green fill color)
            elif 'fillColor=#d5e8d4' in style or 'fillColor=#82b366' in style:
                # Features have ids like "e1f1", "e2f3", etc. or contain "f" followed by number
                if ('f' in cell_id and 'e' in cell_id) or cell_id.startswith('e') and 'f' in cell_id:
                    # Try to extract epic index from feature id
                    epic_id = None
                    if cell_id.startswith('e') and 'f' in cell_id:
                        # Format: e{epic_idx}f{feat_idx}
                        parts = cell_id.replace('e', '').split('f')
                        if len(parts) >= 1:
                            epic_idx = parts[0]
                            epic_id = f"epic{epic_idx}"
                    
                    geometry['epic_id'] = epic_id
                    self.features[cell_id] = geometry
            
            # Identify stories (black, yellow, or colored fill)
            elif 'aspect=fixed' in style:
                # Stories are small squares (50x50 typically)
                if width <= 60 and height <= 60:  # Stories are typically 50x50
                    if cell_id not in self.epics and cell_id not in self.features:
                        self.stories[cell_id] = geometry
    
    def _extract_name_from_value(self, value: str) -> str:
        """Extract readable name from HTML value attribute."""
        if not value:
            return ""
        
        # Try to extract text from HTML
        try:
            # Look for text between > and < or extract from div
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', value)
            # Clean up whitespace
            text = ' '.join(text.split())
            return text[:100]  # Limit length
        except:
            return value[:100]
    
    def validate_feature_vertical_stack(self) -> Dict[str, any]:
        """
        Validate that features in the same epic stack vertically (different y positions).
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Group features by epic
        features_by_epic = {}
        for feat_id, feat_data in self.features.items():
            epic_id = feat_data.get('epic_id')
            if epic_id:
                if epic_id not in features_by_epic:
                    features_by_epic[epic_id] = []
                features_by_epic[epic_id].append((feat_id, feat_data))
        
        # Check each epic
        for epic_id, feature_list in features_by_epic.items():
            if len(feature_list) < 2:
                continue  # Need at least 2 features to check stacking
            
            # Sort features by y position
            sorted_features = sorted(feature_list, key=lambda x: x[1]['y'])
            
            for i in range(len(sorted_features) - 1):
                feat1_id, feat1 = sorted_features[i]
                feat2_id, feat2 = sorted_features[i + 1]
                
                feat1_bottom = feat1['y'] + feat1['height']
                feat2_top = feat2['y']
                
                # Check if features overlap vertically
                if feat1_bottom > feat2_top:
                    overlap = feat1_bottom - feat2_top
                    errors.append({
                        'type': 'vertical_overlap',
                        'epic_id': epic_id,
                        'feature1': feat1_id,
                        'feature2': feat2_id,
                        'feature1_name': feat1['name'],
                        'feature2_name': feat2['name'],
                        'overlap_amount': overlap,
                        'feature1_y': feat1['y'],
                        'feature1_bottom': feat1_bottom,
                        'feature2_y': feat2['y']
                    })
                
                # Check if features are too close (less than 10px spacing)
                elif feat2_top - feat1_bottom < 10:
                    spacing = feat2_top - feat1_bottom
                    warnings.append({
                        'type': 'close_spacing',
                        'epic_id': epic_id,
                        'feature1': feat1_id,
                        'feature2': feat2_id,
                        'spacing': spacing
                    })
        
        return {
            'passed': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def validate_epic_width(self) -> Dict[str, any]:
        """
        Validate that epic width is at least as wide as its widest feature.
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        # Group features by epic
        features_by_epic = {}
        for feat_id, feat_data in self.features.items():
            epic_id = feat_data.get('epic_id')
            if epic_id:
                if epic_id not in features_by_epic:
                    features_by_epic[epic_id] = []
                features_by_epic[epic_id].append(feat_data)
        
        # Check each epic
        for epic_id, epic_data in self.epics.items():
            if epic_id not in features_by_epic:
                continue  # Epic has no features
            
            features = features_by_epic[epic_id]
            if not features:
                continue
            
            # Find widest feature
            max_feature_width = max(feat['width'] for feat in features)
            
            # Epic should be at least as wide as its widest feature (with some padding)
            min_epic_width = max_feature_width + 20  # 10px padding on each side
            
            if epic_data['width'] < min_epic_width:
                errors.append({
                    'type': 'epic_too_narrow',
                    'epic_id': epic_id,
                    'epic_name': epic_data['name'],
                    'epic_width': epic_data['width'],
                    'max_feature_width': max_feature_width,
                    'min_required_width': min_epic_width,
                    'deficit': min_epic_width - epic_data['width']
                })
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_epic_horizontal_separation(self) -> Dict[str, any]:
        """
        Validate that epics don't overlap horizontally.
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        if len(self.epics) < 2:
            return {'passed': True, 'errors': []}
        
        # Sort epics by x position
        sorted_epics = sorted(self.epics.items(), key=lambda x: x[1]['x'])
        
        for i in range(len(sorted_epics) - 1):
            epic1_id, epic1 = sorted_epics[i]
            epic2_id, epic2 = sorted_epics[i + 1]
            
            epic1_right = epic1['x'] + epic1['width']
            epic2_left = epic2['x']
            
            # Check if epics overlap
            if epic1_right > epic2_left:
                overlap = epic1_right - epic2_left
                errors.append({
                    'type': 'epic_horizontal_overlap',
                    'epic1_id': epic1_id,
                    'epic2_id': epic2_id,
                    'epic1_name': epic1['name'],
                    'epic2_name': epic2['name'],
                    'overlap_amount': overlap,
                    'epic1_right': epic1_right,
                    'epic2_left': epic2_left
                })
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_all(self) -> Dict[str, any]:
        """Run all validation checks."""
        results = {
            'drawio_file': str(self.drawio_path),
            'epics_count': len(self.epics),
            'features_count': len(self.features),
            'stories_count': len(self.stories),
            'validations': {}
        }
        
        # Run all validations
        results['validations']['feature_vertical_stack'] = self.validate_feature_vertical_stack()
        results['validations']['epic_width'] = self.validate_epic_width()
        results['validations']['epic_horizontal_separation'] = self.validate_epic_horizontal_separation()
        
        # Overall pass/fail
        all_passed = all(
            v.get('passed', False) 
            for v in results['validations'].values()
        )
        results['all_passed'] = all_passed
        
        return results


def test_multiple_epics_features():
    """Test the multiple epics and features scenario."""
    print("="*80)
    print("Testing Multiple Epics and Features Positioning")
    print("="*80)
    
    # Setup paths
    acceptance_dir = Path(__file__).parent
    input_dir = acceptance_dir / "input"
    output_dir = acceptance_dir / "outputs"
    drawio_dir = output_dir / "drawio"
    
    # Input story graph
    story_graph_path = input_dir / "multiple_epics_features_test_story_graph.json"
    
    if not story_graph_path.exists():
        print(f"[ERROR] Story graph file not found: {story_graph_path}")
        return False
    
    # Render the diagram
    print(f"\n1. Rendering story graph: {story_graph_path}")
    drawio_path = drawio_dir / "multiple_epics_features_test_rendered.drawio"
    
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=story_graph,
        output_path=drawio_path
    )
    
    print(f"   [OK] Rendered to: {drawio_path}")
    
    # Validate positioning
    print(f"\n2. Validating epic and feature positioning...")
    validator = PositioningValidator(drawio_path)
    
    results = validator.validate_all()
    
    print(f"\n   Epics found: {results['epics_count']}")
    print(f"   Features found: {results['features_count']}")
    print(f"   Stories found: {results['stories_count']}")
    
    # Print validation results
    print(f"\n3. Validation Results:")
    print(f"   {'='*76}")
    
    all_passed = True
    
    # Feature vertical stacking
    stack_result = results['validations']['feature_vertical_stack']
    if stack_result['passed']:
        print(f"   [OK] Feature vertical stacking: PASSED")
    else:
        all_passed = False
        print(f"   [FAIL] Feature vertical stacking: FAILED")
        for error in stack_result['errors']:
            print(f"      - {error['feature1_name']} overlaps {error['feature2_name']} by {error['overlap_amount']:.1f}px")
    
    # Epic width
    width_result = results['validations']['epic_width']
    if width_result['passed']:
        print(f"   [OK] Epic width validation: PASSED")
    else:
        all_passed = False
        print(f"   [FAIL] Epic width validation: FAILED")
        for error in width_result['errors']:
            print(f"      - Epic '{error['epic_name']}' width {error['epic_width']:.1f}px is too narrow")
            print(f"        Required: {error['min_required_width']:.1f}px (max feature: {error['max_feature_width']:.1f}px)")
    
    # Epic horizontal separation
    separation_result = results['validations']['epic_horizontal_separation']
    if separation_result['passed']:
        print(f"   [OK] Epic horizontal separation: PASSED")
    else:
        all_passed = False
        print(f"   [FAIL] Epic horizontal separation: FAILED")
        for error in separation_result['errors']:
            print(f"      - Epic '{error['epic1_name']}' overlaps '{error['epic2_name']}' by {error['overlap_amount']:.1f}px")
    
    # Save detailed results
    results_path = output_dir / "multiple_epics_features_test_validation.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n4. Detailed results saved to: {results_path}")
    
    print(f"\n{'='*80}")
    if all_passed:
        print(f"[OK] All validations passed!")
    else:
        print(f"[FAIL] Some validations failed. See details above and in {results_path}")
    print(f"{'='*80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_multiple_epics_features()
    sys.exit(0 if success else 1)




