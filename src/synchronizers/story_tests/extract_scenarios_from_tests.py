"""
Extract scenarios from test method docstrings and update story graph.
"""
import json
import ast
import re
from pathlib import Path
from collections import defaultdict

def normalize_name(name):
    """Normalize names for matching."""
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

def extract_scenario_from_docstring(docstring):
    """Extract scenario name and steps from docstring."""
    if not docstring:
        return None, []
    
    lines = docstring.strip().split('\n')
    scenario_name = None
    steps = []
    
    # Look for SCENARIO: line
    for line in lines:
        line = line.strip()
        if line.startswith('SCENARIO:'):
            scenario_name = line.replace('SCENARIO:', '').strip()
        elif line.startswith('GIVEN:') or line.startswith('Given:'):
            steps.append(f"Given {line.replace('GIVEN:', '').replace('Given:', '').strip()}")
        elif line.startswith('AND:') or line.startswith('And:'):
            steps.append(f"And {line.replace('AND:', '').replace('And:', '').strip()}")
        elif line.startswith('WHEN:') or line.startswith('When:'):
            steps.append(f"When {line.replace('WHEN:', '').replace('When:', '').strip()}")
        elif line.startswith('THEN:') or line.startswith('Then:'):
            steps.append(f"Then {line.replace('THEN:', '').replace('Then:', '').strip()}")
    
    return scenario_name, steps

def generate_scenario_name_from_method(method_name):
    """Generate a readable scenario name from test method name."""
    # Remove 'test_' prefix
    name = method_name.replace('test_', '')
    # Split on underscores and capitalize each word
    words = name.split('_')
    return ' '.join(word.capitalize() for word in words)

def parse_test_file(file_path):
    """Parse a test file and extract classes and methods with docstrings."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': [],
                    'file': file_path.name
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        method_info = {
                            'name': item.name,
                            'docstring': ast.get_docstring(item) or '',
                            'scenario_name': None,
                            'steps': []
                        }
                        
                        # Extract scenario from docstring
                        scenario_name, steps = extract_scenario_from_docstring(method_info['docstring'])
                        if scenario_name:
                            method_info['scenario_name'] = scenario_name
                        else:
                            # Generate from method name
                            method_info['scenario_name'] = generate_scenario_name_from_method(item.name)
                        
                        method_info['steps'] = steps
                        class_info['methods'].append(method_info)
                
                if class_info['methods']:
                    classes.append(class_info)
        
        return classes
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def match_test_to_story(test_name, story_names):
    """Match test class name to story name."""
    test_normalized = normalize_name(test_name.replace('Test', ''))
    
    best_match = None
    best_score = 0
    
    for story in story_names:
        story_normalized = normalize_name(story)
        test_words = set(test_normalized.split())
        story_words = set(story_normalized.split())
        
        if test_words and story_words:
            overlap = len(test_words & story_words)
            if overlap > best_score:
                best_score = overlap
                best_match = story
    
    return best_match

def find_story_in_graph(story_name, story_graph):
    """Find a story in the story graph by name."""
    for epic in story_graph.get('epics', []):
        # Check stories directly under epic
        for story_group in epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                if story.get('name') == story_name:
                    return story
        
        # Check stories in sub-epics
        for sub_epic in epic.get('sub_epics', []):
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    if story.get('name') == story_name:
                        return story
    
    return None

def collect_all_stories(story_graph):
    """Collect all story names from the story graph."""
    stories = []
    
    def collect_from_node(node):
        if 'story_groups' in node:
            for group in node['story_groups']:
                for story in group.get('stories', []):
                    stories.append(story['name'])
        if 'sub_epics' in node:
            for sub_epic in node['sub_epics']:
                collect_from_node(sub_epic)
    
    for epic in story_graph.get('epics', []):
        collect_from_node(epic)
    
    return stories

def update_story_with_scenarios(story, test_methods):
    """Update a story with scenarios extracted from test methods."""
    if 'scenarios' not in story:
        story['scenarios'] = []
    
    # Create a map of existing scenarios by test_method
    existing_scenarios = {s.get('test_method'): s for s in story['scenarios']}
    
    # Add or update scenarios from test methods
    for method_info in test_methods:
        test_method = method_info['name']
        scenario_name = method_info['scenario_name']
        steps = method_info['steps']
        
        if test_method in existing_scenarios:
            # Update existing scenario
            scenario = existing_scenarios[test_method]
            if scenario_name and not scenario.get('name'):
                scenario['name'] = scenario_name
            if steps and not scenario.get('steps'):
                scenario['steps'] = steps
        else:
            # Add new scenario
            scenario = {
                'name': scenario_name,
                'type': 'happy_path',  # Default, could be inferred from method name
                'test_method': test_method,
                'background': [],
                'steps': steps if steps else []
            }
            story['scenarios'].append(scenario)

def main():
    story_graph_path = Path('agile_bots/bots/base_bot/docs/stories/story-graph.json')
    test_dir = Path('agile_bots/bots/base_bot/test')
    
    # Load story graph
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Collect all story names
    all_stories = collect_all_stories(story_graph)
    
    # Parse all test files
    test_files = list(test_dir.glob('test_*.py'))
    test_mapping = defaultdict(lambda: defaultdict(list))  # story_name -> file -> [methods]
    
    for test_file in test_files:
        if test_file.name in ['test_helpers.py', 'test_utils.py', 'conftest.py']:
            continue
        
        classes = parse_test_file(test_file)
        
        for test_class in classes:
            # Try to match class to story
            matched_story = match_test_to_story(test_class['name'], all_stories)
            
            if matched_story:
                # Add all methods to this story
                for method_info in test_class['methods']:
                    test_mapping[matched_story][test_file.name].append(method_info)
            else:
                # Try to match by file name
                file_base = test_file.stem.replace('test_', '')
                file_base_normalized = normalize_name(file_base)
                
                for story_name in all_stories:
                    story_normalized = normalize_name(story_name)
                    if (file_base_normalized in story_normalized or 
                        story_normalized in file_base_normalized):
                        for method_info in test_class['methods']:
                            test_mapping[story_name][test_file.name].append(method_info)
                        break
    
    # Update story graph with scenarios
    for story_name, file_methods in test_mapping.items():
        story = find_story_in_graph(story_name, story_graph)
        if story:
            # Collect all methods for this story
            all_methods = []
            for methods in file_methods.values():
                all_methods.extend(methods)
            
            update_story_with_scenarios(story, all_methods)
    
    # Save updated story graph
    with open(story_graph_path, 'w', encoding='utf-8') as f:
        json.dump(story_graph, f, indent=2, ensure_ascii=False)
    
    print(f"Updated story graph with scenarios from test files")
    print(f"Updated {len(test_mapping)} stories")

if __name__ == '__main__':
    main()
