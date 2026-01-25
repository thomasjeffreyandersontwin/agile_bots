"""Check Story-level test attributes in story-graph.json"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

# Collect all stories from all SubEpics
all_stories = []
for sub_epic in invoke_bot['sub_epics']:
    se_name = sub_epic['name']
    for story in sub_epic.get('stories', []):
        story['_sub_epic'] = se_name  # Track which SubEpic
        all_stories.append(story)

# Find stories with test attributes
stories_with_test = [s for s in all_stories if 'test_file' in s or 'test_class' in s]

print(f'Total stories: {len(all_stories)}')
print(f'Stories with test attributes: {len(stories_with_test)}\n')

print('='*110)
print(f'{"SubEpic":30} {"Story Name":40} {"test_file":40}')
print('='*110)

for story in stories_with_test:
    se = story.get('_sub_epic', 'N/A')[:28]
    name = story['name'][:38]
    test_file = str(story.get('test_file', 'N/A'))[:38]
    test_class = story.get('test_class', '')
    print(f'{se:30} {name:40} {test_file:40}')

print('='*110)

# Check if any stories still have 'test/' prefix
stories_with_test_prefix = [s for s in stories_with_test if str(s.get('test_file', '')).startswith('test/')]
if stories_with_test_prefix:
    print(f'\n[WARN] {len(stories_with_test_prefix)} stories still have test/ prefix!')
