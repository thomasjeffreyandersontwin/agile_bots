import json
import os
from pathlib import Path

def find_invalid_test_files(story_graph_path):
    """
    Find nodes with test_file that is just a folder (ends with /)
    """
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    invalid_entries = []
    
    def check_node(node, parent_chain=None):
        """Recursively check nodes for invalid test_file entries"""
        if parent_chain is None:
            parent_chain = []
        
        node_name = node.get('name', '')
        test_file = node.get('test_file')
        
        # Check if test_file is just a folder (ends with /)
        if test_file and isinstance(test_file, str) and test_file.endswith('/'):
            invalid_entries.append({
                'node_name': node_name,
                'test_file': test_file,
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
    
    return invalid_entries

def remove_invalid_test_files(story_graph_path, invalid_entries):
    """Remove invalid test_file entries (folders) from the story graph"""
    with open(story_graph_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    # Create a set of node names with invalid test_file
    nodes_to_clean = set(entry['node_name'] for entry in invalid_entries)
    
    def clean_node(node):
        """Recursively clean nodes by removing invalid test_file"""
        node_name = node.get('name', '')
        
        # Remove test_file if this node has an invalid one
        if node_name in nodes_to_clean:
            test_file = node.get('test_file')
            if test_file and isinstance(test_file, str) and test_file.endswith('/'):
                node.pop('test_file', None)
        
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
    invalid_entries = find_invalid_test_files(story_graph_path)
    
    if invalid_entries:
        print(f"\nFound {len(invalid_entries)} invalid test_file entries (folders instead of files):\n")
        
        for i, entry in enumerate(invalid_entries, 1):
            print(f"{i}. Node: {entry['node_name']}")
            print(f"   Invalid test_file: {entry['test_file']}")
            print(f"   Parent Chain: {' > '.join(entry['parent_chain'])}")
            print()
        
        print(f"Proceeding to remove {len(invalid_entries)} invalid test_file entries...")
        cleaned_graph = remove_invalid_test_files(story_graph_path, invalid_entries)
        
        # Backup original
        backup_path = story_graph_path.with_suffix('.json.backup2')
        import shutil
        shutil.copy(story_graph_path, backup_path)
        print(f"Backup saved to {backup_path}")
        
        # Write cleaned version
        with open(story_graph_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_graph, f, indent=2, ensure_ascii=False)
        print(f"Cleaned story graph saved to {story_graph_path}")
        print("Done!")
    else:
        print("No invalid test_file entries found!")
