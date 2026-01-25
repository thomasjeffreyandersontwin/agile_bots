"""Update Story-level test_file paths to point to actual test files"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

# Map SubEpic names to their primary test files (relative to test/ folder)
SUBEPIC_TO_TEST_FILE = {
    'Initialize Bot': 'invoke_bot/initialize_bot/',
    'Edit Story Map': 'invoke_bot/edit_story_map/',
    'Navigate Behavior Actions': 'invoke_bot/navigate_behavior_actions/',
    'Perform Action': 'invoke_bot/perform_action/',
    'Get Help': 'invoke_bot/get_help/test_get_help_using_cli.py',
}

updates_count = 0

for sub_epic in invoke_bot['sub_epics']:
    se_name = sub_epic['name']
    test_file_path = SUBEPIC_TO_TEST_FILE.get(se_name)
    
    if not test_file_path:
        print(f'[SKIP] No test file mapping for SubEpic: {se_name}')
        continue
    
    for story in sub_epic.get('stories', []):
        # Only update if story has test_class but no test_file
        if story.get('test_class') and not story.get('test_file'):
            story['test_file'] = test_file_path
            updates_count += 1
            print(f'[OK] {story["name"][:60]:60} -> {test_file_path}')

# Write back
with open('docs/stories/story-graph.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\n[DONE] Updated {updates_count} Story test_file paths')
