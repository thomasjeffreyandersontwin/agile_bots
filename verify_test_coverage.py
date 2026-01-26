import json

with open('docs/stories/story-graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def analyze_coverage(node, parent_chain=None, depth=0):
    """Analyze test coverage for all nodes"""
    if parent_chain is None:
        parent_chain = []
    
    node_id = node.get('id', '')
    node_title = node.get('title', '')
    node_type = node.get('type', '')
    has_test_class = 'test_class' in node
    has_test_file = 'test_file' in node
    test_scenarios = node.get('test_scenarios', [])
    scenarios_with_links = [s for s in test_scenarios if s.get('test_link')]
    
    # Check parent coverage
    parent_has_test = any(
        parent.get('test_file') is not None 
        for parent in parent_chain 
        if parent.get('type') in ['subepic', 'epic']
    )
    
    # Report nodes with test links
    if scenarios_with_links:
        valid = (has_test_class and has_test_file) or parent_has_test
        status = "✓ VALID" if valid else "✗ ORPHAN"
        print(f"{'  ' * depth}[{node_type}] {node_title}")
        print(f"{'  ' * depth}  {status} - test_class: {has_test_class}, test_file: {has_test_file}, parent_test: {parent_has_test}")
        print(f"{'  ' * depth}  Scenarios: {len(scenarios_with_links)}")
        
        if not valid:
            print(f"{'  ' * depth}  ⚠️  ORPHAN FOUND!")
            for scenario in scenarios_with_links:
                print(f"{'  ' * depth}    - {scenario.get('name')}: {scenario.get('test_link')}")
    
    # Recursively check children
    for child in node.get('children', []):
        analyze_coverage(child, parent_chain + [node], depth + 1)

print("Analyzing test coverage in story-graph.json...\n")

count = 0
max_display = 30  # Limit output

for epic in data.get('epics', []):
    if count >= max_display:
        print("\n... (output truncated) ...")
        break
    analyze_coverage(epic)
    count += 1
    print()

print("\nAnalysis complete!")
