"""
Story Scenarios Synchronizer

Renders story markdown files from story graph JSON.
Follows the same pattern as DrawIOSynchronizer.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union
import json
import os
import re
import sys

# Import utils from agile_bots.src
from src.utils import build_test_file_link, build_test_class_link, build_test_method_link


def create_scenario_anchor(scenario_name: str) -> str:
    """Create a markdown anchor ID from scenario name."""
    # Normalize for markdown anchor: lowercase, replace spaces/special chars with hyphens
    anchor = scenario_name.lower()
    # Replace spaces and common special characters with hyphens
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[-\s]+', '-', anchor)
    # Remove leading/trailing hyphens
    anchor = anchor.strip('-')
    return f"scenario-{anchor}"


def format_acceptance_criteria(ac_list):
    """Format acceptance criteria list into markdown"""
    if not ac_list:
        return ""
    
    formatted = []
    for ac in ac_list:
        # Handle both formats: multi-line (WHEN/THEN/AND on separate lines) and single-line (WHEN...THEN...AND in one string)
        parts = ac.split('\n')
        ac_lines = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Check if this is a single-line format with WHEN...THEN...AND all together
            if part.startswith('WHEN') and ' THEN ' in part:
                # Single-line format: "WHEN ... THEN ... AND ..."
                when_then_parts = part.split(' THEN ', 1)
                when_part = when_then_parts[0][4:].strip()  # Remove "WHEN"
                then_and_part = when_then_parts[1] if len(when_then_parts) > 1 else ""
                
                if ac_lines:  # Close previous AC if exists
                    formatted.append('\n'.join(ac_lines))
                    ac_lines = []
                
                ac_lines.append(f"- **When** {when_part}")
                
                # Split THEN and AND clauses
                if ' AND ' in then_and_part:
                    then_parts = then_and_part.split(' AND ')
                    ac_lines.append(f"  **then** {then_parts[0].strip()}")
                    for and_part in then_parts[1:]:
                        ac_lines.append(f"  **and** {and_part.strip()}")
                elif then_and_part:
                    ac_lines.append(f"  **then** {then_and_part.strip()}")
            elif part.startswith('WHEN'):
                if ac_lines:  # Close previous AC if exists
                    formatted.append('\n'.join(ac_lines))
                    ac_lines = []
                ac_lines.append(f"- **When** {part[4:].strip()}")
            elif part.startswith('THEN'):
                # Check if there's an AND clause in the same line
                then_part = part[4:].strip()
                if ' AND ' in then_part:
                    then_parts = then_part.split(' AND ')
                    ac_lines.append(f"  **then** {then_parts[0].strip()}")
                    for and_part in then_parts[1:]:
                        ac_lines.append(f"  **and** {and_part.strip()}")
                else:
                    ac_lines.append(f"  **then** {then_part}")
            elif part.startswith('AND'):
                ac_lines.append(f"  **and** {part[3:].strip()}")
        if ac_lines:
            formatted.append('\n'.join(ac_lines))
    return '\n\n'.join(formatted)


def get_common_background(scenarios_list):
    """Extract common background steps shared across all scenarios"""
    if not scenarios_list:
        return None
    
    # Get backgrounds from all scenarios
    backgrounds = [s.get('background', []) for s in scenarios_list if s.get('background')]
    if not backgrounds:
        return None
    
    # Find common background (all scenarios have same background)
    common = backgrounds[0]
    for bg in backgrounds[1:]:
        if bg != common:
            # Not all the same, return None
            return None
    
    return common


def format_scenarios(scenarios_list, common_background=None, story_test_file='', workspace_directory=None, story_file_path=None):
    """Format scenarios list into markdown"""
    if not scenarios_list:
        return ""
    
    formatted = []
    for scenario in scenarios_list:
        name = scenario.get('name', 'Unnamed Scenario')
        scenario_type = scenario.get('type', 'happy_path')
        background = scenario.get('background', [])
        steps = scenario.get('steps', [])
        
        # Format test method link for scenario level using the same helper as CLI scope display
        scenario_test_link = ""
        test_method = scenario.get('test_method', '')
        
        if story_test_file and test_method and workspace_directory:
            # Use the helper function to build the link (same as CLI scope display)
            scenario_test_link = build_test_method_link(story_test_file, test_method, workspace_directory, story_file_path)

        # Normalize steps into multi-line text:
        # - If provided as a list, join with newlines.
        # - If provided as a string that includes literal "\n", convert to real newlines.
        if isinstance(steps, list):
            steps_list = steps
        else:
            steps_list = str(steps).replace("\\n", "\n").split("\n")
        
        # Scenario Steps should NOT include Background steps - Background is automatically applied
        # Scenario Steps should start with scenario-specific Given steps (if any), then When/Then
        # Only include scenario-specific background if there's no common background
        step_lines = []
        
        # Check if steps already include background (from story-graph.json)
        # If common_background exists, Background is at story level and should NOT be in scenario Steps
        # Only include scenario-specific background if no common background exists
        if not common_background and background:
            # No common background, so include scenario-specific background in steps
            for bg_step in background:
                step_lines.append(bg_step)
        
        # Add scenario-specific steps (these should start with scenario-specific Given if needed)
        for step in steps_list:
            if step.strip():
                step_lines.append(step.strip())
        
        steps_text = "\n".join(step_lines)

        examples_block = ""
        examples_data = scenario.get('examples')
        
        # Handle two formats: list of dicts OR dict with columns+rows (template format)
        if isinstance(examples_data, dict) and 'columns' in examples_data and 'rows' in examples_data:
            # Template format: {"columns": [...], "rows": [[...]]}
            columns = examples_data['columns']
            rows = examples_data['rows']
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"
            table_rows = []
            for row in rows:
                table_rows.append("| " + " | ".join(str(cell).strip() for cell in row) + " |")
            table = "\n".join([header, separator] + table_rows)
            examples_block = f"\n**Examples:**\n{table}\n"
        elif isinstance(examples_data, list) and examples_data:
            if all(isinstance(row, dict) for row in examples_data):
                # Build a single table using all keys across rows (preserve first-seen order)
                columns = []
                for row in examples_data:
                    for key in row.keys():
                        if key not in columns:
                            columns.append(key)
                header = "| " + " | ".join(columns) + " |"
                separator = "| " + " | ".join(["---"] * len(columns)) + " |"
                rows = []
                for row in examples_data:
                    rows.append("| " + " | ".join(str(row.get(col, "")).strip() for col in columns) + " |")
                table = "\n".join([header, separator] + rows)
                examples_block = f"\n**Examples:**\n{table}\n"
            elif all(isinstance(row, str) for row in examples_data):
                rows = "\n".join([f"| {row} |  |" for row in examples_data])
                examples_block = (
                    "\n**Examples:**\n"
                    "| variable | value |\n"
                    "| --- | --- |\n"
                    f"{rows}\n"
                )

        # Create anchor ID for scenario (normalized to match markdown auto-generated anchors)
        scenario_anchor = create_scenario_anchor(name)
        
        # Format test link separately (if exists) - keep as separate link after scenario type
        test_link_display = f" {scenario_test_link}" if scenario_test_link else ""
        
        # VS Code markdown preview generates anchors from header text.
        # To ensure links work reliably, we:
        # 1. Place explicit anchor tag right before header (for external links from panel)
        # 2. Use plain text in header so VS Code generates compatible anchor
        # 3. Make the scenario name itself a clickable link that points to the anchor
        # The header format: "### Scenario: [Name](#anchor) (type)" 
        # VS Code will generate anchor from the rendered text "Scenario: Name (type)"
        # But our explicit anchor tag ensures the link target exists regardless.
        scenario_name_link = f"[{name}](#{scenario_anchor})"
        formatted.append(
            f"<a id=\"{scenario_anchor}\"></a>\n### Scenario: {scenario_name_link} ({scenario_type}){test_link_display}\n\n**Steps:**\n```gherkin\n{steps_text}\n```\n{examples_block}"
        )
    
    return "\n\n".join(formatted)


def build_folder_path_from_graph(epic_name, sub_epic_name, story_graph_data):
    """
    Build folder path dynamically from story graph structure.
    Traverses the graph to find the actual epic and sub_epic names.
    Uses emoji monikers: ðŸŽ¯ for Epic, âš™ï¸ for Sub-Epic.
    Handles nested sub-epics by building full folder path.
    """
    # Find the epic in the graph
    for epic in story_graph_data.get('epics', []):
        if epic['name'] == epic_name:
            epic_folder = f"ðŸŽ¯ {epic_name}"  # Use emoji moniker
            
            # If sub_epic_name matches the epic itself, it's a top-level epic
            if sub_epic_name == epic_name:
                return epic_folder, epic_name
            
            # Handle nested sub-epics (e.g., "Run Interactive REPL/Display Bot State Using CLI")
            if '/' in sub_epic_name:
                parts = sub_epic_name.split('/')
                # Build path with gear emoji for each part
                formatted_parts = [f"âš™ï¸ {part.strip()}" for part in parts]
                # Join with Path separator for folder structure
                sub_epic_path = Path(*formatted_parts)
                return epic_folder, str(sub_epic_path)
            
            # Otherwise, find the sub_epic in the epic's sub_epics
            def find_sub_epic(sub_epics, target_name):
                for sub_epic in sub_epics:
                    if sub_epic['name'] == target_name:
                        return f"âš™ï¸ {target_name}"  # Use emoji moniker for sub-epic
                    # Recursively check nested sub_epics
                    if 'sub_epics' in sub_epic:
                        result = find_sub_epic(sub_epic['sub_epics'], target_name)
                        if result:
                            return result
                return None
            
            sub_epic_folder = find_sub_epic(epic.get('sub_epics', []), sub_epic_name)
            if sub_epic_folder:
                return epic_folder, sub_epic_folder
            
            # If not found in sub_epics, use the provided name with emoji moniker
            return epic_folder, f"âš™ï¸ {sub_epic_name}" if sub_epic_name != epic_name else epic_name
    
    # Fallback: use names directly with emoji monikers
    fallback_epic = f"ðŸŽ¯ {epic_name}"
    fallback_sub_epic = f"âš™ï¸ {sub_epic_name}" if sub_epic_name != epic_name else epic_name
    return fallback_epic, fallback_sub_epic


def create_story_content(story, epic_name, sub_epic_name, workspace_directory, story_file_path=None):
    """Create markdown content for a story. sub_epic_name is the sub-epic name."""
    """Create markdown content for a story"""
    story_name = story['name']
    users = story.get('users', [])
    user_str = ', '.join(users) if users else 'System'
    story_type = story.get('story_type', 'user')
    sequential_order = story.get('sequential_order', 1)
    
    # Format test class link for story level using the same helper as CLI scope display
    test_file_link = ""
    test_file = story.get('test_file', '')
    test_class = story.get('test_class', '')
    
    if test_file and test_class:
        # Use the helper function to build the link (same as CLI scope display)
        test_file_link = build_test_class_link(test_file, test_class, workspace_directory, story_file_path)
    elif test_file:
        # If we only have test_file (no test_class), just link to the file
        test_file_link = build_test_file_link(test_file, workspace_directory, story_file_path)
    
    ac_list = story.get('acceptance_criteria', [])
    ac_formatted = format_acceptance_criteria(ac_list)
    
    scenarios_list = story.get('scenarios', [])
    scenario_outlines_list = story.get('scenario_outlines', [])
    
    # Combine scenarios and scenario_outlines for processing
    all_scenarios = scenarios_list + scenario_outlines_list
    
    # Get common background from all scenarios
    common_background = get_common_background(all_scenarios)
    
    # Format scenarios (pass common_background, test_file, workspace_directory, and story_file_path so scenarios include test links)
    scenarios_formatted = format_scenarios(all_scenarios, common_background, test_file, workspace_directory, story_file_path)
    
    # Default description if not provided
    description = story.get('description', f'{story_name} functionality for the mob minion system.')
    
    # Default acceptance criteria if not provided
    if not ac_formatted:
        ac_formatted = "- **When** action executes, **then** action completes successfully"
    
    # Default scenario if not provided
    if not scenarios_formatted:
        scenarios_formatted = f"""### Scenario: {story_name} (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```"""
    
    # Format background section
    background_section = ""
    if common_background:
        bg_formatted = "\n".join(common_background)
        background_section = f"""## Background

**Common setup steps shared across all scenarios:**

```gherkin
{bg_formatted}
```

"""
    
    # Build clickable path with proper relative links for each level
    path_parts = [f"[ðŸŽ¯ {epic_name}](../..)"]
    
    if sub_epic_name != epic_name:
        # Handle nested sub-epics separated by '/'
        if '/' in sub_epic_name:
            sub_parts = [part.strip() for part in sub_epic_name.split('/')]
            # First sub-epic is 1 level up (..)
            path_parts.append(f"[âš™ï¸ {sub_parts[0]}](..)")
            # Additional nested sub-epics - last one is current folder (.)
            for i, part in enumerate(sub_parts[1:], start=1):
                if i == len(sub_parts) - 1:
                    path_parts.append(f"[âš™ï¸ {part}](.)")
                else:
                    # For middle levels, calculate relative path
                    levels_up = len(sub_parts) - i - 1
                    rel_path = '/'.join(['..'] * levels_up) if levels_up > 0 else '.'
                    path_parts.append(f"[âš™ï¸ {part}]({rel_path})")
        else:
            # Single sub-epic - story is inside it, so current folder (.)
            path_parts.append(f"[âš™ï¸ {sub_epic_name}](.)")
    
    path_line = ' / '.join(path_parts)
    
    content = f"""# ðŸ“ {story_name}

**Navigation:** [ðŸ“‹ Story Map](../../../../story-map.drawio){test_file_link}

**User:** {user_str}
**Path:** {path_line}  
**Sequential Order:** {sequential_order}
**Story Type:** {story_type}

## Story Description

{description}

## Acceptance Criteria

### Behavioral Acceptance Criteria

{ac_formatted}

{background_section}## Scenarios

{scenarios_formatted}
"""
    return content


def extract_stories_from_graph(epic, epic_path="", sub_epic_path="", parent_is_epic=True):
    """
    Extract all stories from story graph recursively.
    Dynamically builds folder structure from the graph itself.
    Handles nested sub-epics (sub-subs) by building up the full path.
    """
    stories = []
    current_epic_path = epic['name'] if not epic_path else f"{epic_path}/{epic['name']}"
    current_is_epic = parent_is_epic and not sub_epic_path
    
    # Get stories from story_groups
    # Exclude Human/AI Chat/AI Agent stories per render instructions
    for group in epic.get('story_groups', []):
        for story in group.get('stories', []):
            # Filter out Human, AI Chat, and AI Agent stories
            users = story.get('users', [])
            if any(u in ['Human', 'AI Chat', 'AI Agent'] for u in users):
                continue  # Skip this story
            
            story['epic_path'] = current_epic_path
            story['sub_epic_path'] = sub_epic_path if sub_epic_path else epic['name']
            story['epic_name'] = current_epic_path.split('/')[0] if '/' in current_epic_path else current_epic_path
            story['sub_epic_name'] = sub_epic_path if sub_epic_path else epic['name']
            story['is_epic'] = current_is_epic
            story['is_sub_epic'] = not current_is_epic
            stories.append(story)
    
    # Get stories from sub_epics (recursively handle nested sub-epics)
    for sub_epic in epic.get('sub_epics', []):
        # Build up the full sub-epic path for nested sub-epics
        # If we're already in a sub-epic, append to the path; otherwise start new path
        if sub_epic_path:
            # We're in a sub-epic already, so this is a nested sub-epic (sub-sub)
            # Keep the epic_path as is (just the epic name), and build sub_epic_path
            current_sub_epic_path = f"{sub_epic_path}/{sub_epic['name']}"
            stories.extend(extract_stories_from_graph(sub_epic, epic_path, current_sub_epic_path, parent_is_epic=False))
        else:
            # This is the first level sub-epic under the epic
            current_sub_epic_path = sub_epic['name']
            stories.extend(extract_stories_from_graph(sub_epic, current_epic_path, current_sub_epic_path, parent_is_epic=False))
    
    return stories


class StoryScenariosSynchronizer:
    """Synchronizer for rendering story markdown files from story graph JSON."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render story markdown files from story graph JSON.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path to output directory for story files
            renderer_command: Optional command variant (unused for now)
            **kwargs: Additional arguments
        
        Returns:
            Dictionary with output_path, summary, and created files
        """
        input_path = Path(input_path)
        output_dir = Path(output_path)
        base_dir = output_dir  # Output path already includes the target directory
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Load story graph
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Track existing story files and their paths
        existing_story_files = {}
        if base_dir.exists():
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.md') and file != 'README.md':
                        file_path = Path(root) / file
                        # Extract story name from filename
                        name = file.replace('.md', '')
                        if name.startswith('[Story] '):
                            name = name[8:]  # Remove '[Story] '
                        elif name.startswith('ðŸ“ '):
                            name = name[2:]  # Remove 'ðŸ“ '
                        existing_story_files[name] = file_path
        
        # Extract all stories from graph
        all_stories = []
        for epic in data['epics']:
            all_stories.extend(extract_stories_from_graph(epic))
        
        # Build set of ALL story names that should exist (regardless of scope)
        # This is used for cleanup - we need to know ALL valid stories to identify obsolete files
        all_story_names_in_graph = {story['name'] for story in all_stories}
        
        # Create story files and track which files were rendered in correct locations
        created_files = []
        updated_files = []
        deleted_files = []
        rendered_file_paths = set()  # Track all files we rendered in their correct locations
        
        for story in all_stories:
            story_name = story['name']
            # Sanitize story name for use in file path (replace invalid path characters)
            # Forward slashes and backslashes are not valid in filenames on Windows
            sanitized_story_name = story_name.replace('/', '-').replace('\\', '-')
            
            # Build folder path dynamically from story graph structure
            epic_folder, sub_epic_folder = build_folder_path_from_graph(
                story['epic_name'], 
                story.get('sub_epic_name', story['epic_name']),
                data
            )
            
            # Create directory structure using names from the graph
            story_dir = base_dir / epic_folder / sub_epic_folder
            story_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file (use ðŸ“ emoji prefix) with sanitized name
            story_file = story_dir / f"ðŸ“ {sanitized_story_name}.md"
            rendered_file_paths.add(story_file)  # Track this as a valid file location
            
            # Generate content - workspace_directory is 3 levels up from map directory (map -> stories -> docs -> workspace)
            workspace_directory = base_dir.parent.parent.parent
            content = create_story_content(story, story['epic_name'], story.get('sub_epic_name', story['epic_name']), workspace_directory, story_file)
            
            # Check if file exists
            if story_file.exists():
                updated_files.append(str(story_file.relative_to(output_dir)))
            else:
                created_files.append(str(story_file.relative_to(output_dir)))
            
            # Write file
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Delete files that exist but weren't rendered (wrong location or obsolete)
        # This runs regardless of scope - we always clean up files that don't belong
        for story_name, file_path in existing_story_files.items():
            if file_path not in rendered_file_paths:
                try:
                    file_path.unlink()
                    deleted_files.append(str(file_path.relative_to(output_dir)))
                except Exception as e:
                    # Log error but continue
                    print(f"Warning: Could not delete obsolete story file {file_path}: {e}")
        
        return {
            'output_path': str(output_dir),
            'summary': {
                'total_stories': len(all_stories),
                'created_files': len(created_files),
                'updated_files': len(updated_files),
                'deleted_files': len(deleted_files)
            },
            'created_files': created_files,
            'updated_files': updated_files,
            'deleted_files': deleted_files
        }

