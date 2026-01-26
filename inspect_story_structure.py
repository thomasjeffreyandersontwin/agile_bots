import json

with open('docs/stories/story-graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

epics = data.get('epics', [])
print(f'Total root epics: {len(epics)}\n')

# Count nodes with test scenarios that have test links
def count_test_links(node, depth=0):
    count = 0
    has_test_class = 'test_class' in node
    has_test_file = 'test_file' in node
    test_scenarios = node.get('test_scenarios', [])
    
    scenarios_with_links = [s for s in test_scenarios if s.get('test_link')]
    
    if scenarios_with_links:
        print(f"{'  ' * depth}[{node.get('type', '?')}] {node.get('title', 'Unknown')}")
        print(f"{'  ' * depth}  test_class: {has_test_class}, test_file: {has_test_file}")
        print(f"{'  ' * depth}  scenarios with links: {len(scenarios_with_links)}")
        for scenario in scenarios_with_links[:2]:  # Show first 2
            print(f"{'  ' * depth}    - {scenario.get('name', 'Unknown')}: {scenario.get('test_link', '')}")
        count += len(scenarios_with_links)
    
    for child in node.get('children', []):
        count += count_test_links(child, depth + 1)
    
    return count

total = 0
for epic in epics[:3]:  # Show first 3 root epics
    total += count_test_links(epic)
    print()

print(f"\nTotal test links found in first 3 epics: {total}")
