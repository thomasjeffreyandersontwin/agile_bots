"""Verify all test_file paths in story-graph.json point to actual files"""
import json
from pathlib import Path
import ast

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

errors = []
warnings = []
successes = []

def check_test_class_exists(test_file_path, test_class):
    """Check if test_class exists in the test file"""
    if not test_file_path.exists():
        return False, "File does not exist"
    
    try:
        content = test_file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == test_class:
                return True, "Found"
        
        return False, f"Class '{test_class}' not found in file"
    except Exception as e:
        return False, f"Error parsing file: {e}"

def verify_subepic(se, level=0):
    """Recursively verify SubEpic and all nested SubEpics"""
    indent = "  " * level
    se_name = se['name']
    test_file = se.get('test_file')
    
    if test_file:
        # Construct full path
        test_path = Path('test') / test_file
        
        # Check if it's a file or directory
        if test_path.is_file():
            successes.append(f'{indent}[OK] {se_name[:50]:50} -> {test_file}')
        elif test_path.is_dir():
            successes.append(f'{indent}[OK] {se_name[:50]:50} -> {test_file} (folder)')
        else:
            errors.append(f'{indent}[ERROR] {se_name[:50]:50} -> {test_file} NOT FOUND')
    
    # Verify stories
    for story in se.get('stories', []):
        story_name = story['name']
        test_class = story.get('test_class')
        
        if test_class:
            # Stories should inherit test_file from their parent SubEpic
            if test_file:
                test_path = Path('test') / test_file
                
                # If test_file is a directory, we can't verify the class
                if test_path.is_dir():
                    warnings.append(f'{indent}  [WARN] Story "{story_name[:40]}" has test_class but parent points to folder')
                elif test_path.is_file():
                    exists, msg = check_test_class_exists(test_path, test_class)
                    if exists:
                        successes.append(f'{indent}  [OK] Story "{story_name[:40]}" -> {test_class}')
                    else:
                        errors.append(f'{indent}  [ERROR] Story "{story_name[:40]}" -> {test_class}: {msg}')
            else:
                warnings.append(f'{indent}  [WARN] Story "{story_name[:40]}" has test_class but no parent test_file')
    
    # Recursively verify nested SubEpics
    for nested in se.get('sub_epics', []):
        verify_subepic(nested, level + 1)

print('='*100)
print('VERIFYING TEST LINKS IN STORY GRAPH')
print('='*100)

for sub_epic in invoke_bot['sub_epics']:
    verify_subepic(sub_epic)
    for nested in sub_epic.get('sub_epics', []):
        verify_subepic(nested, 1)

print('\n' + '='*100)
print('VERIFICATION SUMMARY')
print('='*100)

if successes:
    print(f'\n[OK] {len(successes)} SUCCESSFUL LINKS')
    for s in successes[:10]:  # Show first 10
        print(s)
    if len(successes) > 10:
        print(f'  ... and {len(successes) - 10} more')

if warnings:
    print(f'\n[WARN] {len(warnings)} WARNINGS')
    for w in warnings[:10]:
        print(w)
    if len(warnings) > 10:
        print(f'  ... and {len(warnings) - 10} more')

if errors:
    print(f'\n[ERROR] {len(errors)} ERRORS')
    for e in errors:
        print(e)
else:
    print('\n[OK] NO ERRORS FOUND!')

print('='*100)
