"""Update nested SubEpic test_file paths to point to actual test files"""
import json

data = json.load(open('docs/stories/story-graph.json', encoding='utf-8'))
invoke_bot = [e for e in data['epics'] if e['name'] == 'Invoke Bot'][0]

# Map nested SubEpic names to test files (relative to test/ folder)
# Only LEAF SubEpics (the ones with stories) get test files
NESTED_SUBEPIC_TO_FILE = {
    # Initialize Bot nested SubEpics
    'Load Bot, Behavior, and Actions': 'invoke_bot/initialize_bot/test_load_bot_behavior_and_actions.py',
    'Initialize Bot Interface': 'invoke_bot/initialize_bot/test_initialize_bot_interface.py',
    'Render Bot Interface': 'invoke_bot/initialize_bot/test_render_bot_interface.py',
    'Set Workspace': 'invoke_bot/initialize_bot/test_set_workspace.py',
    
    # Edit Story Map nested SubEpics (leaf level)
    'Set Story Filter': 'invoke_bot/edit_story_map/test_set_story_filter.py',
    'Filter Story Scope': 'invoke_bot/edit_story_map/test_display_scope.py',
    'Manage Story Scope': 'invoke_bot/edit_story_map/test_manage_story_scope.py',
    'Set File Filter': 'invoke_bot/edit_story_map/test_scope_files.py',
    'Filter File Scope': 'invoke_bot/edit_story_map/test_scope_files.py',
    'Edit Increments': 'invoke_bot/edit_story_map/test_edit_increments.py',
    'Edit Story Nodes': 'invoke_bot/edit_story_map/test_edit_story_nodes.py',
    'Submit Scoped Action': 'invoke_bot/edit_story_map/test_submit_scoped_action.py',
    
    # Navigate Behavior Actions nested SubEpics
    'Navigate Behavior And Actions': 'invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py',
    'Perform Behavior Action In Bot Workflow': 'invoke_bot/navigate_behavior_actions/test_perform_behavior_action_in_bot_workflow.py',
    'Display Behavior Action State': 'invoke_bot/navigate_behavior_actions/test_display_behavior_action_state.py',
    
    # Perform Action nested SubEpics
    'Prepare Common Instructions For Behavior, Action, and Scope': 'invoke_bot/perform_action/test_prepare_common_instructions.py',
    'Clarify Requirements': 'invoke_bot/perform_action/test_clarify_requirements.py',
    'Decide Strategy': 'invoke_bot/perform_action/test_decide_strategy.py',
    'Build Story Graph': 'invoke_bot/perform_action/test_build_story_graph.py',
    'Validate With Rules': 'invoke_bot/perform_action/test_validate_with_rules.py',
    'Render Content': 'invoke_bot/perform_action/test_render_content.py',
    'Use Rules In Prompt': 'invoke_bot/perform_action/test_use_rules_in_prompt.py',
    'Synchronize Graph From Rendered': 'invoke_bot/perform_action/test_synchronize_graph_from_rendered.py',
}

updates_count = 0
story_cleanup_count = 0

def process_subepic(se, level=0):
    """Recursively process SubEpic and all nested SubEpics"""
    global updates_count, story_cleanup_count
    
    se_name = se['name']
    test_file = NESTED_SUBEPIC_TO_FILE.get(se_name)
    
    if test_file:
        se['test_file'] = test_file
        updates_count += 1
        print(f'[OK] {"  " * level}{se_name[:60]:60} -> {test_file}')
    
    # Clean up Story-level test_file (stories should only have test_class)
    for story in se.get('stories', []):
        if 'test_file' in story:
            del story['test_file']
            story_cleanup_count += 1
    
    # Recursively process nested SubEpics
    for nested in se.get('sub_epics', []):
        process_subepic(nested, level + 1)

for sub_epic in invoke_bot['sub_epics']:
    # Process all nested SubEpics recursively
    for nested in sub_epic.get('sub_epics', []):
        process_subepic(nested)
    
    # Also clean up direct stories (like Get Help SubEpic)
    for story in sub_epic.get('stories', []):
        if 'test_file' in story:
            del story['test_file']
            story_cleanup_count += 1

# Write back
with open('docs/stories/story-graph.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\n[DONE] Updated {updates_count} nested SubEpic test_file paths')
print(f'[DONE] Removed test_file from {story_cleanup_count} Stories (they only need test_class)')
