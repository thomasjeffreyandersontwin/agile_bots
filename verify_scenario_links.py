"""Verify scenario test_method links work correctly"""
import json
from pathlib import Path

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

issues = []
good = []

def check_scenario_links(se, level=0):
    """Recursively check scenario test links"""
    se_name = se['name']
    se_test_file = se.get('test_file')
    
    for story in se.get('stories', []):
        story_name = story['name']
        story_test_file = story.get('test_file')  # Stories should NOT have this
        
        # Determine which test_file to use
        parent_test_file = story_test_file if story_test_file else se_test_file
        
        for scenario in story.get('scenarios', []):
            scenario_name = scenario.get('name', 'Unnamed')
            test_method = scenario.get('test_method')
            
            if test_method:
                # Scenario needs parent's test_file to build link
                if not parent_test_file:
                    issues.append({
                        'type': 'NO_PARENT_FILE',
                        'story': story_name[:40],
                        'scenario': scenario_name[:30],
                        'test_method': test_method,
                        'subepic': se_name
                    })
                elif parent_test_file.endswith('/'):
                    # Parent points to folder, not file
                    issues.append({
                        'type': 'PARENT_IS_FOLDER',
                        'story': story_name[:40],
                        'scenario': scenario_name[:30],
                        'test_method': test_method,
                        'parent_file': parent_test_file,
                        'subepic': se_name
                    })
                else:
                    # Check if test file exists
                    test_path = Path('test') / parent_test_file
                    if test_path.exists():
                        good.append({
                            'story': story_name,
                            'scenario': scenario_name,
                            'test_method': test_method,
                            'test_file': parent_test_file
                        })
                    else:
                        issues.append({
                            'type': 'FILE_NOT_FOUND',
                            'story': story_name[:40],
                            'scenario': scenario_name[:30],
                            'test_method': test_method,
                            'test_file': parent_test_file
                        })
    
    # Recursively check nested SubEpics
    for nested in se.get('sub_epics', []):
        check_scenario_links(nested, level + 1)

for sub_epic in invoke_bot['sub_epics']:
    check_scenario_links(sub_epic)
    for nested in sub_epic.get('sub_epics', []):
        check_scenario_links(nested, 1)

print('='*100)
print('SCENARIO TEST_METHOD LINK VERIFICATION')
print('='*100)

print(f'\n[OK] {len(good)} scenarios with valid test links')
if good:
    for item in good[:3]:
        print(f'  Story: {item["story"][:35]:35} Scenario: {item["scenario"][:25]:25}')
        print(f'    -> {item["test_file"]} :: {item["test_method"][:50]}')
    if len(good) > 3:
        print(f'  ... and {len(good) - 3} more')

if issues:
    print(f'\n[WARN] {len(issues)} scenarios with potential issues:\n')
    
    no_parent = [i for i in issues if i['type'] == 'NO_PARENT_FILE']
    folder_parent = [i for i in issues if i['type'] == 'PARENT_IS_FOLDER']
    not_found = [i for i in issues if i['type'] == 'FILE_NOT_FOUND']
    
    if no_parent:
        print(f'  NO_PARENT_FILE: {len(no_parent)} scenarios')
        for i in no_parent[:3]:
            print(f'    SubEpic: {i["subepic"]} / Story: {i["story"]}')
            print(f'      Scenario: {i["scenario"]} -> {i["test_method"][:50]}')
        if len(no_parent) > 3:
            print(f'    ... and {len(no_parent) - 3} more')
    
    if folder_parent:
        print(f'\n  PARENT_IS_FOLDER: {len(folder_parent)} scenarios (parent points to folder, not file)')
        for i in folder_parent[:3]:
            print(f'    SubEpic: {i["subepic"]} / Story: {i["story"]}')
            print(f'      Parent: {i["parent_file"]}')
            print(f'      Scenario: {i["scenario"]} -> {i["test_method"][:50]}')
        if len(folder_parent) > 3:
            print(f'    ... and {len(folder_parent) - 3} more')
    
    if not_found:
        print(f'\n  FILE_NOT_FOUND: {len(not_found)} scenarios (test file doesn\'t exist yet)')
        for i in not_found[:3]:
            print(f'    Story: {i["story"]} / Scenario: {i["scenario"]}')
            print(f'      File: {i["test_file"]} -> {i["test_method"][:50]}')
        if len(not_found) > 3:
            print(f'    ... and {len(not_found) - 3} more')

print('='*100)
