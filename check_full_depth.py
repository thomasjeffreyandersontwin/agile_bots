import json

def show_subepic_tree(se, level=0):
    indent = "  " * level
    name = se['name']
    test_file = se.get('test_file', 'N/A')
    stories = len(se.get('stories', []))
    nested = se.get('sub_epics', [])
    
    print(f'{indent}- {name}')
    print(f'{indent}  test_file: {test_file}')
    print(f'{indent}  stories: {stories}, nested SubEpics: {len(nested)}')
    
    for n in nested:
        show_subepic_tree(n, level + 1)

data = json.load(open('docs/stories/story-graph.json'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]
edit_map = [se for se in invoke_bot['sub_epics'] if se['name'] == 'Edit Story Map'][0]

print('Edit Story Map Full Tree:\n')
show_subepic_tree(edit_map)
