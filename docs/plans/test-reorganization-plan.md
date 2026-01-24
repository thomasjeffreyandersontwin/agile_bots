# Test Reorganization Plan - Align Tests with Story Graph Hierarchy

**Date:** 2026-01-24
**Goal:** Reorganize test files to match the Story Graph SubEpic structure

## Mapping Rules

1. **Epic** → Top-level test folder (e.g., `test/invoke_bot/`)
2. **SubEpic** → Test file name (e.g., `test_edit_story_nodes.py`)
3. **Story** → Test class name (e.g., `TestCreateEpic`)
4. **Scenario** → Test method name (e.g., `test_create_epic_with_name_at_default_position`)
5. **Domain + CLI tests** → Merged into single `.py` file
6. **Panel tests** → Separate `.js` files in `panel/` subfolder

---

## Epic: Build Agile Bots 🎯

### SubEpic: Generate MCP Tools

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| ❌ None found | `test/build_agile_bots/test_generate_mcp_tools.py` | **CREATE** | TestGenerateBotTools<br>TestGenerateBehaviorTools<br>TestGenerateMCPBotServer<br>TestGenerateBehaviorActionTools<br>TestDeployMCPBotServer<br>TestRestartMCPServerToLoadCodeChanges |

### SubEpic: Generate CLI

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| ❌ None found | `test/build_agile_bots/test_generate_cli.py` | **CREATE** | (To be determined from Story Graph) |

---

## Epic: Invoke Bot 🎯

### SubEpic: Edit Story Map → Edit Story Nodes

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| `test/domain/test_edit_story_graph.py`<br>`test/CLI/test_edit_story_graph_in_cli.py` | `test/invoke_bot/test_edit_story_nodes.py` | **MERGE** + **RENAME** | **Domain:**<br>• TestCreateEpic<br>• TestCreateChildStoryNode<br>• TestDeleteStoryNode<br>• TestUpdateStoryNodeName<br>• TestMoveStoryNodeToParent<br>• TestExecuteActionScopedToStoryNode<br><br>**CLI:**<br>• TestCreateEpic<br>• TestCreateChildStoryNodeUnderParent<br>• TestDeleteStoryNodeFromParent<br>• TestUpdateStoryNodename<br>• TestMoveStoryNode<br>• TestSubmitActionScopedToStoryScope |
| `test/panel/test_edit_story_graph_in_panel.js` | `test/invoke_bot/panel/test_edit_story_nodes_panel.js` | **RENAME** | (JavaScript panel tests) |

### SubEpic: Edit Story Map → Edit Increments

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| ❌ None found | `test/invoke_bot/test_edit_increments.py` | **CREATE** | TestCreateIncrement<br>TestDeleteIncrement<br>TestMoveStoryToIncrement<br>TestDisplayIncrementScope<br>TestShowAllIncrementScope |

### SubEpic: Edit Story Map → Filter Scope → Set Story Filter

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_manage_scope.py` (TestFilterScopeByStories)<br>Part of `test/CLI/test_manage_scope_using_cli.py` (TestFilterScopeByStoriesUsingCLI) | `test/invoke_bot/test_set_story_filter.py` | **SPLIT** + **MERGE** | TestAddFilterPartToStoryScope<br>TestRemoveFilterPartFromStoryScope<br>TestAddIncrementFilterPartToStoryScope<br>TestRemoveIncrementFilterPartFromStoryScope |

### SubEpic: Edit Story Map → Filter Scope → Manage Story Scope

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_manage_scope.py` (TestNavigateStoryGraph)<br>Part of `test/CLI/test_manage_scope_using_cli.py` (TestNavigateStoryGraphUsingCLI) | `test/invoke_bot/test_manage_story_scope.py` | **SPLIT** + **MERGE** | TestNavigateStoryGraph<br>TestSaveStoryNodes<br>TestDisplayStoryScopeHierarchy |

### SubEpic: Edit Story Map → Filter Scope → Scope Files

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_manage_scope.py` (TestFilterScopeByFiles)<br>Part of `test/CLI/test_manage_scope_using_cli.py` (TestFilterScopeByFilesUsingCLI) | `test/invoke_bot/test_scope_files.py` | **SPLIT** + **MERGE** | TestFilterScopeByFiles<br>TestGetFilesFilteredByStoryScope<br>TestOpenStoryFiles |

### SubEpic: Edit Story Map → Filter Scope → Display Scope

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_manage_scope.py` (TestCreateScope, TestPersistScope, TestClearScope)<br>Part of `test/CLI/test_manage_scope_using_cli.py` (TestCreateScopeUsingCLI, TestDisplayScopeUsingCLI) | `test/invoke_bot/test_display_scope.py` | **SPLIT** + **MERGE** | TestCreateScope<br>TestPersistScope<br>TestClearScope<br>TestDisplayBuildScopeThroughCLI<br>TestShowAllScopeThroughPanel<br>TestDisplayFilteredKnowledgeGraphThroughCLI |
| `test/panel/test_manage_scope.js`<br>`test/panel/test_scope_view.js` | `test/invoke_bot/panel/test_display_scope_panel.js` | **MERGE** + **RENAME** | (JavaScript panel tests) |

### SubEpic: Edit Story Map → Submit Scoped Action

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_manage_scope.py` (TestExecuteActionsWithScope, TestEnrichScopeWithLinks)<br>Part of `test/CLI/test_manage_scope_using_cli.py` (TestExecuteActionsWithScopeUsingCLI) | `test/invoke_bot/test_submit_scoped_action.py` | **SPLIT** + **MERGE** | TestExecuteActionsWithScope<br>TestEnrichScopeWithLinks<br>TestExecuteActionScopedToStoryNode<br>TestSubmitActionScopedToIncrement<br>TestSubmitActionScopedToStoryScope<br>TestAutomaticallyRefreshStoryGraphChanges |

---

### SubEpic: Initiialize Bot → Load Bot, Behavior, and Actions

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| `test/domain/test_initialize_bot.py` (TestResolveBotPath, TestLoadBotBehaviors, TestLoadActions, TestManageBotRegistry)<br>`test/CLI/test_initialize_cli_session.py` (TestResolveBotPathUsingCLI, TestLoadBotUsingCLI, TestLoadBotBehaviorsUsingCLI, TestLoadActionsUsingCLI, TestSwitchRegisteredBots) | `test/invoke_bot/test_load_bot_behavior_and_actions.py` | **MERGE** + **EXTRACT** | **Domain:**<br>• TestResolveBotPath<br>• TestLoadBot<br>• TestLoadBotBehaviors<br>• TestLoadActions<br>• TestManageBotRegistry<br><br>**CLI:**<br>• TestResolveBotPathUsingCLI<br>• TestLoadBotUsingCLI<br>• TestLoadBotBehaviorsUsingCLI<br>• TestLoadActionsUsingCLI<br>• TestSwitchRegisteredBots |

### SubEpic: Initiialize Bot → Initialize Bot Interface

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/CLI/test_initialize_cli_session.py` (TestDetectCLIMode, TestInitializeCLISession) | `test/invoke_bot/test_initialize_bot_interface.py` | **SPLIT** + **EXTRACT** | TestDetectAndConfigureTTYNonTTYInput<br>TestStartCLISessionInPipeMode<br>TestStartCLISessionInTTYMode<br>TestStartCLISessionInJSONMode<br>TestOpenPanel<br>TestExitREPL |

### SubEpic: Initiialize Bot → Render Bot Interface

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/CLI/test_initialize_cli_session.py` | `test/invoke_bot/test_render_bot_interface.py` | **SPLIT** + **EXTRACT** | TestViewSessionHeader<br>TestDisplayCLIBotCommandInNavigationMenuFooter<br>TestDisplayPipedModeInstructionsForAIAgents<br>TestViewHeadlessModeStatus<br>TestDisplaySessionStatus<br>TestTogglePanelSection |

### SubEpic: Initiialize Bot → Set Workspace

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_initialize_bot.py` (TestManageBotRegistry)<br>Part of `test/CLI/test_initialize_cli_session.py` (TestLoadWorkspaceContext) | `test/invoke_bot/test_set_workspace.py` | **SPLIT** + **MERGE** | TestManageBotRegistry<br>TestLoadWorkspaceContext<br>TestChangeWorkspacePath |

---

### SubEpic: Navigate Behavior Actions → Display Behavior Action State

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_navigate_and_execute_behaviors.py` (TestManageBehaviorActionState)<br>Part of `test/CLI/test_navigate_behaviors_using_cli_commands.py` (TestManageBehaviorActionStateUsingCLI, TestDisplayContextUsingCLI) | `test/invoke_bot/test_display_behavior_action_state.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestManageBehaviorActionState<br><br>**CLI:**<br>• TestManageBehaviorActionStateUsingCLI<br>• TestDisplayContextUsingCLI |

### SubEpic: Navigate Behavior Actions → Navigate Behavior And Actions

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_navigate_and_execute_behaviors.py` (TestManageBehaviors, TestNavigateToBehaviorActionAndExecute, TestNavigateSequentially)<br>Part of `test/CLI/test_navigate_behaviors_using_cli_commands.py` (TestManageBehaviorsUsingCLI, TestNavigateToBehaviorActionAndExecuteUsingCLI, TestNavigateSequentiallyUsingCLI) | `test/invoke_bot/test_navigate_behavior_and_actions.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestManageBehaviors<br>• TestNavigateToBehaviorActionAndExecute<br>• TestNavigateSequentially<br><br>**CLI:**<br>• TestManageBehaviorsUsingCLI<br>• TestNavigateToBehaviorActionAndExecuteUsingCLI<br>• TestNavigateSequentiallyUsingCLI |
| `test/panel/test_navigate_behaviors.js`<br>`test/panel/test_behaviors_view.js`<br>`test/panel/test_behaviors_view_example.js` | `test/invoke_bot/panel/test_navigate_behavior_and_actions_panel.js` | **MERGE** + **RENAME** | (JavaScript panel tests) |

### SubEpic: Navigate Behavior Actions → Perform Behavior Action In Bot Workflow

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_navigate_and_execute_behaviors.py` (TestInjectContextIntoInstructions, TestExecuteEndToEndWorkflow, TestTrackActivityForWorkspace)<br>Part of `test/CLI/test_navigate_behaviors_using_cli_commands.py` (TestExecuteEndToEndWorkflowUsingCLI) | `test/invoke_bot/test_perform_behavior_action_in_bot_workflow.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestInjectContextIntoInstructions<br>• TestExecuteEndToEndWorkflow<br>• TestTrackActivityForWorkspace<br><br>**CLI:**<br>• TestExecuteEndToEndWorkflowUsingCLI |

---

### SubEpic: Perform Action → Build Story Graph

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_perform_action.py` (TestBuildStoryGraph)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestBuildStoryGraphUsingCLI) | `test/invoke_bot/test_build_story_graph.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestBuildStoryGraph<br><br>**CLI:**<br>• TestBuildStoryGraphUsingCLI |

### SubEpic: Perform Action → Clarify Requirements

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_perform_action.py` (TestClarifyRequirements)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestClarifyRequirementsUsingCLI) | `test/invoke_bot/test_clarify_requirements.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestClarifyRequirements<br><br>**CLI:**<br>• TestClarifyRequirementsUsingCLI |

### SubEpic: Perform Action → Decide Strategy

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_perform_action.py` (TestDecideStrategy)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestDecideStrategyUsingCLI) | `test/invoke_bot/test_decide_strategy.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestDecideStrategy<br><br>**CLI:**<br>• TestDecideStrategyUsingCLI |

### SubEpic: Perform Action → Prepare Common Instructions For Behavior, Action, and Scope

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| `test/domain/test_save_guardrails.py` (ALL classes)<br>Part of `test/domain/test_perform_action.py` (TestSaveGuardrailsViaCLI)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestSaveGuardrailsUsingCLI, TestHandleErrorsUsingCLI) | `test/invoke_bot/test_prepare_common_instructions.py` | **MERGE** + **SPLIT** | **Domain:**<br>• TestSaveClarificationAnswers<br>• TestSaveClarificationEvidence<br>• TestSaveStrategyDecisions<br>• TestSaveMultipleGuardrails<br>• TestSaveFileIsolation<br>• TestInjectContextIntoInstructions<br><br>**CLI:**<br>• TestSaveGuardrailsUsingCLI<br>• TestHandleErrorsUsingCLI |
| `test/panel/test_display_instructions.js`<br>`test/panel/test_instructions_view.js` | `test/invoke_bot/panel/test_prepare_common_instructions_panel.js` | **MERGE** + **RENAME** | (JavaScript panel tests) |

### SubEpic: Perform Action → Render Content

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_perform_action.py` (TestRenderOutput)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestRenderOutputUsingCLI) | `test/invoke_bot/test_render_content.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestRenderOutput<br><br>**CLI:**<br>• TestRenderOutputUsingCLI |

### SubEpic: Perform Action → Synchronize Graph From Rendered

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| ❌ None found | `test/invoke_bot/test_synchronize_graph_from_rendered.py` | **CREATE** | TestDetectStoryGraphChangesFromDiagram<br>TestCreateChildStoryNodeFromDiagram<br>TestDeleteStoryNodeFromDiagram<br>TestMoveStoryNodeFromDiagram<br>TestUpdateStoryNodeNameFromDiagram<br>TestPersistStoryGraphChangesFromDiagram |

### SubEpic: Perform Action → Use Rules In Prompt

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_perform_action.py` (TestDisplayRules)<br>`test/CLI/test_display_rules_through_repl.py` (ALL)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestDisplayRulesUsingCLI) | `test/invoke_bot/test_use_rules_in_prompt.py` | **MERGE** + **SPLIT** | **Domain:**<br>• TestDisplayRules<br><br>**CLI:**<br>• TestDisplayRulesUsingCLI |

### SubEpic: Perform Action → Validate With Rules

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| Part of `test/domain/test_perform_action.py` (TestValidateRules)<br>Part of `test/CLI/test_execute_actions_using_cli.py` (TestValidateRulesUsingCLI) | `test/invoke_bot/test_validate_with_rules.py` | **SPLIT** + **MERGE** | **Domain:**<br>• TestValidateRules<br><br>**CLI:**<br>• TestValidateRulesUsingCLI |

---

### SubEpic: Get Help Using CLI

| Current Test Files | New Test File | Action | Test Classes |
|-------------------|---------------|--------|--------------|
| `test/domain/test_get_help.py` (TestGetHelp)<br>`test/CLI/test_get_help_using_cli.py` (TestGetHelpUsingCLI, TestDisplayHelpUsingCLI) | `test/invoke_bot/test_get_help_using_cli.py` | **MERGE** + **RENAME** | **Domain:**<br>• TestGetHelp<br><br>**CLI:**<br>• TestGetHelpUsingCLI<br>• TestDisplayHelpUsingCLI |
| `test/panel/test_get_help.js` | `test/invoke_bot/panel/test_get_help_panel.js` | **RENAME** | (JavaScript panel tests) |

---

## New Folder Structure

```
test/
├── build_agile_bots/
│   ├── __init__.py
│   ├── test_generate_mcp_tools.py
│   └── test_generate_cli.py
│
├── invoke_bot/
│   ├── __init__.py
│   │
│   # Edit Story Map SubEpics
│   ├── test_edit_story_nodes.py
│   ├── test_edit_increments.py
│   ├── test_set_story_filter.py
│   ├── test_manage_story_scope.py
│   ├── test_scope_files.py
│   ├── test_display_scope.py
│   ├── test_submit_scoped_action.py
│   │
│   # Initiialize Bot SubEpics
│   ├── test_load_bot_behavior_and_actions.py
│   ├── test_initialize_bot_interface.py
│   ├── test_render_bot_interface.py
│   ├── test_set_workspace.py
│   │
│   # Navigate Behavior Actions SubEpics
│   ├── test_display_behavior_action_state.py
│   ├── test_navigate_behavior_and_actions.py
│   ├── test_perform_behavior_action_in_bot_workflow.py
│   │
│   # Perform Action SubEpics
│   ├── test_build_story_graph.py
│   ├── test_clarify_requirements.py
│   ├── test_decide_strategy.py
│   ├── test_prepare_common_instructions.py
│   ├── test_render_content.py
│   ├── test_synchronize_graph_from_rendered.py
│   ├── test_use_rules_in_prompt.py
│   ├── test_validate_with_rules.py
│   │
│   # Get Help Using CLI SubEpic
│   ├── test_get_help_using_cli.py
│   │
│   └── panel/
│       ├── __init__.py
│       ├── test_edit_story_nodes_panel.js
│       ├── test_display_scope_panel.js
│       ├── test_navigate_behavior_and_actions_panel.js
│       ├── test_prepare_common_instructions_panel.js
│       ├── test_get_help_panel.js
│       └── helpers/
│           └── (panel test helpers)
│
├── helpers/
│   ├── __init__.py
│   ├── cli_bot_test_helper.py
│   ├── json_bot_test_helper.py
│   ├── pipe_bot_test_helper.py
│   ├── tty_bot_test_helper.py
│   └── bot_test_helper.py
│
└── end_2_end/
    └── (keep as-is)
```

---

## Files to DELETE After Migration

### Python Test Files (after merging):
- `test/domain/test_edit_story_graph.py`
- `test/domain/test_initialize_bot.py`
- `test/domain/test_manage_scope.py`
- `test/domain/test_navigate_and_execute_behaviors.py`
- `test/domain/test_perform_action.py`
- `test/domain/test_save_guardrails.py`
- `test/domain/test_get_help.py`

### CLI Test Files (after merging):
- `test/CLI/test_edit_story_graph_in_cli.py`
- `test/CLI/test_initialize_cli_session.py`
- `test/CLI/test_manage_scope_using_cli.py`
- `test/CLI/test_navigate_behaviors_using_cli_commands.py`
- `test/CLI/test_execute_actions_using_cli.py`
- `test/CLI/test_display_rules_through_repl.py`
- `test/CLI/test_get_help_using_cli.py`

### Panel Test Files (after moving):
- `test/panel/test_edit_story_graph_in_panel.js`
- `test/panel/test_manage_scope.js`
- `test/panel/test_scope_view.js`
- `test/panel/test_navigate_behaviors.js`
- `test/panel/test_behaviors_view.js`
- `test/panel/test_behaviors_view_example.js`
- `test/panel/test_display_instructions.js`
- `test/panel/test_instructions_view.js`
- `test/panel/test_get_help.js`

### Folders to DELETE:
- `test/domain/` (after extracting helpers to `test/helpers/`)
- `test/CLI/` (after extracting helpers to `test/helpers/`)
- `test/panel/` (after moving to `test/invoke_bot/panel/`)

---

## Migration Steps

1. **Create new folder structure**
   - Create `test/build_agile_bots/`
   - Create `test/invoke_bot/`
   - Create `test/invoke_bot/panel/`
   - Create `test/helpers/`

2. **Move and consolidate helpers**
   - Move all helper files from `test/domain/helpers/` and `test/CLI/helpers/` to `test/helpers/`
   - Update imports in helper files

3. **Create new test files** (start with simplest merges)
   - `test_get_help_using_cli.py` (simple merge)
   - `test_edit_story_nodes.py` (simple merge)
   - Then proceed with more complex splits

4. **Update imports** in all new test files
   - Change from `from domain.bot_test_helper` to `from helpers.bot_test_helper`
   - Change from `from CLI.helpers` to `from helpers`

5. **Run tests** after each file migration to ensure nothing breaks

6. **Update pytest configuration**
   - Update `pytest.ini` to reflect new test structure
   - Update any CI/CD configurations

7. **Delete old files** only after confirming all tests pass

---

## Action Legend

- **MERGE** = Combine multiple files into one
- **SPLIT** = Extract test classes from large file into new file
- **RENAME** = Just rename the file (no content changes)
- **CREATE** = Create new test file (no existing tests)
- **EXTRACT** = Take specific test classes from a file

---

## Notes

- All domain and CLI tests for a SubEpic go into the same `.py` file
- Panel tests (JavaScript) stay separate in `panel/` subfolder
- Test helpers are consolidated into shared `test/helpers/` folder
- Maintain test class naming conventions (TestXxx for domain, TestXxxUsingCLI for CLI)
- Keep end-to-end tests in their own folder
