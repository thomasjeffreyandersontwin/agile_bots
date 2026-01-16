"""
Scenario-Based Acceptance Tests for Story IO

Each scenario is in its own folder with either:
- expected_story_graph.json (JSON-based test)
- expected_story-map-outline.drawio (DrawIO-based test)

Test workflows:
- JSON: render → sync → render → assert JSONs and DrawIOs match
- DrawIO: sync → merge → render → assert DrawIO matches
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import shutil

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram


class ScenarioBasedTestRunner:
    """Runs acceptance tests organized by scenario folders."""
    
    def __init__(self, scenarios_dir: Path, output_dir: Path = None):
        self.scenarios_dir = scenarios_dir
        # If output_dir not specified, outputs go in scenario folders
        self.output_dir = output_dir
        self.results = []
    
    def discover_scenarios(self) -> List[Path]:
        """Discover all scenario folders."""
        scenarios = []
        if not self.scenarios_dir.exists():
            return scenarios
        
        for item in self.scenarios_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it has an expected file
                expected_json = item / "expected_story_graph.json"
                expected_drawio = item / "expected_story-map-outline.drawio"
                if expected_json.exists() or expected_drawio.exists():
                    scenarios.append(item)
                    # Log input directory if present
                    input_dir = item / "input"
                    if input_dir.exists():
                        print(f"   Scenario '{item.name}' has input directory")
        
        return sorted(scenarios)
    
    def run_scenario(self, scenario_folder: Path) -> Dict[str, Any]:
        """Run a single scenario test."""
        scenario_name = scenario_folder.name
        print(f"\n{'='*80}")
        print(f"Running Scenario: {scenario_name}")
        print(f"{'='*80}")
        
        result = {
            'scenario': scenario_name,
            'scenario_folder': str(scenario_folder),
            'success': False,
            'files': {},
            'assertions': {}
        }
        
        try:
            # Determine test type
            expected_json = scenario_folder / "expected_story_graph.json"
            expected_drawio = scenario_folder / "expected_story-map-outline.drawio"
            
            if expected_json.exists():
                result.update(self._run_json_scenario(scenario_folder, expected_json))
            elif expected_drawio.exists():
                result.update(self._run_drawio_scenario(scenario_folder, expected_drawio))
            else:
                raise ValueError(f"No expected file found in {scenario_folder}")
            
            # Check if all assertions passed
            all_passed = self._check_all_assertions_passed(result.get('assertions', {}))
            result['success'] = all_passed
            
            if all_passed:
                print(f"\n[OK] Scenario '{scenario_name}' completed successfully")
            else:
                print(f"\n[FAIL] Scenario '{scenario_name}' failed: one or more assertions failed")
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            print(f"\n[FAIL] Error in scenario '{scenario_name}': {e}")
            import traceback
            traceback.print_exc()
        
        self.results.append(result)
        return result
    
    def _run_json_scenario(self, scenario_folder: Path, expected_json: Path) -> Dict[str, Any]:
        """
        Run JSON-based scenario: render → sync → render → assert JSONs and DrawIOs match.
        """
        scenario_name = scenario_folder.name
        # Output goes in scenario folder, just called "actual"
        if self.output_dir:
            scenario_output = self.output_dir / scenario_name
        else:
            scenario_output = scenario_folder / "actual"
        scenario_output.mkdir(parents=True, exist_ok=True)
        
        # Delete all contents of actual directory to start fresh
        if scenario_output.exists():
            for file in scenario_output.iterdir():
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    import shutil
                    shutil.rmtree(file)
            print(f"   [OK] Cleared contents of actual directory: {scenario_output}")
        
        # Check for input directory
        input_dir = scenario_folder / "input"
        if input_dir.exists():
            print(f"   Found input directory: {input_dir}")
        
        result = {
            'type': 'json',
            'files': {},
            'assertions': {},
            'input_dir': str(input_dir) if input_dir.exists() else None
        }
        
        print(f"\n[JSON Scenario] Expected: {expected_json}")
        
        # Check if expected DrawIO exists (for layout extraction)
        expected_drawio = scenario_folder / "expected_story-map-outline.drawio"
        initial_layout_data = None
        if expected_drawio.exists():
            print(f"\n0. Extracting layout from expected DrawIO...")
            # Sync from expected DrawIO to extract layout
            temp_diagram = StoryIODiagram(drawio_file=expected_drawio)
            temp_sync_path = scenario_output / "temp_sync.json"
            temp_diagram.synchronize_outline(
                drawio_path=expected_drawio,
                original_path=expected_json,
                output_path=temp_sync_path,
                generate_report=True
            )
            # Load layout if generated
            temp_layout_path = temp_sync_path.parent / f"{temp_sync_path.stem}-layout.json"
            if temp_layout_path.exists():
                with open(temp_layout_path, 'r', encoding='utf-8') as f:
                    initial_layout_data = json.load(f)
                print(f"   [OK] Extracted layout from expected DrawIO")
        
        # Step 1: Render expected JSON to DrawIO
        print(f"\n1. Rendering expected JSON to DrawIO...")
        rendered1_path = scenario_output / "rendered1.drawio"
        
        with open(expected_json, 'r', encoding='utf-8') as f:
            expected_graph = json.load(f)
        
        # Check if this is an exploration test (has stories with Steps)
        has_steps = any(
            story.get('Steps') or story.get('steps')
            for epic in expected_graph.get('epics', [])
            for feature in epic.get('features', [])
            for story in feature.get('stories', [])
        )
        
        has_increments = len(expected_graph.get('increments', [])) > 0
        
        if has_steps and scenario_name == 'exploration_render_test':
            # Exploration mode: only render stories with Steps
            # For exploration_render_test, don't use layout_data on first render to calculate positions from scratch
            render_result1 = StoryIODiagram.render_exploration_from_graph(
                story_graph=expected_graph,
                output_path=rendered1_path,
                layout_data=None,  # Calculate positions from scratch for this test
                scope=None
            )
        elif has_increments:
            render_result1 = StoryIODiagram.render_increments_from_graph(
                story_graph=expected_graph,
                output_path=rendered1_path
            )
        else:
            render_result1 = StoryIODiagram.render_outline_from_graph(
                story_graph=expected_graph,
                output_path=rendered1_path
            )
        
        result['files']['rendered1_drawio'] = str(rendered1_path)
        print(f"   [OK] Rendered to: {rendered1_path}")
        
        # Step 2: Sync from DrawIO back to JSON
        print(f"\n2. Syncing from DrawIO back to JSON...")
        synced_json_path = scenario_output / "synced.json"
        
        diagram = StoryIODiagram(drawio_file=rendered1_path)
        if has_increments:
            diagram.synchronize_increments(
                drawio_path=rendered1_path,
                original_path=expected_json,
                output_path=synced_json_path,
                generate_report=True
            )
        else:
            diagram.synchronize_outline(
                drawio_path=rendered1_path,
                original_path=expected_json,
                output_path=synced_json_path,
                generate_report=True
            )
        
        diagram.save_story_graph(synced_json_path)
        result['files']['synced_json'] = str(synced_json_path)
        print(f"   [OK] Synced to: {synced_json_path}")
        
        # Load layout if generated
        layout_path = synced_json_path.parent / f"{synced_json_path.stem}-layout.json"
        layout_data = None
        if layout_path.exists():
            with open(layout_path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            result['files']['layout'] = str(layout_path)
            print(f"   [OK] Layout saved to: {layout_path}")
        
        # Step 3: Render synced JSON to DrawIO again
        print(f"\n3. Rendering synced JSON to DrawIO again...")
        rendered2_path = scenario_output / "rendered2.drawio"
        
        with open(synced_json_path, 'r', encoding='utf-8') as f:
            synced_graph = json.load(f)
        
        if has_steps and scenario_name == 'exploration_render_test':
            # Exploration mode: only render stories with Steps
            render_result2 = StoryIODiagram.render_exploration_from_graph(
                story_graph=synced_graph,
                output_path=rendered2_path,
                layout_data=layout_data,
                scope=None
            )
        elif has_increments:
            render_result2 = StoryIODiagram.render_increments_from_graph(
                story_graph=synced_graph,
                output_path=rendered2_path,
                layout_data=layout_data
            )
        else:
            render_result2 = StoryIODiagram.render_outline_from_graph(
                story_graph=synced_graph,
                output_path=rendered2_path,
                layout_data=layout_data
            )
        
        result['files']['rendered2_drawio'] = str(rendered2_path)
        print(f"   [OK] Rendered to: {rendered2_path}")
        
        # Step 4: Assert JSONs match (expected vs synced)
        print(f"\n4. Asserting JSONs match...")
        json_match = self._assert_jsons_match(expected_json, synced_json_path)
        result['assertions']['json_match'] = json_match
        if json_match['match']:
            print(f"   [OK] Expected JSON matches synced JSON!")
        else:
            print(f"   [FAIL] Expected JSON doesn't match synced JSON: {json_match.get('message', 'Unknown error')}")
            if json_match.get('differences'):
                print(f"   Differences: {len(json_match['differences'])}")
                for diff in json_match['differences'][:5]:
                    print(f"      - {diff}")
        
        # Step 5: Extract JSONs from rendered DrawIOs and compare with expected
        print(f"\n5. Extracting and comparing JSONs from rendered DrawIOs...")
        
        # Extract JSON from rendered1
        temp_json1 = scenario_output / "temp_rendered1.json"
        diagram1 = StoryIODiagram(drawio_file=rendered1_path)
        diagram1.synchronize_outline(drawio_path=rendered1_path, output_path=temp_json1)
        diagram1.save_story_graph(temp_json1)
        
        # Extract JSON from rendered2
        temp_json2 = scenario_output / "temp_rendered2.json"
        diagram2 = StoryIODiagram(drawio_file=rendered2_path)
        diagram2.synchronize_outline(drawio_path=rendered2_path, output_path=temp_json2)
        diagram2.save_story_graph(temp_json2)
        
        # Compare expected JSON with extracted JSON from rendered1
        print(f"   5a. Comparing expected JSON with extracted JSON from rendered1...")
        json_match_rendered1 = self._assert_jsons_match(expected_json, temp_json1)
        result['assertions']['json_match_rendered1'] = json_match_rendered1
        if json_match_rendered1['match']:
            print(f"   [OK] Expected JSON matches rendered1 extracted JSON!")
        else:
            print(f"   [FAIL] Expected JSON doesn't match rendered1 extracted JSON: {json_match_rendered1.get('message', 'Unknown error')}")
            if json_match_rendered1.get('differences'):
                print(f"   Differences: {len(json_match_rendered1['differences'])}")
                for diff in json_match_rendered1['differences'][:5]:
                    print(f"      - {diff}")
        
        # Compare expected JSON with extracted JSON from rendered2
        print(f"   5b. Comparing expected JSON with extracted JSON from rendered2...")
        json_match_rendered2 = self._assert_jsons_match(expected_json, temp_json2)
        result['assertions']['json_match_rendered2'] = json_match_rendered2
        if json_match_rendered2['match']:
            print(f"   [OK] Expected JSON matches rendered2 extracted JSON!")
        else:
            print(f"   [FAIL] Expected JSON doesn't match rendered2 extracted JSON: {json_match_rendered2.get('message', 'Unknown error')}")
            if json_match_rendered2.get('differences'):
                print(f"   Differences: {len(json_match_rendered2['differences'])}")
                for diff in json_match_rendered2['differences'][:5]:
                    print(f"      - {diff}")
        
        # Step 6: Assert DrawIOs match (visual layout comparison)
        print(f"\n6. Asserting DrawIOs match (visual layout)...")
        
        # Compare expected DrawIO with rendered1 if it exists
        expected_drawio = scenario_folder / "expected_story-map-outline.drawio"
        if expected_drawio.exists():
            print(f"   6a. Comparing expected DrawIO with rendered1...")
            expected_match_rendered1 = self._assert_drawios_match(expected_drawio, rendered1_path)
            result['assertions']['expected_drawio_match_rendered1'] = expected_match_rendered1
            if expected_match_rendered1['match']:
                print(f"   [OK] Expected DrawIO matches rendered1!")
            else:
                print(f"   [FAIL] Expected DrawIO doesn't match rendered1: {expected_match_rendered1.get('message', 'Unknown error')}")
                if expected_match_rendered1.get('differences'):
                    print(f"   Differences: {len(expected_match_rendered1['differences'])} (XML: {expected_match_rendered1.get('xml_differences', 0)}, JSON: {expected_match_rendered1.get('json_differences', 0)})")
                    for diff in expected_match_rendered1['differences'][:10]:
                        print(f"      - {diff}")
            
            # Compare expected DrawIO with rendered2
            print(f"   6b. Comparing expected DrawIO with rendered2...")
            expected_match_rendered2 = self._assert_drawios_match(expected_drawio, rendered2_path)
            result['assertions']['expected_drawio_match_rendered2'] = expected_match_rendered2
            if expected_match_rendered2['match']:
                print(f"   [OK] Expected DrawIO matches rendered2!")
            else:
                print(f"   [FAIL] Expected DrawIO doesn't match rendered2: {expected_match_rendered2.get('message', 'Unknown error')}")
                if expected_match_rendered2.get('differences'):
                    print(f"   Differences: {len(expected_match_rendered2['differences'])} (XML: {expected_match_rendered2.get('xml_differences', 0)}, JSON: {expected_match_rendered2.get('json_differences', 0)})")
                    for diff in expected_match_rendered2['differences'][:10]:
                        print(f"      - {diff}")
        
        # Compare rendered1 with rendered2 (round-trip test)
        print(f"   6c. Comparing rendered1 with rendered2 (round-trip)...")
        drawio_match_roundtrip = self._assert_drawios_match(rendered1_path, rendered2_path)
        result['assertions']['drawio_match_roundtrip'] = drawio_match_roundtrip
        if drawio_match_roundtrip['match']:
            print(f"   [OK] Rendered1 matches rendered2 (round-trip)!")
        else:
            print(f"   [FAIL] Rendered1 doesn't match rendered2: {drawio_match_roundtrip.get('message', 'Unknown error')}")
            if drawio_match_roundtrip.get('differences'):
                print(f"   Differences: {len(drawio_match_roundtrip['differences'])} (XML: {drawio_match_roundtrip.get('xml_differences', 0)}, JSON: {drawio_match_roundtrip.get('json_differences', 0)})")
                for diff in drawio_match_roundtrip['differences'][:10]:
                    print(f"      - {diff}")
        
        # Clean up temp JSON files
        for temp_file in [temp_json1, temp_json2]:
            if temp_file.exists():
                temp_file.unlink()
            layout_file = temp_file.parent / f"{temp_file.stem}-layout.json"
            if layout_file.exists():
                layout_file.unlink()
        
        # Cleanup: Delete layout data files at test end
        print(f"\n7. Cleaning up layout data files...")
        layout_files_to_delete = [
            scenario_output / "temp_sync-layout.json",
            scenario_output / "temp_sync-merge-report.json",
            scenario_output / "temp_sync.json",
            scenario_output / "synced-layout.json",
            scenario_output / "synced-merge-report.json",
            scenario_output / "synced.json"
        ]
        deleted_count = 0
        for layout_file in layout_files_to_delete:
            if layout_file.exists():
                layout_file.unlink()
                deleted_count += 1
        if deleted_count > 0:
            print(f"   [OK] Deleted {deleted_count} layout data file(s)")
        else:
            print(f"   [OK] No layout data files to delete")
        
        return result
    
    def _run_drawio_scenario(self, scenario_folder: Path, expected_drawio: Path) -> Dict[str, Any]:
        """
        Run DrawIO-based scenario: sync → merge → render → assert DrawIO matches.
        """
        scenario_name = scenario_folder.name
        # Output goes in scenario folder, just called "actual"
        if self.output_dir:
            scenario_output = self.output_dir / scenario_name
        else:
            scenario_output = scenario_folder / "actual"
        scenario_output.mkdir(parents=True, exist_ok=True)
        
        # Delete all contents of actual directory to start fresh
        if scenario_output.exists():
            for file in scenario_output.iterdir():
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    import shutil
                    shutil.rmtree(file)
            print(f"   [OK] Cleared contents of actual directory: {scenario_output}")
        
        # Check for input directory
        input_dir = scenario_folder / "input"
        if input_dir.exists():
            print(f"   Found input directory: {input_dir}")
        
        result = {
            'type': 'drawio',
            'files': {},
            'assertions': {},
            'input_dir': str(input_dir) if input_dir.exists() else None
        }
        
        print(f"\n[DrawIO Scenario] Expected: {expected_drawio}")
        
        # Step 1: Sync from DrawIO to JSON
        print(f"\n1. Syncing from DrawIO to JSON...")
        extracted_json_path = scenario_output / "extracted.json"
        
        diagram = StoryIODiagram(drawio_file=expected_drawio)
        
        # Check if there's an original JSON to merge with (in input dir or scenario folder)
        original_json = None
        if input_dir.exists():
            original_json = input_dir / "original_story_graph.json"
            if not original_json.exists():
                original_json = None
        if original_json is None:
            original_json = scenario_folder / "original_story_graph.json"
        if original_json.exists():
            print(f"   Found original JSON for merge: {original_json}")
            diagram.synchronize_outline(
                drawio_path=expected_drawio,
                original_path=original_json,
                output_path=extracted_json_path,
                generate_report=True
            )
            
            # Step 2: Merge extracted with original
            print(f"\n2. Merging extracted with original...")
            merged_json_path = scenario_output / "merged.json"
            # Use the merge report that was already generated during sync
            merge_report_path = scenario_output / "extracted-merge-report.json"
            
            if not merge_report_path.exists():
                # Fallback: create a new report path
                merge_report_path = scenario_output / "merge_report.json"
            
            diagram.merge_story_graphs(
                extracted_path=extracted_json_path,
                original_path=original_json,
                report_path=merge_report_path,
                output_path=merged_json_path
            )
            
            result['files']['merge_report'] = str(merge_report_path)
            print(f"   [OK] Merged to: {merged_json_path}")
            print(f"   [OK] Merge report: {merge_report_path}")
            
            # Use merged JSON for rendering
            graph_to_render = merged_json_path
        else:
            # No original, just use extracted
            diagram.synchronize_outline(
                drawio_path=expected_drawio,
                output_path=extracted_json_path,
                generate_report=True
            )
            graph_to_render = extracted_json_path
        
        diagram.save_story_graph(extracted_json_path)
        result['files']['extracted_json'] = str(extracted_json_path)
        print(f"   [OK] Extracted to: {extracted_json_path}")
        
        # Load layout if generated
        layout_path = extracted_json_path.parent / f"{extracted_json_path.stem}-layout.json"
        layout_data = None
        if layout_path.exists():
            with open(layout_path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            result['files']['layout'] = str(layout_path)
            print(f"   [OK] Layout saved to: {layout_path}")
        
        # Step 3: Render JSON to DrawIO
        print(f"\n3. Rendering JSON to DrawIO...")
        rendered_path = scenario_output / "rendered.drawio"
        
        with open(graph_to_render, 'r', encoding='utf-8') as f:
            graph_to_render_data = json.load(f)
        
        has_increments = len(graph_to_render_data.get('increments', [])) > 0
        if has_increments:
            render_result = StoryIODiagram.render_increments_from_graph(
                story_graph=graph_to_render_data,
                output_path=rendered_path,
                layout_data=layout_data
            )
        else:
            render_result = StoryIODiagram.render_outline_from_graph(
                story_graph=graph_to_render_data,
                output_path=rendered_path,
                layout_data=layout_data
            )
        
        result['files']['rendered_drawio'] = str(rendered_path)
        print(f"   [OK] Rendered to: {rendered_path}")
        
        # Step 4: Assert rendered DrawIO matches expected
        print(f"\n4. Asserting rendered DrawIO matches expected...")
        drawio_match = self._assert_drawios_match(expected_drawio, rendered_path)
        result['assertions']['drawio_match'] = drawio_match
        if drawio_match['match']:
            print(f"   [OK] DrawIOs match!")
        else:
            print(f"   [FAIL] DrawIOs don't match: {drawio_match.get('message', 'Unknown error')}")
            if drawio_match.get('differences'):
                print(f"   Differences: {len(drawio_match['differences'])}")
                for diff in drawio_match['differences'][:5]:
                    print(f"      - {diff}")
        
        # Cleanup: Delete layout data files at test end
        print(f"\n5. Cleaning up layout data files...")
        layout_files_to_delete = [
            scenario_output / "extracted-layout.json",
            scenario_output / "extracted-merge-report.json",
            scenario_output / "extracted.json",
            scenario_output / "merged.json",
            scenario_output / "merge_report.json"
        ]
        deleted_count = 0
        for layout_file in layout_files_to_delete:
            if layout_file.exists():
                layout_file.unlink()
                deleted_count += 1
        if deleted_count > 0:
            print(f"   [OK] Deleted {deleted_count} layout data file(s)")
        else:
            print(f"   [OK] No layout data files to delete")
        
        return result
    
    def _check_all_assertions_passed(self, assertions: Dict[str, Any]) -> bool:
        """Check if all assertions in the dictionary passed."""
        for key, assertion_result in assertions.items():
            if isinstance(assertion_result, dict):
                if not assertion_result.get('match', False):
                    return False
        return True
    
    def _assert_jsons_match(self, json1_path: Path, json2_path: Path) -> Dict[str, Any]:
        """Assert two JSON story graphs match."""
        with open(json1_path, 'r', encoding='utf-8') as f:
            json1 = json.load(f)
        
        with open(json2_path, 'r', encoding='utf-8') as f:
            json2 = json.load(f)
        
        differences = []
        
        # Compare epics count
        epics1 = len(json1.get('epics', []))
        epics2 = len(json2.get('epics', []))
        if epics1 != epics2:
            differences.append(f"Epic count mismatch: {epics1} vs {epics2}")
        
        # Compare features count
        features1 = sum(len(epic.get('features', [])) for epic in json1.get('epics', []))
        features2 = sum(len(epic.get('features', [])) for epic in json2.get('epics', []))
        if features1 != features2:
            differences.append(f"Feature count mismatch: {features1} vs {features2}")
        
        # Compare stories count
        stories1 = sum(
            len(feature.get('stories', []))
            for epic in json1.get('epics', [])
            for feature in epic.get('features', [])
        )
        stories2 = sum(
            len(feature.get('stories', []))
            for epic in json2.get('epics', [])
            for feature in epic.get('features', [])
        )
        if stories1 != stories2:
            differences.append(f"Story count mismatch: {stories1} vs {stories2}")
        
        # Compare increments count
        increments1 = len(json1.get('increments', []))
        increments2 = len(json2.get('increments', []))
        if increments1 != increments2:
            differences.append(f"Increment count mismatch: {increments1} vs {increments2}")
        
        # Deep comparison of structure (simplified - could be more thorough)
        # For now, just check counts and basic structure
        
        return {
            'match': len(differences) == 0,
            'differences': differences,
            'message': 'JSONs match' if len(differences) == 0 else f'{len(differences)} differences found'
        }
    
    def _assert_drawios_match(self, drawio1_path: Path, drawio2_path: Path) -> Dict[str, Any]:
        """
        Assert two DrawIO files match by comparing XML structure directly.
        Compares positions, sizes, text content, and styles of all cells.
        """
        import xml.etree.ElementTree as ET
        
        differences = []
        
        # Parse both DrawIO files
        try:
            tree1 = ET.parse(drawio1_path)
            root1 = tree1.getroot()
            tree2 = ET.parse(drawio2_path)
            root2 = tree2.getroot()
        except Exception as e:
            return {
                'match': False,
                'differences': [f"Failed to parse DrawIO files: {e}"],
                'message': f"Parse error: {e}"
            }
        
        # Find all mxCell elements (excluding root cells with id="0" and id="1")
        def get_cells(root):
            cells = {}
            for cell in root.findall('.//mxCell'):
                cell_id = cell.get('id')
                if cell_id and cell_id not in ['0', '1']:
                    cells[cell_id] = cell
            return cells
        
        cells1 = get_cells(root1)
        cells2 = get_cells(root2)
        
        # Compare cell counts
        if len(cells1) != len(cells2):
            differences.append(f"Cell count mismatch: {len(cells1)} vs {len(cells2)}")
        
        # Get all cell IDs (union of both)
        all_cell_ids = set(cells1.keys()) | set(cells2.keys())
        
        # Compare each cell
        for cell_id in sorted(all_cell_ids):
            cell1 = cells1.get(cell_id)
            cell2 = cells2.get(cell_id)
            
            if cell1 is None:
                differences.append(f"Cell {cell_id} missing in first DrawIO")
                continue
            if cell2 is None:
                differences.append(f"Cell {cell_id} missing in second DrawIO")
                continue
            
            # Compare value (text content)
            value1 = cell1.get('value', '')
            value2 = cell2.get('value', '')
            if value1 != value2:
                # Only report if it's a significant difference (not just whitespace)
                if value1.strip() != value2.strip():
                    differences.append(f"Cell {cell_id} value mismatch")
            
            # Compare style
            style1 = cell1.get('style', '')
            style2 = cell2.get('style', '')
            if style1 != style2:
                differences.append(f"Cell {cell_id} style mismatch")
            
            # Compare geometry (position and size)
            geom1 = cell1.find('mxGeometry')
            geom2 = cell2.find('mxGeometry')
            
            if geom1 is None and geom2 is None:
                continue
            if geom1 is None:
                differences.append(f"Cell {cell_id} missing geometry in first DrawIO")
                continue
            if geom2 is None:
                differences.append(f"Cell {cell_id} missing geometry in second DrawIO")
                continue
            
            # Compare x, y, width, height
            x1 = float(geom1.get('x', 0))
            x2 = float(geom2.get('x', 0))
            y1 = float(geom1.get('y', 0))
            y2 = float(geom2.get('y', 0))
            w1 = float(geom1.get('width', 0))
            w2 = float(geom2.get('width', 0))
            h1 = float(geom1.get('height', 0))
            h2 = float(geom2.get('height', 0))
            
            # Allow small floating point differences (0.1px tolerance)
            tolerance = 0.1
            if abs(x1 - x2) > tolerance:
                differences.append(f"Cell {cell_id} x position mismatch: {x1} vs {x2}")
            if abs(y1 - y2) > tolerance:
                differences.append(f"Cell {cell_id} y position mismatch: {y1} vs {y2}")
            if abs(w1 - w2) > tolerance:
                differences.append(f"Cell {cell_id} width mismatch: {w1} vs {w2}")
            if abs(h1 - h2) > tolerance:
                differences.append(f"Cell {cell_id} height mismatch: {h1} vs {h2}")
        
        # Also compare extracted JSONs for structural validation
        temp_dir = self.output_dir if self.output_dir else self.scenarios_dir
        temp_json1 = temp_dir / "temp_extract1.json"
        temp_json2 = temp_dir / "temp_extract2.json"
        
        json_differences = []
        try:
            # Extract from first DrawIO
            diagram1 = StoryIODiagram(drawio_file=drawio1_path)
            diagram1.synchronize_outline(
                drawio_path=drawio1_path,
                output_path=temp_json1
            )
            diagram1.save_story_graph(temp_json1)
            
            # Extract from second DrawIO
            diagram2 = StoryIODiagram(drawio_file=drawio2_path)
            diagram2.synchronize_outline(
                drawio_path=drawio2_path,
                output_path=temp_json2
            )
            diagram2.save_story_graph(temp_json2)
            
            # Compare the extracted JSONs
            json_match = self._assert_jsons_match(temp_json1, temp_json2)
            if not json_match['match']:
                json_differences.extend(json_match.get('differences', []))
        
        finally:
            # Clean up temp files
            for temp_file in [temp_json1, temp_json2]:
                if temp_file.exists():
                    temp_file.unlink()
                layout_file = temp_file.parent / f"{temp_file.stem}-layout.json"
                if layout_file.exists():
                    layout_file.unlink()
        
        # Combine differences
        all_differences = differences + json_differences
        
        return {
            'match': len(all_differences) == 0,
            'differences': all_differences,
            'message': 'DrawIOs match' if len(all_differences) == 0 else f'{len(all_differences)} differences found',
            'xml_differences': len(differences),
            'json_differences': len(json_differences)
        }
    
    def run_all(self) -> List[Dict[str, Any]]:
        """Run all discovered scenarios."""
        scenarios = self.discover_scenarios()
        print(f"\nDiscovered {len(scenarios)} scenarios:")
        for scenario in scenarios:
            print(f"  - {scenario.name}")
        
        for scenario in scenarios:
            self.run_scenario(scenario)
        
        return self.results
    
    def print_summary(self):
        """Print summary of all test results."""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('success', False))
        failed = total - passed
        
        print(f"Total scenarios: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print(f"\nFailed scenarios:")
            for result in self.results:
                if not result.get('success', False):
                    print(f"  - {result['scenario']}: {result.get('error', 'Unknown error')}")
        
        # Save summary
        if self.output_dir:
            summary_path = self.output_dir / "test_summary.json"
        else:
            summary_path = self.scenarios_dir / "test_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total': total,
                'passed': passed,
                'failed': failed,
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nSummary saved to: {summary_path}")


def main():
    """Main entry point for scenario-based tests."""
    parser = argparse.ArgumentParser(description='Run scenario-based acceptance tests')
    parser.add_argument(
        '--scenario',
        type=str,
        help='Run specific scenario folder name (e.g., complex_story_graph)'
    )
    parser.add_argument(
        '--scenarios-dir',
        type=str,
        default='scenarios',
        help='Directory containing scenario folders (default: scenarios)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for test results (default: None = outputs go in scenario folders with _actual suffix)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths relative to acceptance directory
    acceptance_dir = Path(__file__).parent
    scenarios_dir = acceptance_dir / args.scenarios_dir
    output_dir = None
    if args.output_dir:
        output_dir = acceptance_dir / args.output_dir
    
    runner = ScenarioBasedTestRunner(scenarios_dir, output_dir)
    
    if args.scenario:
        # Run single scenario
        scenario_folder = scenarios_dir / args.scenario
        if not scenario_folder.exists():
            print(f"Error: Scenario folder not found: {scenario_folder}")
            sys.exit(1)
        
        runner.run_scenario(scenario_folder)
    else:
        # Run all scenarios
        runner.run_all()
    
    runner.print_summary()
    
    # Exit with error code if any tests failed
    failed = sum(1 for r in runner.results if not r.get('success', False))
    sys.exit(1 if failed > 0 else 0)


if __name__ == '__main__':
    main()

