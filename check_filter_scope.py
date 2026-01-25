import json
data = json.load(open('docs/stories/story-graph.json'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]
edit_map = [se for se in invoke_bot['sub_epics'] if se['name'] == 'Edit Story Map'][0]
filter_scope = [n for n in edit_map['sub_epics'] if n['name'] == 'Filter Scope'][0]

print(f'Filter Scope has {len(filter_scope.get("sub_epics", []))} nested SubEpics:\n')
for nested in filter_scope.get('sub_epics', []):
    print(f'  - {nested["name"]} ({len(nested.get("stories", []))} stories)')
