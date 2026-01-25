"""Show the SubEpic hierarchy to understand nested structure"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

print('SubEpic Hierarchy:\n')
print('='*120)

for sub_epic in invoke_bot['sub_epics']:
    se_name = sub_epic['name']
    se_test_file = sub_epic.get('test_file', 'N/A')
    
    # Check if this SubEpic has nested sub_epics
    nested_sub_epics = sub_epic.get('sub_epics', [])
    direct_stories = sub_epic.get('stories', [])
    
    print(f'\n{se_name}')
    print(f'  test_file: {se_test_file}')
    print(f'  Direct stories: {len(direct_stories)}')
    print(f'  Nested SubEpics: {len(nested_sub_epics)}')
    
    if nested_sub_epics:
        print(f'\n  Nested SubEpics:')
        for nested in nested_sub_epics:
            nested_name = nested['name']
            nested_test_file = nested.get('test_file', 'N/A')
            nested_stories = len(nested.get('stories', []))
            print(f'    - {nested_name}')
            print(f'      test_file: {nested_test_file}')
            print(f'      Stories: {nested_stories}')
    
    if direct_stories:
        print(f'\n  Direct Stories:')
        for story in direct_stories[:3]:  # Show first 3
            print(f'    - {story["name"]}')
            print(f'      test_class: {story.get("test_class", "N/A")}')
    
    print('-'*120)
