"""
Example: Load and render a story graph from structured.json

Converts format and renders to DrawIO.
"""

import json
import sys
import os
import argparse
from pathlib import Path

from ..story_io_diagram import StoryIODiagram


def convert_behavioral_ac_to_steps(story_data):
    """Convert behavioral_ac array to Steps format."""
    if 'behavioral_ac' in story_data and story_data['behavioral_ac']:
        steps = []
        for i, step_text in enumerate(story_data['behavioral_ac'], 1):
            # Determine step type from content
            step_type = "Given"
            step_lower = step_text.lower()
            if step_lower.startswith('when'):
                step_type = "When"
            elif step_lower.startswith('then'):
                step_type = "Then"
            elif step_lower.startswith('and'):
                step_type = steps[-1]['type'] if steps else "Given"
            
            steps.append({
                "description": step_text,
                "type": step_type
            })
        return steps
    return story_data.get('Steps', [])


def adapt_story_in_story_groups(story_data, epic_users=None):
    """Adapt a single story, converting acceptance_criteria to Steps."""
    adapted_story = story_data.copy()
    
    # Convert acceptance_criteria to Steps if present
    if 'acceptance_criteria' in adapted_story:
        steps = []
        for i, ac in enumerate(adapted_story['acceptance_criteria']):
            if isinstance(ac, str):
                # Determine step type from content
                step_type = "Given"
                ac_lower = ac.lower()
                if ac_lower.startswith('when'):
                    step_type = "When"
                elif ac_lower.startswith('then'):
                    step_type = "Then"
                elif ac_lower.startswith('and'):
                    step_type = steps[-1]['type'] if steps else "Given"
                
                steps.append({
                    "description": ac,
                    "type": step_type
                })
        
        if steps:
            adapted_story['Steps'] = steps
            # Keep acceptance_criteria for backward compatibility, but Steps takes precedence
    else:
        # Also handle behavioral_ac (legacy)
        steps = convert_behavioral_ac_to_steps(adapted_story)
        if steps:
            adapted_story['Steps'] = steps
    
    # Handle users
    if epic_users and not adapted_story.get('users'):
        adapted_story['users'] = epic_users
    
    return adapted_story


def adapt_sub_epic(sub_epic_data, epic_users=None):
    """Recursively adapt a sub_epic, preserving structure and converting stories."""
    adapted_sub_epic = {
        'name': sub_epic_data['name'],
        'sequential_order': sub_epic_data.get('sequential_order')
    }
    
    # Preserve other fields
    for key in ['domain_concepts', 'test_file', 'estimated_stories', 'story_count']:
        if key in sub_epic_data:
            adapted_sub_epic[key] = sub_epic_data[key]
    
    # Handle nested sub_epics (recursive)
    if 'sub_epics' in sub_epic_data:
        adapted_sub_epic['sub_epics'] = [
            adapt_sub_epic(nested_sub_epic, epic_users)
            for nested_sub_epic in sub_epic_data['sub_epics']
        ]
    
    # Handle story_groups (preserve structure, adapt stories within)
    if 'story_groups' in sub_epic_data:
        adapted_sub_epic['story_groups'] = []
        for story_group in sub_epic_data['story_groups']:
            adapted_group = {
                'type': story_group.get('type'),
                'connector': story_group.get('connector')
            }
            
            # Adapt stories in the group
            if 'stories' in story_group:
                adapted_group['stories'] = [
                    adapt_story_in_story_groups(story, epic_users)
                    for story in story_group['stories']
                ]
            
            adapted_sub_epic['story_groups'].append(adapted_group)
    
    # Handle direct stories (legacy format)
    if 'stories' in sub_epic_data:
        adapted_sub_epic['stories'] = [
            adapt_story_in_story_groups(story, epic_users)
            for story in sub_epic_data['stories']
        ]
    
    return adapted_sub_epic


def adapt_story_graph(data):
    """
    Adapt story graph to our expected format.
    Preserves sub_epics structure and converts acceptance_criteria/behavioral_ac to Steps.
    """
    adapted = {}
    
    # Copy solution if exists
    if 'solution' in data:
        adapted['solution'] = data['solution']
    
    # Adapt epics
    if 'epics' in data:
        adapted['epics'] = []
        for epic in data['epics']:
            adapted_epic = {
                'name': epic['name'],
                'sequential_order': epic.get('sequential_order')
            }
            
            # Preserve other epic-level fields
            for key in ['domain_concepts', 'estimated_stories', 'story_count']:
                if key in epic:
                    adapted_epic[key] = epic[key]
            
            # Handle users - use epic users if story users is empty
            epic_users = epic.get('users', [])
            
            # Adapt sub_epics (new format, preferred)
            if 'sub_epics' in epic:
                adapted_epic['sub_epics'] = [
                    adapt_sub_epic(sub_epic, epic_users)
                    for sub_epic in epic['sub_epics']
                ]
            
            # Adapt features (old format, for backward compatibility)
            if 'features' in epic:
                adapted_epic['features'] = []
                for feature in epic['features']:
                    adapted_feature = {
                        'name': feature['name'],
                        'sequential_order': feature.get('sequential_order')
                    }
                    
                    # Adapt stories
                    if 'stories' in feature:
                        adapted_feature['stories'] = []
                        for story in feature['stories']:
                            adapted_story = adapt_story_in_story_groups(story, epic_users)
                            adapted_feature['stories'].append(adapted_story)
                    
                    adapted_epic['features'].append(adapted_feature)
            
            # Handle direct stories on epic (if any)
            if 'stories' in epic:
                adapted_epic['stories'] = [
                    adapt_story_in_story_groups(story, epic_users)
                    for story in epic['stories']
                ]
            
            adapted['epics'].append(adapted_epic)
    
    # Adapt increments
    if 'increments' in data:
        adapted['increments'] = []
        for increment in data['increments']:
            adapted_increment = {
                'name': increment['name'],
                'priority': increment.get('priority', 'NEXT')
            }
            
            # Increments can have epics directly - use same adaptation logic
            if 'epics' in increment:
                adapted_increment['epics'] = []
                for epic in increment['epics']:
                    adapted_epic = {
                        'name': epic['name'],
                        'sequential_order': epic.get('sequential_order')
                    }
                    
                    # Preserve other epic-level fields
                    for key in ['domain_concepts', 'estimated_stories', 'story_count']:
                        if key in epic:
                            adapted_epic[key] = epic[key]
                    
                    epic_users = epic.get('users', [])
                    
                    # Adapt sub_epics (new format)
                    if 'sub_epics' in epic:
                        adapted_epic['sub_epics'] = [
                            adapt_sub_epic(sub_epic, epic_users)
                            for sub_epic in epic['sub_epics']
                        ]
                    
                    # Adapt features (old format, for backward compatibility)
                    if 'features' in epic:
                        adapted_epic['features'] = []
                        for feature in epic['features']:
                            adapted_feature = {
                                'name': feature['name'],
                                'sequential_order': feature.get('sequential_order')
                            }
                            
                            if 'stories' in feature:
                                adapted_feature['stories'] = [
                                    adapt_story_in_story_groups(story, epic_users)
                                    for story in feature['stories']
                                ]
                            
                            adapted_epic['features'].append(adapted_feature)
                    
                    # Handle direct stories on epic (if any)
                    if 'stories' in epic:
                        adapted_epic['stories'] = [
                            adapt_story_in_story_groups(story, epic_users)
                            for story in epic['stories']
                        ]
                    
                    adapted_increment['epics'].append(adapted_epic)
            
            adapted['increments'].append(adapted_increment)
    
    return adapted


def main():
    """Load structured.json and render to DrawIO."""
    # Path to the structured.json file (relative to workspace root)
    # Determine Python import root for imports; keep it separate from runtime workspace.
    python_workspace_root = Path(__file__).parent.parent.parent.parent.parent.parent

    # Resolve workspace from environment (WORKING_AREA preferred)
    parser = argparse.ArgumentParser(description='Load and render a story graph from structured.json')
    parser.add_argument('structured_path', nargs='?', help='Optional path to structured.json to load')
    args = parser.parse_args()

    from bots.base_bot.src.state.workspace import get_workspace_directory
    workspace_root = get_workspace_directory()

    if args.structured_path:
        structured_path = Path(args.structured_path)
    else:
        structured_path = workspace_root / "demo" / "cheap_wealth_online" / "docs" / "stories" / "structured.json"
    
    if not structured_path.exists():
        print(f"Error: File not found: {structured_path}")
        print(f"Current working directory: {Path.cwd()}")
        return 1
    
    print(f"Loading: {structured_path}")
    
    # Load and adapt the story graph
    with open(structured_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"Original epics: {len(original_data.get('epics', []))}")
    print(f"Original increments: {len(original_data.get('increments', []))}")
    
    # Adapt format
    adapted_data = adapt_story_graph(original_data)
    
    # Save adapted version for reference
    adapted_path = structured_path.parent / "structured_adapted.json"
    with open(adapted_path, 'w', encoding='utf-8') as f:
        json.dump(adapted_data, f, indent=2, ensure_ascii=False)
    print(f"Adapted format saved to: {adapted_path}")
    
    # Render outline
    output_path = structured_path.parent / "story-map-outline.drawio"
    print(f"\nRendering to: {output_path}")
    
    result = StoryIODiagram.render_outline_from_graph(
        story_graph=adapted_data,
        output_path=output_path
    )
    
    print(f"\n[OK] Render complete!")
    print(f"Output: {output_path}")
    print(f"Epics: {result['summary'].get('epics', 0)}")
    
    # Optionally render with increments
    if adapted_data.get('increments'):
        output_increments = structured_path.parent / "story-map-increments.drawio"
        print(f"\nRendering with increments to: {output_increments}")
        
        result_increments = StoryIODiagram.render_increments_from_graph(
            story_graph=adapted_data,
            output_path=output_increments
        )
        
        print(f"[OK] Increments render complete!")
        print(f"Output: {output_increments}")
        print(f"Epics: {result_increments['summary'].get('epics', 0)}")
        print(f"Increments: {result_increments['summary'].get('increments', 0)}")
    
    print(f"\n{'='*80}")
    print("Next steps:")
    print(f"1. Open {output_path} in DrawIO to verify")
    print(f"2. Check {adapted_path} to see adapted format")
    print(f"{'='*80}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

