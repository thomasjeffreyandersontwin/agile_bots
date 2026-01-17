"""
Extract scenario steps from test method docstrings and populate story graph JSON.
"""
import json
import ast
import re
from pathlib import Path
from collections import defaultdict

def normalize_name(name):
    """Normalize names for matching."""
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

def extract_steps_from_docstring(docstring):
    """Extract Gherkin steps from docstring."""
    if not docstring:
        return []
    
    steps = []
    lines = docstring.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for step keywords (case insensitive) - more flexible pattern
        step_match = re.match(r'^\s*(SCENARIO|GIVEN|WHEN|THEN|AND|BUT)\s*:\s*(.+)', line, re.IGNORECASE)
        if step_match:
            keyword = step_match.group(1).upper()
            step_text = step_match.group(2).strip()
            
            if keyword == 'SCENARIO':
                # Scenario name, skip
                continue
            else:
                # Normalize keyword (GIVEN/WHEN/THEN/AND/BUT)
                if keyword == 'GIVEN':
                    steps.append(f"Given {step_text}")
                elif keyword == 'WHEN':
                    steps.append(f"When {step_text}")
                elif keyword == 'THEN':
                    steps.append(f"Then {step_text}")
                elif keyword in ['AND', 'BUT']:
                    # Use And/But, but capitalize properly
                    steps.append(f"And {step_text}")
            continue
        
        # Look for "Flow:" sections with numbered steps
        if line.startswith('Flow:'):
            continue
        
        # Match numbered steps: "1. Start at initialize_project"
        numbered_match = re.match(r'^\d+\.\s+(.+)', line)
        if numbered_match:
            step_text = numbered_match.group(1).strip()
            
            # Try to infer step type from content
            step_lower = step_text.lower()
            if any(word in step_lower for word in ['start', 'given', 'setup', 'initialize', 'create', 'set', 'prepare']):
                steps.append(f"Given {step_text}")
            elif any(word in step_lower for word in ['when', 'execute', 'call', 'invoke', 'trigger', 'run', 'perform', 'close', 'jump']):
                steps.append(f"When {step_text}")
            elif any(word in step_lower for word in ['then', 'verify', 'assert', 'check', 'confirm', 'should', 'expect', 'transitions']):
                steps.append(f"Then {step_text}")
            else:
                # Default to Given if unclear
                steps.append(f"Given {step_text}")
            continue
    
    return steps

def parse_test_file(file_path):
    """Parse a test file and extract test methods with their docstrings."""
    test_methods = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try AST parsing first
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    docstring = ast.get_docstring(node)
                    steps = extract_steps_from_docstring(docstring) if docstring else []
                    test_methods[node.name] = {
                        'name': node.name,
                        'docstring': docstring,
                        'steps': steps
                    }
        except SyntaxError:
            # Fallback to regex parsing for files with syntax errors
            print(f"  Using regex fallback for {file_path.name} (AST parse failed)")
            # Find test method definitions
            test_pattern = r'def\s+(test_\w+)\s*\([^)]*\):\s*\n\s*"""(.*?)"""'
            matches = re.finditer(test_pattern, content, re.DOTALL | re.MULTILINE)
            for match in matches:
                method_name = match.group(1)
                docstring = match.group(2).strip()
                steps = extract_steps_from_docstring(docstring) if docstring else []
                test_methods[method_name] = {
                    'name': method_name,
                    'docstring': docstring,
                    'steps': steps
                }
        
        return test_methods
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {}

def main():
    story_graph_path = Path('agile_bots/bots/base_bot/docs/stories/story-graph.json')
    test_dir = Path('agile_bots/bots/base_bot/test')
    
    # Load story graph
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Parse all test files
    test_methods_map = {}
    for test_file in test_dir.glob('test_*.py'):
        if test_file.name.endswith('_helpers.py') or test_file.name in ['test_helpers.py', 'test_utils.py', 'conftest.py']:
            continue
        
        methods = parse_test_file(test_file)
        test_methods_map.update(methods)
    
    # Debug: Show what we found
    print(f"\nFound {len(test_methods_map)} test methods")
    print(f"Sample test methods with steps:")
    sample_count = 0
    for method_name, method_info in test_methods_map.items():
        if method_info['steps']:
            print(f"  {method_name}: {len(method_info['steps'])} steps")
            sample_count += 1
            if sample_count >= 5:
                break
    
    # Update scenarios in story graph
    updated_count = 0
    
    def update_scenarios_in_node(node):
        nonlocal updated_count
        
        # Handle stories in story_groups
        if 'story_groups' in node:
            for group in node['story_groups']:
                if 'stories' in group:
                    for story in group['stories']:
                        if 'scenarios' in story:
                            for scenario in story['scenarios']:
                                test_method = scenario.get('test_method')
                                if test_method:
                                    if test_method in test_methods_map:
                                        method_info = test_methods_map[test_method]
                                        if method_info['steps']:
                                            scenario['steps'] = method_info['steps']
                                            updated_count += 1
                                            print(f"[OK] Updated scenario '{scenario['name']}' with {len(method_info['steps'])} steps from {test_method}")
                                    # else:
                                    #     print(f"  ⚠ Test method not found: {test_method}")
        
        # Handle direct stories (for epics without story_groups)
        if 'stories' in node:
            for story in node['stories']:
                if 'scenarios' in story:
                    for scenario in story['scenarios']:
                        test_method = scenario.get('test_method')
                        if test_method:
                            if test_method in test_methods_map:
                                method_info = test_methods_map[test_method]
                                if method_info['steps']:
                                    scenario['steps'] = method_info['steps']
                                    updated_count += 1
                                    print(f"✓ Updated scenario '{scenario['name']}' with {len(method_info['steps'])} steps from {test_method}")
        
        if 'sub_epics' in node:
            for sub_epic in node['sub_epics']:
                update_scenarios_in_node(sub_epic)
    
    # Process all epics
    for epic in story_graph.get('epics', []):
        update_scenarios_in_node(epic)
    
    # Save updated story graph
    if updated_count > 0:
        with open(story_graph_path, 'w', encoding='utf-8') as f:
            json.dump(story_graph, f, indent=2, ensure_ascii=False)
        print(f"\nUpdated {updated_count} scenarios with steps in story graph JSON")
    else:
        print("No scenarios were updated. Check if test methods have docstrings with scenario steps.")

if __name__ == '__main__':
    main()
