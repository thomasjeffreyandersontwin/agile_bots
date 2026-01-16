"""
Acceptance Tests for Story IO

Real tests with real files that can be visually verified in DrawIO.
Tests follow: Build Graph → Render → Sync Back → Verify
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram


class AcceptanceTestRunner:
    """Runs acceptance tests and generates real output files for visual verification."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Create drawio subdirectory for DrawIO files
        self.drawio_dir = output_dir / "drawio"
        self.drawio_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
    
    def run_scenario(self, scenario_name: str, story_graph_path: Path,
                    layout_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run a single scenario: render → sync → verify
        
        Args:
            scenario_name: Name of the scenario
            story_graph_path: Path to story graph JSON
            layout_path: Optional path to layout JSON
        
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*80}")
        print(f"Running Scenario: {scenario_name}")
        print(f"{'='*80}")
        
        # Use flat file structure with prefixed names
        result = {
            'scenario': scenario_name,
            'story_graph': str(story_graph_path),
            'output_dir': str(self.output_dir),
            'success': False,
            'files': {}
        }
        
        try:
            # Step 1: Load story graph
            print(f"\n1. Loading story graph: {story_graph_path}")
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                story_graph = json.load(f)
            
            epics_count = len(story_graph.get('epics', []))
            increments_count = len(story_graph.get('increments', []))
            print(f"   [OK] Loaded {epics_count} epics")
            if increments_count > 0:
                print(f"   [OK] Loaded {increments_count} increments")
            
            # Step 2: Render to DrawIO (flat file with prefix)
            rendered_path = self.drawio_dir / f"{scenario_name}_rendered.drawio"
            print(f"\n2. Rendering to DrawIO: {rendered_path}")
            
            layout_data = None
            if layout_path and layout_path.exists():
                with open(layout_path, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                print(f"   Using layout from: {layout_path}")
            
            # Detect if story graph has increments and use appropriate renderer
            has_increments = increments_count > 0
            if has_increments:
                print(f"   Rendering in increments mode...")
                render_result = StoryIODiagram.render_increments_from_graph(
                    story_graph=story_graph,
                    output_path=rendered_path,
                    layout_data=layout_data
                )
            else:
                render_result = StoryIODiagram.render_outline_from_graph(
                    story_graph=story_graph,
                    output_path=rendered_path,
                    layout_data=layout_data
                )
            
            result['files']['rendered_drawio'] = str(rendered_path)
            print(f"   [OK] Rendered to: {rendered_path}")
            print(f"   Epics: {render_result['summary'].get('epics', 0)}")
            
            # Step 3: Sync back from DrawIO (flat file with prefix)
            synced_path = self.output_dir / f"{scenario_name}_synced.json"
            print(f"\n3. Syncing back from DrawIO: {synced_path}")
            
            diagram = StoryIODiagram(drawio_file=rendered_path)
            # Use appropriate sync method based on render mode
            if has_increments:
                print(f"   Syncing in increments mode...")
                sync_result = diagram.synchronize_increments(
                    drawio_path=rendered_path,
                    original_path=story_graph_path,
                    output_path=synced_path,  # Pass output_path so layout file gets saved
                    generate_report=True
                )
            else:
                sync_result = diagram.synchronize_outline(
                    drawio_path=rendered_path,
                    original_path=story_graph_path,
                    output_path=synced_path,  # Pass output_path so layout file gets saved
                    generate_report=True
                )
            
            diagram.save_story_graph(synced_path)
            result['files']['synced_json'] = str(synced_path)
            print(f"   [OK] Synced to: {synced_path}")
            
            # Extract and save layout file (for preserving positions in render->sync->render cycle)
            layout_path = synced_path.parent / f"{synced_path.stem}-layout.json"
            if layout_path.exists():
                # Copy to outputs folder with consistent naming
                output_layout_path = self.output_dir / f"{scenario_name}_layout.json"
                import shutil
                shutil.copy2(layout_path, output_layout_path)
                result['files']['layout'] = str(output_layout_path)
                print(f"   [OK] Layout saved to: {output_layout_path}")
            
            # Save sync report (flat file with prefix)
            if 'sync_report' in sync_result:
                report_path = self.output_dir / f"{scenario_name}_sync_report.json"
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(sync_result['sync_report'], f, indent=2, ensure_ascii=False)
                result['files']['sync_report'] = str(report_path)
                print(f"   [OK] Report saved to: {report_path}")
            
            # Step 4: Round-trip render (render again using layout to verify positions preserved)
            round_trip_rendered_path = None
            if output_layout_path and output_layout_path.exists():
                round_trip_rendered_path = self.drawio_dir / f"{scenario_name}_round_trip_rendered.drawio"
                print(f"\n4. Round-trip: Rendering again using layout file...")
                print(f"   Using layout: {output_layout_path}")
                
                # Load synced story graph and layout
                with open(synced_path, 'r', encoding='utf-8') as f:
                    synced_story_graph = json.load(f)
                
                with open(output_layout_path, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                
                # Render again with layout
                StoryIODiagram.render_outline_from_graph(
                    story_graph=synced_story_graph,
                    output_path=round_trip_rendered_path,
                    layout_data=layout_data
                )
                
                result['files']['round_trip_rendered_drawio'] = str(round_trip_rendered_path)
                print(f"   [OK] Round-trip rendered to: {round_trip_rendered_path}")
                
                # Extract layout from second render and compare
                print(f"\n4a. Extracting layout from round-trip render...")
                round_trip_synced_path = self.output_dir / f"{scenario_name}_round_trip_synced.json"
                
                # Sync the round-trip render to extract its layout
                diagram2 = StoryIODiagram(drawio_file=round_trip_rendered_path)
                diagram2.synchronize_outline(
                    drawio_path=round_trip_rendered_path,
                    output_path=round_trip_synced_path
                )
                
                # Extract layout from round-trip sync
                round_trip_layout_path = round_trip_synced_path.parent / f"{round_trip_synced_path.stem}-layout.json"
                if round_trip_layout_path.exists():
                    with open(round_trip_layout_path, 'r', encoding='utf-8') as f:
                        round_trip_layout = json.load(f)
                    
                    # Compare layouts
                    print(f"\n4b. Comparing positions between first and second render...")
                    position_comparison = self._compare_layouts(layout_data, round_trip_layout)
                    result['position_comparison'] = position_comparison
                    
                    if position_comparison.get('all_match'):
                        print(f"   [OK] All positions preserved!")
                    else:
                        mismatches = position_comparison.get('mismatches', [])
                        print(f"   [FAIL] Position mismatches found: {len(mismatches)}")
                        for i, mismatch in enumerate(mismatches[:5]):
                            diff = mismatch.get('difference', {})
                            diff_str = f"x:{diff.get('x', 0):.1f}, y:{diff.get('y', 0):.1f}"
                            print(f"      {i+1}. {mismatch.get('key', 'unknown')}: {diff_str}")
                        if len(mismatches) > 5:
                            print(f"      ... and {len(mismatches) - 5} more")
                    
                    # Save position comparison
                    position_comparison_path = self.output_dir / f"{scenario_name}_position_comparison.json"
                    with open(position_comparison_path, 'w', encoding='utf-8') as f:
                        json.dump(position_comparison, f, indent=2, ensure_ascii=False)
                    result['files']['position_comparison'] = str(position_comparison_path)
                else:
                    print(f"   [WARN] Could not extract layout from round-trip render")
            else:
                print(f"\n4. Skipping round-trip render (no layout file generated)")
            
            # Step 5: Compare original vs synced
            print(f"\n{'5' if round_trip_rendered_path else '4'}. Comparing original vs synced...")
            comparison = self._compare_graphs(story_graph_path, synced_path)
            result['comparison'] = comparison
            
            comparison_path = self.output_dir / f"{scenario_name}_comparison.json"
            with open(comparison_path, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False)
            result['files']['comparison'] = str(comparison_path)
            
            # Step 6: Summary
            step_num = 6 if round_trip_rendered_path else 5
            print(f"\n{step_num}. Summary:")
            print(f"   Original epics: {comparison['original']['epics_count']}")
            print(f"   Synced epics: {comparison['synced']['epics_count']}")
            print(f"   Epic match: {'[OK]' if comparison['epics_match'] else '[FAIL]'}")
            
            print(f"   Original features: {comparison['original']['features_count']}")
            print(f"   Synced features: {comparison['synced']['features_count']}")
            print(f"   Feature match: {'[OK]' if comparison['features_match'] else '[FAIL]'}")
            
            print(f"   Original stories: {comparison['original']['stories_count']}")
            print(f"   Synced stories: {comparison['synced']['stories_count']}")
            print(f"   Story match: {'[OK]' if comparison['stories_match'] else '[FAIL]'}")
            
            if comparison['original'].get('increments_count', 0) > 0 or comparison['synced'].get('increments_count', 0) > 0:
                print(f"   Original increments: {comparison['original'].get('increments_count', 0)}")
                print(f"   Synced increments: {comparison['synced'].get('increments_count', 0)}")
                print(f"   Increment match: {'[OK]' if comparison.get('increments_match', False) else '[FAIL]'}")
            
            if comparison.get('all_match'):
                print(f"\n   [OK] All checks passed!")
            elif comparison['differences']:
                print(f"\n   [FAIL] Differences found: {len(comparison['differences'])}")
                # Show first few differences
                for i, diff in enumerate(comparison['differences'][:5]):
                    print(f"      {i+1}. {diff.get('type', 'unknown')}: {diff}")
                if len(comparison['differences']) > 5:
                    print(f"      ... and {len(comparison['differences']) - 5} more")
            
            result['success'] = True
            print(f"\n[OK] Scenario '{scenario_name}' completed successfully")
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            print(f"\n[FAIL] Error in scenario '{scenario_name}': {e}")
            import traceback
            traceback.print_exc()
        
        self.results.append(result)
        return result
    
    def _compare_graphs(self, original_path: Path, synced_path: Path) -> Dict[str, Any]:
        """Compare original and synced story graphs with detailed checks."""
        with open(original_path, 'r', encoding='utf-8') as f:
            original = json.load(f)
        
        with open(synced_path, 'r', encoding='utf-8') as f:
            synced = json.load(f)
        
        # Helper functions
        def count_stories(graph):
            count = 0
            for epic in graph.get('epics', []):
                for feature in epic.get('features', []):
                    count += len(feature.get('stories', []))
            return count
        
        def count_features(graph):
            count = 0
            for epic in graph.get('epics', []):
                count += len(epic.get('features', []))
            return count
        
        def normalize_steps(steps):
            """Normalize Steps format for comparison (handle both string arrays and object arrays)."""
            if not steps:
                return []
            normalized = []
            for step in steps:
                if isinstance(step, str):
                    normalized.append(step.strip())
                elif isinstance(step, dict):
                    # Extract text from step object
                    text = step.get('description', step.get('text', step.get('step', '')))
                    if text:
                        normalized.append(str(text).strip())
            return normalized
        
        # Count components
        original_epics = len(original.get('epics', []))
        synced_epics = len(synced.get('epics', []))
        original_features = count_features(original)
        synced_features = count_features(synced)
        original_stories = count_stories(original)
        synced_stories = count_stories(synced)
        original_increments = len(original.get('increments', []))
        synced_increments = len(synced.get('increments', []))
        
        # Find differences
        differences = []
        
        # Epic count check
        if original_epics != synced_epics:
            differences.append({
                'type': 'epic_count_mismatch',
                'original': original_epics,
                'synced': synced_epics
            })
        
        # Sub-epic count check
        if original_features != synced_features:
            differences.append({
                'type': 'sub_epic_count_mismatch',
                'original': original_features,
                'synced': synced_features
            })
        
        # Story count check
        if original_stories != synced_stories:
            differences.append({
                'type': 'story_count_mismatch',
                'original': original_stories,
                'synced': synced_stories
            })
        
        # Increment count check
        if original_increments != synced_increments:
            differences.append({
                'type': 'increment_count_mismatch',
                'original': original_increments,
                'synced': synced_increments
            })
        
        # Compare epic names and children
        original_epic_map = {e.get('name'): e for e in original.get('epics', [])}
        synced_epic_map = {e.get('name'): e for e in synced.get('epics', [])}
        
        missing_epics = set(original_epic_map.keys()) - set(synced_epic_map.keys())
        extra_epics = set(synced_epic_map.keys()) - set(original_epic_map.keys())
        
        if missing_epics:
            differences.append({
                'type': 'missing_epics',
                'epics': list(missing_epics)
            })
        
        if extra_epics:
            differences.append({
                'type': 'extra_epics',
                'epics': list(extra_epics)
            })
        
        # Check epic children (features)
        for epic_name in original_epic_map:
            if epic_name not in synced_epic_map:
                continue
            
            orig_epic = original_epic_map[epic_name]
            synced_epic = synced_epic_map[epic_name]
            
            orig_features = {f.get('name'): f for f in orig_epic.get('features', [])}
            synced_features_map = {f.get('name'): f for f in synced_epic.get('features', [])}
            
            # Check estimated_stories on epic
            orig_est = orig_epic.get('estimated_stories')
            synced_est = synced_epic.get('estimated_stories')
            if orig_est != synced_est:
                differences.append({
                    'type': 'epic_estimated_stories_mismatch',
                    'epic': epic_name,
                    'original': orig_est,
                    'synced': synced_est
                })
            
            # Check feature children match
            missing_features = set(orig_features.keys()) - set(synced_features_map.keys())
            extra_features = set(synced_features_map.keys()) - set(orig_features.keys())
            
            if missing_features:
                differences.append({
                    'type': 'missing_features_in_epic',
                    'epic': epic_name,
                    'features': list(missing_features)
                })
            
            if extra_features:
                differences.append({
                    'type': 'extra_features_in_epic',
                    'epic': epic_name,
                    'features': list(extra_features)
                })
            
            # Check feature children (stories) and their properties
            for feature_name in orig_features:
                if feature_name not in synced_features_map:
                    continue
                
                orig_feat = orig_features[feature_name]
                synced_feat = synced_features_map[feature_name]
                
                # Check estimated_stories on feature
                orig_feat_est = orig_feat.get('estimated_stories')
                synced_feat_est = synced_feat.get('estimated_stories')
                if orig_feat_est != synced_feat_est:
                    differences.append({
                        'type': 'feature_estimated_stories_mismatch',
                        'epic': epic_name,
                        'feature': feature_name,
                        'original': orig_feat_est,
                        'synced': synced_feat_est
                    })
                
                # Check story children
                orig_stories = {s.get('name'): s for s in orig_feat.get('stories', [])}
                synced_stories_map = {s.get('name'): s for s in synced_feat.get('stories', [])}
                
                missing_stories = set(orig_stories.keys()) - set(synced_stories_map.keys())
                extra_stories = set(synced_stories_map.keys()) - set(orig_stories.keys())
                
                if missing_stories:
                    differences.append({
                        'type': 'missing_stories_in_feature',
                        'epic': epic_name,
                        'feature': feature_name,
                        'stories': list(missing_stories)
                    })
                
                if extra_stories:
                    differences.append({
                        'type': 'extra_stories_in_feature',
                        'epic': epic_name,
                        'feature': feature_name,
                        'stories': list(extra_stories)
                    })
                
                # Check story properties for matching stories
                for story_name in orig_stories:
                    if story_name not in synced_stories_map:
                        continue
                    
                    orig_story = orig_stories[story_name]
                    synced_story = synced_stories_map[story_name]
                    
                    # Check story type
                    orig_type = orig_story.get('story_type', 'user')
                    synced_type = synced_story.get('story_type', 'user')
                    if orig_type != synced_type:
                        differences.append({
                            'type': 'story_type_mismatch',
                            'epic': epic_name,
                            'feature': feature_name,
                            'story': story_name,
                            'original': orig_type,
                            'synced': synced_type
                        })
                    
                    # Check users (story <> user relationship)
                    orig_users = set(orig_story.get('users', []))
                    synced_users = set(synced_story.get('users', []))
                    if orig_users != synced_users:
                        differences.append({
                            'type': 'story_users_mismatch',
                            'epic': epic_name,
                            'feature': feature_name,
                            'story': story_name,
                            'original': list(orig_users),
                            'synced': list(synced_users)
                        })
                    
                    # Check Steps/acceptance criteria
                    orig_steps = normalize_steps(orig_story.get('Steps', []) or orig_story.get('steps', []))
                    synced_steps = normalize_steps(synced_story.get('Steps', []) or synced_story.get('steps', []))
                    
                    if orig_steps != synced_steps:
                        differences.append({
                            'type': 'story_steps_mismatch',
                            'epic': epic_name,
                            'feature': feature_name,
                            'story': story_name,
                            'original': orig_steps,
                            'synced': synced_steps
                        })
        
        # Check increments and their children
        original_increment_map = {inc.get('name'): inc for inc in original.get('increments', [])}
        synced_increment_map = {inc.get('name'): inc for inc in synced.get('increments', [])}
        
        for inc_name in original_increment_map:
            if inc_name not in synced_increment_map:
                differences.append({
                    'type': 'missing_increment',
                    'increment': inc_name
                })
                continue
            
            orig_inc = original_increment_map[inc_name]
            synced_inc = synced_increment_map[inc_name]
            
            # Check increment epic children
            orig_inc_epics = {e.get('name'): e for e in orig_inc.get('epics', [])}
            synced_inc_epics = {e.get('name'): e for e in synced_inc.get('epics', [])}
            
            for epic_name in orig_inc_epics:
                if epic_name not in synced_inc_epics:
                    differences.append({
                        'type': 'missing_epic_in_increment',
                        'increment': inc_name,
                        'epic': epic_name
                    })
                    continue
                
                orig_inc_epic = orig_inc_epics[epic_name]
                synced_inc_epic = synced_inc_epics[epic_name]
                
                # Check estimated_stories on increment epic
                orig_inc_epic_est = orig_inc_epic.get('estimated_stories')
                synced_inc_epic_est = synced_inc_epic.get('estimated_stories')
                if orig_inc_epic_est != synced_inc_epic_est:
                    differences.append({
                        'type': 'increment_epic_estimated_stories_mismatch',
                        'increment': inc_name,
                        'epic': epic_name,
                        'original': orig_inc_epic_est,
                        'synced': synced_inc_epic_est
                    })
                
                # Check increment epic feature children
                orig_inc_features = {f.get('name'): f for f in orig_inc_epic.get('features', [])}
                synced_inc_features = {f.get('name'): f for f in synced_inc_epic.get('features', [])}
                
                for feature_name in orig_inc_features:
                    if feature_name not in synced_inc_features:
                        differences.append({
                            'type': 'missing_feature_in_increment_epic',
                            'increment': inc_name,
                            'epic': epic_name,
                            'feature': feature_name
                        })
                        continue
                    
                    orig_inc_feat = orig_inc_features[feature_name]
                    synced_inc_feat = synced_inc_features[feature_name]
                    
                    # Check estimated_stories on increment feature
                    orig_inc_feat_est = orig_inc_feat.get('estimated_stories')
                    synced_inc_feat_est = synced_inc_feat.get('estimated_stories')
                    if orig_inc_feat_est != synced_inc_feat_est:
                        differences.append({
                            'type': 'increment_feature_estimated_stories_mismatch',
                            'increment': inc_name,
                            'epic': epic_name,
                            'feature': feature_name,
                            'original': orig_inc_feat_est,
                            'synced': synced_inc_feat_est
                        })
        
        for inc_name in synced_increment_map:
            if inc_name not in original_increment_map:
                differences.append({
                    'type': 'extra_increment',
                    'increment': inc_name
                })
        
        return {
            'original': {
                'epics_count': original_epics,
                'features_count': original_features,
                'stories_count': original_stories,
                'increments_count': original_increments
            },
            'synced': {
                'epics_count': synced_epics,
                'features_count': synced_features,
                'stories_count': synced_stories,
                'increments_count': synced_increments
            },
            'epics_match': original_epics == synced_epics,
            'features_match': original_features == synced_features,
            'stories_match': original_stories == synced_stories,
            'increments_match': original_increments == synced_increments,
            'all_match': len(differences) == 0,
            'differences': differences
        }
    
    def _compare_layouts(self, layout1: Dict[str, Any], layout2: Dict[str, Any], tolerance: float = 1.0) -> Dict[str, Any]:
        """
        Compare two layout data dictionaries to verify positions are preserved.
        
        Args:
            layout1: First layout data (from initial sync)
            layout2: Second layout data (from round-trip render/sync)
            tolerance: Tolerance for position comparison (default 1.0 pixel)
        
        Returns:
            Dictionary with comparison results
        """
        all_keys = set(layout1.keys()) | set(layout2.keys())
        mismatches = []
        matches = []
        missing_in_2 = []
        extra_in_2 = []
        
        for key in all_keys:
            if key not in layout1:
                extra_in_2.append(key)
                continue
            if key not in layout2:
                missing_in_2.append(key)
                continue
            
            pos1 = layout1[key]
            pos2 = layout2[key]
            
            # Handle both formats: {x, y} for stories/users or {x, y, width, height} for epics/features
            x1 = pos1.get('x', 0)
            y1 = pos1.get('y', 0)
            w1 = pos1.get('width', 0)
            h1 = pos1.get('height', 0)
            
            x2 = pos2.get('x', 0)
            y2 = pos2.get('y', 0)
            w2 = pos2.get('width', 0)
            h2 = pos2.get('height', 0)
            
            # Check if positions match (within tolerance)
            x_diff = abs(x1 - x2)
            y_diff = abs(y1 - y2)
            w_diff = abs(w1 - w2)
            h_diff = abs(h1 - h2)
            
            if x_diff <= tolerance and y_diff <= tolerance and w_diff <= tolerance and h_diff <= tolerance:
                matches.append(key)
            else:
                mismatches.append({
                    'key': key,
                    'first': pos1,
                    'second': pos2,
                    'difference': {
                        'x': x_diff,
                        'y': y_diff,
                        'width': w_diff,
                        'height': h_diff
                    }
                })
        
        return {
            'all_match': len(mismatches) == 0 and len(missing_in_2) == 0 and len(extra_in_2) == 0,
            'matches_count': len(matches),
            'mismatches_count': len(mismatches),
            'missing_in_second_count': len(missing_in_2),
            'extra_in_second_count': len(extra_in_2),
            'mismatches': mismatches[:20],  # Limit to first 20 for readability
            'missing_in_second': missing_in_2[:20],
            'extra_in_second': extra_in_2[:20],
            'tolerance': tolerance
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all test results."""
        summary = {
            'total_scenarios': len(self.results),
            'passed': sum(1 for r in self.results if r.get('success')),
            'failed': sum(1 for r in self.results if not r.get('success')),
            'results': self.results
        }
        
        summary_path = self.output_dir / "test_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary


def main():
    """Run all acceptance test scenarios."""
    print("="*80)
    print("Story IO Acceptance Tests")
    print("="*80)
    print("\nThese tests create real DrawIO files you can open and verify visually.")
    print("DrawIO files are in: acceptance/outputs/drawio/")
    print("Other output files (JSON, reports) are in: acceptance/outputs/")
    print("="*80)
    
    # Setup paths
    acceptance_dir = Path(__file__).parent
    input_dir = acceptance_dir / "input"
    outputs_dir = acceptance_dir / "outputs"
    
    # Create runner
    runner = AcceptanceTestRunner(outputs_dir)
    
    # Find all scenario files in input/ folder (flat structure)
    scenarios = []
    if input_dir.exists():
        for input_file in input_dir.iterdir():
            if input_file.is_file() and input_file.name.endswith("_story_graph.json"):
                # Extract scenario name from filename (e.g., "complex_story_graph.json" -> "complex")
                scenario_name = input_file.name.replace("_story_graph.json", "")
                
                # Look for corresponding layout file
                layout_file = input_dir / f"{scenario_name}_layout.json"
                layout_path = layout_file if layout_file.exists() else None
                
                scenarios.append({
                    'name': scenario_name,
                    'story_graph': input_file,
                    'layout': layout_path
                })
    
    if not scenarios:
        print("\nNo scenarios found! Create files in acceptance/input/ with pattern: <name>_story_graph.json")
        return
    
    print(f"\nFound {len(scenarios)} scenario(s):")
    for scenario in scenarios:
        print(f"  - {scenario['name']}")
    
    # Run each scenario
    for scenario in scenarios:
        runner.run_scenario(
            scenario_name=scenario['name'],
            story_graph_path=scenario['story_graph'],
            layout_path=scenario['layout']
        )
    
    # Generate summary
    print(f"\n{'='*80}")
    print("Test Summary")
    print(f"{'='*80}")
    
    summary = runner.generate_summary()
    print(f"\nTotal scenarios: {summary['total_scenarios']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"\nSummary saved to: {outputs_dir / 'test_summary.json'}")
    
    print(f"\n{'='*80}")
    print("Next Steps:")
    print(f"{'='*80}")
    print("1. Open DrawIO files in acceptance/outputs/drawio/ to visually verify")
    print("2. Check comparison.json files in acceptance/outputs/ to see differences")
    print("3. Review sync_report.json files in acceptance/outputs/ for sync details")
    if scenarios:
        print(f"\nExample:")
        example_file = f"{scenarios[0]['name']}_rendered.drawio"
        print(f"  Open: {outputs_dir / 'drawio' / example_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

