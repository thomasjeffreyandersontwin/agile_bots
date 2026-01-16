#!/usr/bin/env python3
"""
Test extraction from DrawIO and identify user/story errors.

This test:
1. Extracts story graph from DrawIO file
2. Compares extracted JSON with original JSON
3. Identifies discrepancies in users and stories
"""

import sys
import json
from pathlib import Path

# Add parent directories to path
script_dir = Path(__file__).parent
scenario_dir = script_dir
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram

def get_story_path(story, path=""):
    """Get a readable path for a story (epic > sub_epic > story)."""
    return path

def find_story_in_graph(story_name, story_graph, epic_name=None, sub_epic_name=None):
    """Find a story in the graph by name."""
    for epic in story_graph.get('epics', []):
        if epic_name and epic['name'] != epic_name:
            continue
        for sub_epic in epic.get('sub_epics', []):
            if sub_epic_name and sub_epic['name'] != sub_epic_name:
                continue
            for group in sub_epic.get('story_groups', []):
                for story in group.get('stories', []):
                    if story['name'] == story_name:
                        return story, epic['name'], sub_epic['name']
    return None, None, None

def compare_users(original_story, extracted_story, story_path):
    """Compare users between original and extracted story."""
    original_users = set(original_story.get('users', []))
    extracted_users = set(extracted_story.get('users', []))
    
    errors = []
    if original_users != extracted_users:
        missing = original_users - extracted_users
        extra = extracted_users - original_users
        if missing:
            errors.append(f"  Missing users: {sorted(missing)}")
        if extra:
            errors.append(f"  Extra users: {sorted(extra)}")
    
    return errors

def main():
    drawio_path = Path("3_then/expected copy.drawio")
    original_json_path = Path("1_given/story-graph.json")
    extracted_json_path = Path("1_given/extracted-for-test.json")
    
    print("=" * 80)
    print("EXTRACT TEST - Identifying User/Story Errors")
    print("=" * 80)
    print()
    
    # Load original JSON
    print(f"1. Loading original JSON: {original_json_path}")
    with open(original_json_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    print(f"   [OK] Loaded {len(original_data.get('epics', []))} epics")
    print()
    
    # Extract from DrawIO
    print(f"2. Extracting from DrawIO: {drawio_path}")
    diagram = StoryIODiagram()
    result = diagram.synchronize_outline(
        drawio_path=drawio_path,
        output_path=extracted_json_path
    )
    print(f"   [OK] Extraction complete")
    print()
    
    # Load extracted JSON
    print(f"3. Loading extracted JSON: {extracted_json_path}")
    with open(extracted_json_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    print(f"   [OK] Loaded {len(extracted_data.get('epics', []))} epics")
    print()
    
    # Compare stories and users
    print("4. Comparing stories and users...")
    print()
    
    total_errors = 0
    total_stories_checked = 0
    
    for epic in original_data.get('epics', []):
        epic_name = epic['name']
        for sub_epic in epic.get('sub_epics', []):
            sub_epic_name = sub_epic['name']
            for group in sub_epic.get('story_groups', []):
                for original_story in group.get('stories', []):
                    story_name = original_story['name']
                    total_stories_checked += 1
                    
                    # Find corresponding story in extracted data
                    extracted_story, found_epic, found_sub_epic = find_story_in_graph(
                        story_name, extracted_data, epic_name, sub_epic_name
                    )
                    
                    if not extracted_story:
                        print(f"[ERROR] Story not found in extracted data:")
                        print(f"  Epic: {epic_name}")
                        print(f"  Sub-Epic: {sub_epic_name}")
                        print(f"  Story: {story_name}")
                        print()
                        total_errors += 1
                        continue
                    
                    # Compare users
                    user_errors = compare_users(original_story, extracted_story, story_name)
                    if user_errors:
                        print(f"[ERROR] User mismatch for story:")
                        print(f"  Epic: {epic_name}")
                        print(f"  Sub-Epic: {sub_epic_name}")
                        print(f"  Story: {story_name}")
                        for error in user_errors:
                            print(error)
                        print(f"  Original users: {sorted(original_story.get('users', []))}")
                        print(f"  Extracted users: {sorted(extracted_story.get('users', []))}")
                        print()
                        total_errors += 1
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total stories checked: {total_stories_checked}")
    print(f"Total errors found: {total_errors}")
    print()
    
    if total_errors == 0:
        print("[OK] No user/story errors found!")
        return 0
    else:
        print(f"[FAIL] Found {total_errors} errors")
        return 1

if __name__ == "__main__":
    exit(main())

