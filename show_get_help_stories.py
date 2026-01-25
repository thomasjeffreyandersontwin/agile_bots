"""Show Get Help SubEpic stories"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]
get_help = [se for se in invoke_bot['sub_epics'] if se['name'] == 'Get Help'][0]

print('Get Help SubEpic Stories:\n')
print('='*90)
for i, story in enumerate(get_help.get('stories', []), 1):
    print(f'{i}. {story["name"]}')
    print(f'   test_file: {story.get("test_file")}')
    print(f'   test_class: {story.get("test_class")}')
    print(f'   test_method: {story.get("test_method")}')
    print()
print('='*90)
