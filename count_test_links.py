import json

with open('docs/stories/story-graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_scenarios = 0
scenarios_with_links = 0
nodes_with_test_class = 0
nodes_with_test_file = 0

def count(node):
    global total_scenarios, scenarios_with_links, nodes_with_test_class, nodes_with_test_file
    
    test_scenarios = node.get('test_scenarios', [])
    total_scenarios += len(test_scenarios)
    scenarios_with_links += len([s for s in test_scenarios if s.get('test_link')])
    
    if 'test_class' in node:
        nodes_with_test_class += 1
    if 'test_file' in node:
        nodes_with_test_file += 1
    
    for child in node.get('children', []):
        count(child)

for epic in data.get('epics', []):
    count(epic)

print(f"Total test scenarios: {total_scenarios}")
print(f"Test scenarios with test_link: {scenarios_with_links}")
print(f"Nodes with test_class: {nodes_with_test_class}")
print(f"Nodes with test_file: {nodes_with_test_file}")
