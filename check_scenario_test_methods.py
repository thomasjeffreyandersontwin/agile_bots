"""Check if scenarios have test_method attributes"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

scenarios_with_test = []
scenarios_without_test = []

def check_scenarios(se, level=0):
    """Recursively check scenarios in SubEpic"""
    indent = "  " * level
    
    for story in se.get('stories', []):
        story_name = story['name']
        
        for scenario in story.get('scenarios', []):
            scenario_name = scenario.get('name', 'Unnamed')
            test_method = scenario.get('test_method')
            
            if test_method:
                scenarios_with_test.append({
                    'story': story_name,
                    'scenario': scenario_name,
                    'test_method': test_method
                })
            else:
                scenarios_without_test.append({
                    'story': story_name,
                    'scenario': scenario_name
                })
    
    # Recursively check nested SubEpics
    for nested in se.get('sub_epics', []):
        check_scenarios(nested, level + 1)

for sub_epic in invoke_bot['sub_epics']:
    check_scenarios(sub_epic)
    for nested in sub_epic.get('sub_epics', []):
        check_scenarios(nested, 1)

print('='*100)
print('SCENARIO TEST_METHOD CHECK')
print('='*100)

print(f'\nScenarios WITH test_method: {len(scenarios_with_test)}')
if scenarios_with_test:
    for item in scenarios_with_test[:5]:
        print(f'  Story: {item["story"][:40]:40} Scenario: {item["scenario"][:30]:30} -> {item["test_method"]}')
    if len(scenarios_with_test) > 5:
        print(f'  ... and {len(scenarios_with_test) - 5} more')

print(f'\nScenarios WITHOUT test_method: {len(scenarios_without_test)}')
if scenarios_without_test:
    for item in scenarios_without_test[:10]:
        print(f'  Story: {item["story"][:40]:40} Scenario: {item["scenario"][:30]}')
    if len(scenarios_without_test) > 10:
        print(f'  ... and {len(scenarios_without_test) - 10} more')

print('='*100)
