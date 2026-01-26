import json
import os
from pathlib import Path

def find_orphan_test_links(story_graph_path):
    """
    Find story scenarios with test_method where:
    - The story has test_class but no test_file
    - A subepic above it doesn't have a test file
    """
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    orphans = []
    
    def check_node(node, parent_chain=None):
        """Recursively check nodes for orphaned test methods"""
        if parent_chain is None:
            parent_chain = []
        
        node_type = node.get('type', '')
        node_id = node.get('id', '')
        node_title = node.get('name', '')  # Changed from 'title' to 'name'
        
        # Check if this node has scenarios with test_method
        scenarios = node.get('scenarios', [])
        
        for scenario in scenarios:
            test_method = scenario.get('test_method', '')
            
            if test_method:
                # Check if the story has both test_class AND test_file
                has_test_class = node.get('test_class') is not None
                has_test_file = node.get('test_file') is not None
                has_valid_test = has_test_class and has_test_file
                
                # Check if any parent subepic/epic has a test file
                parent_has_test = any(
                    parent.get('test_file') is not None 
                    for parent in parent_chain
                )
                
                # If neither the story (with both test_class and test_file) nor parent has test info, it's an orphan
                if not has_valid_test and not parent_has_test:
                    orphans.append({
                        'node_id': node_id,
                        'node_title': node_title,
                        'node_type': node_type,
                        'scenario': scenario.get('name', ''),
                        'test_method': test_method,
                        'has_test_class': has_test_class,
                        'has_test_file': has_test_file,
                        'parent_chain': [p.get('name', '') for p in parent_chain]
                    })
        
        # Recursively check children in story_groups and sub_epics
        for story_group in node.get('story_groups', []):
            for story in story_group.get('stories', []):
                check_node(story, parent_chain + [node])
        
        for sub_epic in node.get('sub_epics', []):
            check_node(sub_epic, parent_chain + [node])
    
    # Start checking from root nodes (epics)
    for root_node in story_graph.get('epics', []):
        check_node(root_node)
    
    return orphans

def remove_orphan_test_links(story_graph_path, orphans):
    """Remove orphaned test_method and test_class from the story graph"""
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Create a set of orphan identifiers for quick lookup
    orphan_methods = set()
    nodes_to_clean_test_class = set()
    
    for orphan in orphans:
        orphan_methods.add((orphan['node_title'], orphan['test_method']))
        # If the node has a test_class but no test_file, mark it for test_class removal
        if orphan['has_test_class'] and not orphan['has_test_file']:
            nodes_to_clean_test_class.add(orphan['node_title'])
    
    def clean_node(node):
        """Recursively clean nodes by removing orphaned test_method and test_class"""
        node_name = node.get('name', '')
        scenarios = node.get('scenarios', [])
        
        # Remove test_method from orphaned scenarios
        for scenario in scenarios:
            test_method = scenario.get('test_method', '')
            if test_method and (node_name, test_method) in orphan_methods:
                # This is an orphan, remove the test_method
                scenario.pop('test_method', None)
        
        # Remove test_class if this node is marked for cleaning
        if node_name in nodes_to_clean_test_class:
            node.pop('test_class', None)
        
        # Recursively clean children in story_groups and sub_epics
        for story_group in node.get('story_groups', []):
            for story in story_group.get('stories', []):
                clean_node(story)
        
        for sub_epic in node.get('sub_epics', []):
            clean_node(sub_epic)
    
    # Clean all root nodes (epics)
    for root_node in story_graph.get('epics', []):
        clean_node(root_node)
    
    return story_graph

if __name__ == '__main__':
    story_graph_path = Path(__file__).parent / 'docs' / 'stories' / 'story-graph.json'
    
    print(f"Analyzing {story_graph_path}...")
    orphans = find_orphan_test_links(story_graph_path)
    
    if orphans:
        print(f"\nFound {len(orphans)} orphaned test methods:\n")
        nodes_with_orphan_test_class = set()
        
        for i, orphan in enumerate(orphans, 1):
            print(f"{i}. Story: {orphan['node_title']}")
            print(f"   Scenario: {orphan['scenario']}")
            print(f"   Test Method: {orphan['test_method']}")
            print(f"   Has test_class: {orphan['has_test_class']}, Has test_file: {orphan['has_test_file']}")
            print(f"   Parent Chain: {' > '.join(orphan['parent_chain'])}")
            
            if orphan['has_test_class'] and not orphan['has_test_file']:
                nodes_with_orphan_test_class.add(orphan['node_title'])
                print(f"   WARNING: Will also remove orphaned test_class")
            print()
        
        if nodes_with_orphan_test_class:
            print(f"Will remove test_class from {len(nodes_with_orphan_test_class)} node(s)\n")
        
        print(f"Proceeding to remove {len(orphans)} orphaned test methods and test_class...")
        cleaned_graph = remove_orphan_test_links(story_graph_path, orphans)
        
        # Backup original
        backup_path = story_graph_path.with_suffix('.json.backup')
        import shutil
        shutil.copy(story_graph_path, backup_path)
        print(f"Backup saved to {backup_path}")
        
        # Write cleaned version
        with open(story_graph_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_graph, f, indent=2, ensure_ascii=False)
        print(f"Cleaned story graph saved to {story_graph_path}")
        print("Done!")
    else:
        print("No orphaned test methods found!")
