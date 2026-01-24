# Test Migration Status

## ✅ Completed

1. **Folder Structure Created**
   - ✓ `test/build_agile_bots/`
   - ✓ `test/invoke_bot/`
   - ✓ `test/invoke_bot/panel/`
   - ✓ `test/helpers/`

2. **Helpers Consolidated**
   - ✓ All helpers moved to `test/helpers/`
   - ✓ Imports updated in helper files

3. **Files Merged**
   - ✓ `test/invoke_bot/test_get_help_using_cli.py` (domain + CLI merged)
   - ✓ `test/invoke_bot/test_edit_story_nodes.py` (domain + CLI merged)

## 🔄 Remaining Work (Manual Splitting Required)

The following files require **manual extraction** of specific test classes from large files:

### Files Requiring Complex Splits

1. **test_navigate_and_execute_behaviors.py** → Split into 3 files:
   - `test_display_behavior_action_state.py`
   - `test_navigate_behavior_and_actions.py`
   - `test_perform_behavior_action_in_bot_workflow.py`

2. **test_perform_action.py** → Split into 8 files:
   - `test_build_story_graph.py`
   - `test_clarify_requirements.py`
   - `test_decide_strategy.py`
   - `test_prepare_common_instructions.py`
   - `test_render_content.py`
   - `test_use_rules_in_prompt.py`
   - `test_validate_with_rules.py`

3. **test_manage_scope.py** → Split into 6 files:
   - `test_set_story_filter.py`
   - `test_manage_story_scope.py`
   - `test_scope_files.py`
   - `test_display_scope.py`
   - `test_submit_scoped_action.py`

4. **test_initialize_bot.py** → Split into 4 files:
   - `test_load_bot_behavior_and_actions.py`
   - `test_initialize_bot_interface.py`
   - `test_render_bot_interface.py`
   - `test_set_workspace.py`

5. **Missing Test Files to Create**:
   - `test_edit_increments.py`
   - `test_synchronize_graph_from_rendered.py`

6. **Panel Files to Move**:
   - All JS files from `test/panel/` to `test/invoke_bot/panel/`

## 📋 Next Steps

1. Use test-reorganization-plan.md as reference
2. Manually extract test classes according to the plan
3. Update pytest.ini configuration
4. Run tests to verify
5. Delete old files after confirmation

## Notes

- Simple 1:1 merges: **DONE** ✅
- Complex splits: **MANUAL WORK NEEDED** 🔧
- See `test-reorganization-plan.md` for complete mapping
