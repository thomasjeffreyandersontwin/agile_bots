import json

data = json.load(open(r'c:\dev\agile_bots\docs\stories\story-graph.json', 'r', encoding='utf-8'))

def find_scenarios(obj, path=''):
    scenarios = []
    if isinstance(obj, dict):
        if 'scenarios' in obj and 'name' in obj:
            for i, s in enumerate(obj.get('scenarios', [])):
                scenarios.append({
                    'story': obj['name'], 
                    'scenario': s.get('name', ''), 
                    'steps': s.get('steps', ''), 
                    'path': f'{path}.scenarios[{i}]'
                })
        for key, value in obj.items():
            scenarios.extend(find_scenarios(value, f'{path}.{key}' if path else key))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            scenarios.extend(find_scenarios(item, f'{path}[{i}]'))
    return scenarios

scenarios = find_scenarios(data)
print(f'Found {len(scenarios)} scenarios total')
print()

# Show all scenarios with their steps
for i, s in enumerate(scenarios):
    print(f'{i+1}. Story: {s["story"]}')
    print(f'   Scenario: {s["scenario"]}')
    print(f'   Steps:')
    steps = s['steps'].split('\n')
    for step in steps:
        print(f'     {step}')
    print()
    if i >= 20:  # Show first 20 scenarios
        print(f'... and {len(scenarios) - 21} more scenarios')
        break
