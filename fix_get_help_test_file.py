"""Fix Get Help SubEpic to point to test file instead of folder"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

# Find Get Help SubEpic
get_help = [se for se in invoke_bot['sub_epics'] if se['name'] == 'Get Help'][0]

print('Get Help SubEpic:')
print(f'  Current test_file: {get_help.get("test_file")}')
print(f'  Stories: {len(get_help.get("stories", []))}')

# Change from folder to file
get_help['test_file'] = 'invoke_bot/get_help/test_get_help_using_cli.py'

print(f'  New test_file: {get_help.get("test_file")}')

# Write back
with open('docs/stories/story-graph.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('\n[OK] Updated Get Help SubEpic test_file')
