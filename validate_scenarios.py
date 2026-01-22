import json
import re

data = json.load(open(r'c:\dev\agile_bots\docs\stories\story-graph.json', 'r', encoding='utf-8'))

violations = []

def find_scenarios_with_context(obj, epic_path='', sub_epic_path='', story_path=''):
    results = []
    if isinstance(obj, dict):
        # Track epic/sub_epic/story context
        current_epic = epic_path
        current_sub_epic = sub_epic_path
        current_story = story_path
        
        if 'epics' in obj:
            for i, epic in enumerate(obj['epics']):
                results.extend(find_scenarios_with_context(epic, f'epics[{i}]({epic.get("name", "")})', '', ''))
        elif 'sub_epics' in obj:
            for i, sub_epic in enumerate(obj.get('sub_epics', [])):
                results.extend(find_scenarios_with_context(sub_epic, epic_path, f'sub_epics[{i}]({sub_epic.get("name", "")})', ''))
        elif 'story_groups' in obj:
            for i, group in enumerate(obj.get('story_groups', [])):
                for j, story in enumerate(group.get('stories', [])):
                    story_location = f'{epic_path}.{sub_epic_path}.story_groups[{i}].stories[{j}]'
                    results.extend(find_scenarios_with_context(story, epic_path, sub_epic_path, story_location))
        
        # Check if this is a story with scenarios
        if 'scenarios' in obj and 'name' in obj:
            story_name = obj['name']
            for i, scenario in enumerate(obj.get('scenarios', [])):
                results.append({
                    'epic': epic_path,
                    'sub_epic': sub_epic_path,
                    'story_location': story_path,
                    'story_name': story_name,
                    'scenario_index': i,
                    'scenario': scenario
                })
    
    return results

scenarios_with_context = find_scenarios_with_context(data)

print(f'Analyzing {len(scenarios_with_context)} scenarios for violations...\n')

# Rule 1: Given Describes State Not Actions
for item in scenarios_with_context:
    scenario = item['scenario']
    steps = scenario.get('steps', '')
    
    # Handle both string and list formats
    if isinstance(steps, str):
        step_lines = steps.split('\n')
    elif isinstance(steps, list):
        step_lines = steps
    else:
        step_lines = []
    
    for step in step_lines:
        if step.strip().startswith('Given'):
            # Check for action verbs
            action_verbs = ['executes', 'invokes', 'calls', 'sends', 'receives', 'processes', 
                          'creates', 'generates', 'deploys', 'starts', 'initializes',
                          'triggered', 'clicked', 'submitted', 'performed']
            step_lower = step.lower()
            
            for verb in action_verbs:
                if verb in step_lower:
                    violations.append({
                        'rule': 'Given Describes State Not Actions',
                        'location': f"{item['story_location']}.scenarios[{item['scenario_index']}]",
                        'story': item['story_name'],
                        'scenario': scenario.get('name', ''),
                        'problem': step.strip(),
                        'reason': f'Given contains action verb "{verb}"',
                        'severity': 'High'
                    })
                    break

# Rule 2: Improper Gherkin Format (colons after GIVEN/WHEN/THEN)
for item in scenarios_with_context:
    scenario = item['scenario']
    steps = scenario.get('steps', '')
    
    if 'GIVEN:' in steps or 'WHEN:' in steps or 'THEN:' in steps:
        violations.append({
            'rule': 'Write Plain English Scenarios',
            'location': f"{item['story_location']}.scenarios[{item['scenario_index']}]",
            'story': item['story_name'],
            'scenario': scenario.get('name', ''),
            'problem': 'Uses colons after GIVEN:/WHEN:/THEN:',
            'reason': 'Improper Gherkin syntax - should be "Given", "When", "Then" without colons',
            'severity': 'Medium'
        })

# Rule 3: Missing Background field
for item in scenarios_with_context:
    scenario = item['scenario']
    if 'background' not in scenario:
        # Check if steps has common setup that should be in background
        steps = scenario.get('steps', '')
        
        # Handle both string and list formats
        if isinstance(steps, str):
            step_lines = steps.split('\n')
        elif isinstance(steps, list):
            step_lines = steps
        else:
            step_lines = []
        given_steps = [s for s in step_lines if s.strip().startswith('Given') or s.strip().startswith('And')]
        
        if len(given_steps) > 1:
            violations.append({
                'rule': 'Scenario Structure',
                'location': f"{item['story_location']}.scenarios[{item['scenario_index']}]",
                'story': item['story_name'],
                'scenario': scenario.get('name', ''),
                'problem': 'Missing background field with multiple Given steps',
                'reason': 'Scenarios should have separate background field for common setup',
                'severity': 'Low'
            })

# Rule 4: Steps as string instead of array
for item in scenarios_with_context:
    scenario = item['scenario']
    steps = scenario.get('steps', '')
    
    if isinstance(steps, str):
        violations.append({
            'rule': 'Scenario Structure',
            'location': f"{item['story_location']}.scenarios[{item['scenario_index']}]",
            'story': item['story_name'],
            'scenario': scenario.get('name', ''),
            'problem': 'Steps field is a string instead of array',
            'reason': 'Steps should be an array of strings, not a single concatenated string',
            'severity': 'Low'
        })

# Rule 5: Missing scenario type
for item in scenarios_with_context:
    scenario = item['scenario']
    
    if 'type' not in scenario:
        violations.append({
            'rule': 'Scenarios Cover All Cases',
            'location': f"{item['story_location']}.scenarios[{item['scenario_index']}]",
            'story': item['story_name'],
            'scenario': scenario.get('name', ''),
            'problem': 'Missing type field (happy_path, edge_case, error_case)',
            'reason': 'Scenarios should be classified by type',
            'severity': 'Low'
        })

# Print summary
print(f'Total violations found: {len(violations)}\n')

# Group by rule
by_rule = {}
for v in violations:
    rule = v['rule']
    if rule not in by_rule:
        by_rule[rule] = []
    by_rule[rule].append(v)

for rule, items in by_rule.items():
    print(f'{rule}: {len(items)} violations')

print('\n' + '='*80)
print('DETAILED VIOLATIONS')
print('='*80 + '\n')

# Show first 20 violations with details
for i, v in enumerate(violations[:20]):
    print(f"{i+1}. {v['rule']} ({v['severity']})")
    print(f"   Story: {v['story']}")
    print(f"   Scenario: {v['scenario']}")
    print(f"   Location: {v['location']}")
    print(f"   Problem: {v['problem']}")
    print(f"   Reason: {v['reason']}")
    print()

if len(violations) > 20:
    print(f"... and {len(violations) - 20} more violations\n")

# Save violations to file
with open(r'c:\dev\agile_bots\scenario_violations.json', 'w', encoding='utf-8') as f:
    json.dump(violations, f, indent=2, ensure_ascii=False)
    
print(f'Full violation list saved to: c:\\dev\\agile_bots\\scenario_violations.json')
