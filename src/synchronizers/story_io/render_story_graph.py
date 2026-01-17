"""
Simple script to render any story graph JSON to DrawIO.

Usage:
    python render_story_graph.py <story_graph.json> [output.drawio]

Example:
    python render_story_graph.py demo/cheap_wealth_online/docs/stories/structured.json
"""

import json
import sys
from pathlib import Path

from .story_io_diagram import StoryIODiagram


def convert_behavioral_ac_to_steps(story_data):
    """Convert behavioral_ac array to Steps format."""
    if 'behavioral_ac' in story_data and story_data['behavioral_ac']:
        steps = []
        for step_text in story_data['behavioral_ac']:
            step_type = "Given"
            step_lower = step_text.lower()
            if step_lower.startswith('when'):
                step_type = "When"
            elif step_lower.startswith('then'):
                step_type = "Then"
            elif step_lower.startswith('and') and steps:
                step_type = steps[-1]['type']
            
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
    
    if 'solution' in data:
        adapted['solution'] = data['solution']
    
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
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python render_story_graph.py <story_graph.json> [output.drawio]")
        print("\nExample:")
        print("  python render_story_graph.py demo/cheap_wealth_online/docs/stories/structured.json")
        sys.exit(1)
    
    # Get input file
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.parent / "story-map-outline.drawio"
    
    print(f"Loading: {input_path}")
    
    # Load and adapt
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    adapted_data = adapt_story_graph(data)
    
    # Render
    print(f"Rendering to: {output_path}")
    result = StoryIODiagram.render_outline_from_graph(
        story_graph=adapted_data,
        output_path=output_path
    )
    
    print(f"\n[SUCCESS] Rendered!")
    print(f"Output file: {output_path}")
    print(f"Epics: {result['summary'].get('epics', 0)}")
    print(f"\nOpen {output_path} in DrawIO to verify.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

