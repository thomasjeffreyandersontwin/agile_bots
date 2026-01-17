"""
Story Tests Synchronizer

Renders pytest test files from story graph JSON.
Generates test files organized by sub-epic with test classes matching stories.
"""
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import json
import re


def format_test_method_from_scenario(scenario, scenario_name, test_method_name, background_steps=None):
    """Format a test method from a scenario."""
    steps = scenario.get('steps', [])
    scenario_type = scenario.get('type', 'happy_path')
    
    # Format docstring with scenario info
    docstring = f'        """{scenario_name} ({scenario_type})."""'
    
    # Format test method
    method_lines = [
        f"    def {test_method_name}(self, tmp_path):",
        docstring,
        "        # Given:",
    ]
    
    # Add background steps if provided
    if background_steps:
        for bg_step in background_steps:
            method_lines.append(f"        # {bg_step}")
    
    # Add scenario steps
    for step in steps:
        if step.strip():
            method_lines.append(f"        # {step}")
    
    method_lines.append("        # TODO: Implement test")
    method_lines.append("        pass")
    
    return "\n".join(method_lines)


def format_test_method_from_scenario_outline(scenario_outline, scenario_name, test_method_name, background_steps=None):
    """Format a parametrized test method from a scenario outline."""
    steps = scenario_outline.get('steps', [])
    scenario_type = scenario_outline.get('type', 'happy_path')
    examples = scenario_outline.get('examples', {})
    
    # Extract columns and rows
    columns = examples.get('columns', [])
    rows = examples.get('rows', [])
    
    # Format docstring
    docstring = f'        """{scenario_name} ({scenario_type})."""'
    
    # Format parametrize decorator
    if columns and rows:
        # Create parametrize string
        param_names = ", ".join(columns)
        param_values = []
        for row in rows:
            if isinstance(row, list):
                # Format row as tuple
                row_str = "(" + ", ".join(f'"{val}"' if isinstance(val, str) else str(val) for val in row) + ")"
            else:
                row_str = str(row)
            param_values.append(row_str)
        
        param_values_str = ",\n            ".join(param_values)
        parametrize = f"""    @pytest.mark.parametrize("{param_names}", [
            {param_values_str}
        ])"""
    else:
        parametrize = ""
    
    # Format test method
    method_lines = []
    if parametrize:
        method_lines.append(parametrize)
    
    # Build parameter list for method signature
    param_list = "tmp_path"
    if columns:
        param_list += ", " + ", ".join(columns)
    
    method_lines.extend([
        f"    def {test_method_name}(self, {param_list}):",
        docstring,
        "        # Given:",
    ])
    
    # Add background steps if provided
    if background_steps:
        for bg_step in background_steps:
            method_lines.append(f"        # {bg_step}")
    
    # Add scenario steps (with parameter placeholders)
    for step in steps:
        if step.strip():
            method_lines.append(f"        # {step}")
    
    method_lines.append("        # TODO: Implement test")
    method_lines.append("        pass")
    
    return "\n".join(method_lines)


def get_common_background(scenarios_list):
    """Extract common background steps shared across all scenarios."""
    if not scenarios_list:
        return None
    
    backgrounds = [s.get('background', []) for s in scenarios_list if s.get('background')]
    if not backgrounds:
        return None
    
    common = backgrounds[0]
    for bg in backgrounds[1:]:
        if bg != common:
            return None
    
    return common


def create_test_file_content(sub_epic, stories, epic_name):
    """Create test file content for a sub-epic."""
    sub_epic_name = sub_epic.get('name', '')
    test_file = sub_epic.get('test_file', f'test_{sub_epic_name.lower().replace(" ", "_")}.py')
    
    # File docstring
    file_docstring = f'"""{sub_epic_name} Tests\n\nTests for all stories in the \'{sub_epic_name}\' sub-epic:'
    for story in stories:
        file_docstring += f"\n- {story.get('name', '')}"
    file_docstring += '\n"""'
    
    # Imports
    imports = [
        "import pytest",
        "from pathlib import Path",
        "import json",
        ""
    ]
    
    # Helper functions section
    helpers = [
        "# ============================================================================",
        "# HELPER FUNCTIONS",
        "# ============================================================================",
        "",
        "# TODO: Add helper functions as needed",
        ""
    ]
    
    # Fixtures section
    fixtures = [
        "# ============================================================================",
        "# FIXTURES",
        "# ============================================================================",
        "",
        "# TODO: Add fixtures as needed",
        ""
    ]
    
    # Test classes
    test_classes = []
    for story in stories:
        story_name = story.get('name', '')
        test_class = story.get('test_class', f'Test{story_name.replace(" ", "")}')
        
        # Get scenarios and scenario outlines
        scenarios = story.get('scenarios', [])
        scenario_outlines = story.get('scenario_outlines', [])
        
        # Get common background
        all_scenarios = scenarios + scenario_outlines
        common_background = get_common_background(all_scenarios)
        
        # Class docstring
        class_docstring = f'class {test_class}:'
        class_docstring += f'\n    """Story: {story_name} - Tests {story_name.lower()}."""'
        
        test_classes.append(class_docstring)
        test_classes.append("")
        
        # Add test methods for scenarios
        for scenario in scenarios:
            scenario_name = scenario.get('name', '')
            test_method = scenario.get('test_method', f'test_{scenario_name.lower().replace(" ", "_")}')
            method_content = format_test_method_from_scenario(scenario, scenario_name, test_method, common_background)
            test_classes.append(method_content)
            test_classes.append("")
        
        # Add test methods for scenario outlines
        for scenario_outline in scenario_outlines:
            scenario_name = scenario_outline.get('name', '')
            test_method = scenario_outline.get('test_method', f'test_{scenario_name.lower().replace(" ", "_")}')
            method_content = format_test_method_from_scenario_outline(scenario_outline, scenario_name, test_method, common_background)
            test_classes.append(method_content)
            test_classes.append("")
    
    # Combine all parts
    content = "\n".join([
        file_docstring,
        "",
    ] + imports + helpers + fixtures + test_classes)
    
    return content


def extract_stories_from_sub_epic(sub_epic):
    """Extract all stories from a sub-epic."""
    stories = []
    for story_group in sub_epic.get('story_groups', []):
        stories.extend(story_group.get('stories', []))
    return stories


def process_sub_epic_for_tests(sub_epic, epic_name, output_dir):
    """Process a sub-epic and generate test file."""
    # Only process lowest-level sub_epics (those with test_file field)
    if 'test_file' not in sub_epic:
        return None
    
    test_file_name = sub_epic.get('test_file')
    if not test_file_name:
        return None
    
    # Extract stories
    stories = extract_stories_from_sub_epic(sub_epic)
    if not stories:
        return None
    
    # Generate test file content
    content = create_test_file_content(sub_epic, stories, epic_name)
    
    # Write test file
    test_file_path = output_dir / test_file_name
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(test_file_path)


class StoryTestsSynchronizer:
    """Synchronizer for rendering pytest test files from story graph JSON."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render pytest test files from story graph JSON.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path to output directory for test files
            renderer_command: Optional command variant (unused for now)
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with output_path, summary, and created files
        """
        input_path = Path(input_path)
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load story graph
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process all sub-epics
        created_files = []
        updated_files = []
        
        def process_recursive(epic, epic_name):
            """Recursively process sub-epics."""
            for sub_epic in epic.get('sub_epics', []):
                # Check if this is a lowest-level sub_epic (has test_file field)
                if 'test_file' in sub_epic:
                    result = process_sub_epic_for_tests(sub_epic, epic_name, output_dir)
                    if result:
                        if Path(result).exists():
                            updated_files.append(result)
                        else:
                            created_files.append(result)
                # Recursively process nested sub-epics
                if sub_epic.get('sub_epics'):
                    process_recursive(sub_epic, epic_name)
        
        # Process each epic
        for epic in data.get('epics', []):
            epic_name = epic.get('name', '')
            process_recursive(epic, epic_name)
        
        return {
            'output_path': str(output_dir),
            'summary': {
                'total_files': len(created_files) + len(updated_files),
                'created_files': len(created_files),
                'updated_files': len(updated_files)
            },
            'created_files': created_files,
            'updated_files': updated_files
        }

