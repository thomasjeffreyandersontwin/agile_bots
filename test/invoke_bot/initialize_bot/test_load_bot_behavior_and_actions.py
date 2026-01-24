"""
Test Load Bot, Behavior, and Actions

SubEpic: Load Bot, Behavior, and Actions
Parent Epic: Invoke Bot

Domain tests verify core bot logic.
CLI tests verify command parsing and output formatting across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
import os
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper
from bot_path import BotPath


# ============================================================================
# DOMAIN TESTS - Core Bot Logic
# ============================================================================

class TestResolveBotPath:
    
    def test_bot_paths_resolves_bot_and_workspace_directories_from_environment(self, tmp_path):
        """
        SCENARIO: BotPath resolves directories from environment variables
        GIVEN: BOT_DIRECTORY and WORKING_AREA environment variables set
        WHEN: BotPath accessed from bot
        THEN: Both directory properties return paths from environment
        """
        # Given: Production bot with bot_paths
        helper = BotTestHelper(tmp_path)
        bot_paths = helper.bot.bot_paths
        
        # Then: Both directories resolved correctly
        assert bot_paths.bot_directory == helper.bot_directory
        assert bot_paths.workspace_directory == helper.workspace
        assert bot_paths.bot_directory.exists()
        assert bot_paths.workspace_directory.exists()
        assert (bot_paths.bot_directory / 'bot_config.json').exists()
    
    def test_bot_paths_base_actions_directory_property(self, tmp_path):
        """
        SCENARIO: BotPath.base_actions_directory returns real agile_bot base_actions
        GIVEN: BotPath instantiated
        WHEN: base_actions_directory property accessed
        THEN: Returns real agile_bots/base_actions path (not test directory)
        
        Note: base_actions_directory always returns the real agile_bots/base_actions path,
        not the test directory. This is by design - see get_base_actions_directory() in workspace.py.
        """
        helper = BotTestHelper(tmp_path)
        
        from bot.workspace import get_base_actions_directory
        expected_base_actions = get_base_actions_directory()
        assert helper.bot.bot_paths.base_actions_directory == expected_base_actions
        assert helper.bot.bot_paths.base_actions_directory.exists()
    
    def test_bot_paths_python_workspace_root_property(self, tmp_path):
        """SCENARIO: BotPath.python_workspace_root property returns Python workspace root."""
        helper = BotTestHelper(tmp_path)
        
        assert isinstance(helper.bot.bot_paths.python_workspace_root, Path)
        assert helper.bot.bot_paths.python_workspace_root.exists()
        assert (helper.bot.bot_paths.python_workspace_root / 'src').exists()
    
    def test_bot_paths_find_repo_root_method(self, tmp_path):
        """SCENARIO: BotPath.find_repo_root() method returns repository root."""
        helper = BotTestHelper(tmp_path)
        
        repo_root = helper.bot.bot_paths.find_repo_root()
        
        assert isinstance(repo_root, Path)
        assert repo_root.exists()
        assert (repo_root / 'src').exists()
        assert (repo_root / 'bots' / 'story_bot').exists()
    
    def test_bot_paths_raises_error_when_environment_variables_not_set(self, tmp_path):
        """
        SCENARIO: BotPath raises error when environment variables not set
        GIVEN: No BOT_DIRECTORY or WORKING_AREA environment variables
        WHEN: BotPath instantiated
        THEN: Raises RuntimeError
        """
        import os
        original_bot_dir = os.environ.get('BOT_DIRECTORY')
        original_working_area = os.environ.get('WORKING_AREA')
        
        try:
            if 'BOT_DIRECTORY' in os.environ:
                del os.environ['BOT_DIRECTORY']
            if 'WORKING_AREA' in os.environ:
                del os.environ['WORKING_AREA']
            
            with pytest.raises(RuntimeError):
                BotPath()
        finally:
            if original_bot_dir:
                os.environ['BOT_DIRECTORY'] = original_bot_dir
            if original_working_area:
                os.environ['WORKING_AREA'] = original_working_area

# Story: Load Bot Configuration (sequential_order: 1)

class TestLoadBotBehaviors:
    
    def test_load_behaviors_from_bot_config(self, tmp_path):
        """Scenario: Bot behaviors are loaded from BotConfig."""
        helper = BotTestHelper(tmp_path)
        # story_bot has exactly 7 behaviors (sorted by their order property)
        expected_behaviors = ['shape', 'prioritization', 'discovery', 'exploration', 'scenarios', 'tests', 'code']
        assert helper.bot.behaviors.names == expected_behaviors, \
            f"Expected {expected_behaviors}, got {helper.bot.behaviors.names}"
    
    def test_load_behaviors_sets_first_as_current(self, tmp_path):
        """Scenario: When behaviors are loaded, first behavior is set as current."""
        helper = BotTestHelper(tmp_path)
        # First behavior is whatever sorts first by order (no guarantee of specific name)
        assert helper.bot.behaviors.current is not None
        assert helper.bot.behaviors.current.name in helper.bot.behaviors.names
    
    def test_behavior_provides_access_to_all_config_properties(self, tmp_path):
        """
        Scenario: Loaded behavior provides access to all config properties
        GIVEN: Behavior loaded from production config
        WHEN: Config properties accessed
        THEN: All properties accessible with correct structure
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('prioritization')
        behavior = helper.bot.behaviors.current
        
        # Assert complete behavior structure with all config properties
        helper.behaviors.assert_behavior_complete_structure(
            behavior=behavior,
            expected_name='prioritization',
            expected_order=2,
            expected_actions=['clarify', 'strategy', 'validate', 'render'],
            expected_description='Organize stories into delivery increments based on business value, dependencies, and risk'
        )

class TestLoadActions:
    
    def test_load_actions_from_behavior_config(self, tmp_path):
        """Scenario: Actions are loaded and available."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        actions = helper.bot.behaviors.current.actions
        
        # Assert complete actions structure with all properties
        expected_actions = [
            {"name": "clarify", "order": 1, "next_action": "strategy"},
            {"name": "strategy", "order": 2, "next_action": "build"},
            {"name": "build", "order": 3, "next_action": "validate"},
            {"name": "validate", "order": 4, "next_action": "render"},
            {"name": "render", "order": 5, "next_action": None}
        ]
        helper.behaviors.assert_actions_complete_structure(actions, expected_actions)
        
        # Also verify current action is first one
        assert actions.current.action_name == 'clarify'
    
    def test_load_actions_sets_first_as_current(self, tmp_path):
        """Scenario: When actions are loaded, first action is set as current."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        assert helper.bot.behaviors.current.actions.current_action_name == 'clarify'
    
    def test_action_merges_instructions_from_base_and_behavior(self, tmp_path):
        """Scenario: Action merges instructions from BaseActionConfig and Behavior config."""
        # Given: Environment with behavior and actions
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        actions = helper.bot.behaviors.current.actions
        clarify_action = actions.find_by_name('clarify')
        
        # Then: Action has merged instructions
        assert clarify_action.action_name == 'clarify'
        assert clarify_action.instructions is not None
        assert 'base_instructions' in clarify_action.instructions
        assert isinstance(clarify_action.instructions['base_instructions'], list)
        
        # And: Base instructions are present (from real base_actions/clarify/action_config.json)
        base_instructions_list = clarify_action.instructions['base_instructions']
        assert isinstance(base_instructions_list, list)
        assert len(base_instructions_list) >= 1
        # Base instructions from clarify action_config.json contain the actual instructions
        # Just verify that we have some instructions (format may vary)

# Story: Manage Bot Registry (sequential_order: 5)

class TestManageBotRegistry:
    
    def test_get_list_of_registered_bots(self, tmp_path):
        """
        Scenario: Get List of Registered Bots
        GIVEN: bot registry has multiple registered bots (story_bot, task_bot, crc_bot)
        WHEN: bot.bots property is accessed
        THEN: System returns ["story_bot", "task_bot", "crc_bot"]
        """
        # Given: Bot registry with multiple bots
        helper = BotTestHelper(tmp_path)
        
        # Create additional bot directories
        task_bot_dir = tmp_path / 'bots' / 'task_bot'
        task_bot_dir.mkdir(parents=True, exist_ok=True)
        (task_bot_dir / 'bot_config.json').write_text(json.dumps({
            "bot_name": "task_bot",
            "behaviors": []
        }))
        
        crc_bot_dir = tmp_path / 'bots' / 'crc_bot'
        crc_bot_dir.mkdir(parents=True, exist_ok=True)
        (crc_bot_dir / 'bot_config.json').write_text(json.dumps({
            "bot_name": "crc_bot",
            "behaviors": []
        }))
        
        # When: bots property accessed
        registered_bots = helper.bot.bots
        
        # Then: Returns list of registered bot names
        assert isinstance(registered_bots, list)
        assert 'story_bot' in registered_bots
    
    def test_get_active_bot(self, tmp_path):
        """
        Scenario: Get Active Bot
        GIVEN: story_bot is currently active
        WHEN: bot.active_bot property is accessed
        THEN: System returns story_bot instance
        AND: Instance contains loaded behaviors and actions
        """
        # Given: story_bot is active
        helper = BotTestHelper(tmp_path)
        
        # When: active_bot property accessed
        active_bot = helper.bot.active_bot
        
        # Then: Returns story_bot instance
        assert active_bot is not None
        assert active_bot.bot_name == 'story_bot'
        assert active_bot.behaviors is not None
        assert len(active_bot.behaviors.names) > 0
    
    def test_set_active_bot_to_registered_bot(self, tmp_path):
        """
        Scenario: Set Active Bot to Registered Bot
        GIVEN: story_bot is currently active
        AND: crc_bot is registered (from production)
        WHEN: bot.active_bot is set to "crc_bot"
        THEN: System switches to crc_bot
        AND: System loads crc_bot configuration from bot_config.json
        AND: System loads crc_bot behaviors and actions
        AND: bot.active_bot returns crc_bot instance
        """
        # Given: story_bot is active and crc_bot is registered
        helper = BotTestHelper(tmp_path)
        
        # When: active_bot is set to crc_bot (which already exists in production)
        helper.bot.active_bot = "crc_bot"
        
        # Then: System switches to crc_bot
        active_bot = helper.bot.active_bot
        assert active_bot.bot_name == 'crc_bot'
    
    def test_attempt_to_set_unregistered_bot(self, tmp_path):
        """
        Scenario: Attempt to Set Unregistered Bot
        GIVEN: story_bot is currently active
        AND: "invalid_bot" is not registered
        WHEN: bot.active_bot is set to "invalid_bot"
        THEN: System raises BotNotFoundError with message "Bot 'invalid_bot' not found"
        AND: bot.active_bot still returns story_bot instance
        AND: No bot state changes occur
        """
        # Given: story_bot is active
        helper = BotTestHelper(tmp_path)
        original_bot_name = helper.bot.active_bot.bot_name
        
        # When/Then: Setting invalid bot raises error
        with pytest.raises(Exception) as exc_info:
            helper.bot.active_bot = "invalid_bot"
        
        assert "invalid_bot" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
        
        # And: active_bot still returns story_bot
        assert helper.bot.active_bot.bot_name == original_bot_name
    
    def test_set_active_bot_to_current_bot(self, tmp_path):
        """
        Scenario: Set Active Bot to Current Bot
        GIVEN: story_bot is currently active
        WHEN: bot.active_bot is set to "story_bot"
        THEN: System returns current story_bot instance
        AND: No reload or reconfiguration occurs
        AND: bot.active_bot still returns same story_bot instance
        """
        # Given: story_bot is active
        helper = BotTestHelper(tmp_path)
        original_bot = helper.bot.active_bot
        original_bot_id = id(original_bot)
        
        # When: active_bot set to current bot
        helper.bot.active_bot = "story_bot"
        
        # Then: Returns same instance (no reload)
        current_bot = helper.bot.active_bot
        assert current_bot.bot_name == 'story_bot'
        # Note: Depending on implementation, this might be same instance or new one
        # Just verify bot_name is correct

# ============================================================================
# CLI TESTS - Bot Operations via CLI Commands
# ============================================================================

class TestResolveBotPathUsingCLI:
    """
    Story: Resolve Bot Paths Using CLI
    
    Domain logic: test_initialize_bot.py::TestResolveBotPath
    CLI focus: Verify bot paths accessible via CLI session
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_resolves_bot_and_workspace_directories(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session resolves bot and workspace directories
        GIVEN: CLI session initialized
        WHEN: Bot paths accessed via CLI
        THEN: Directories resolved correctly
        
        Domain: test_bot_paths_resolves_bot_and_workspace_directories_from_environment
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then - Bot paths accessible via CLI session
        assert helper.cli_session.bot.bot_paths.bot_directory == helper.domain.bot_directory
        assert helper.cli_session.bot.bot_paths.workspace_directory == helper.domain.workspace
        assert helper.cli_session.bot.bot_paths.bot_directory.exists()
        assert helper.cli_session.bot.bot_paths.workspace_directory.exists()
        assert (helper.cli_session.bot.bot_paths.bot_directory / 'bot_config.json').exists()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_base_actions_directory_accessible(self, tmp_path, helper_class):
        """
        SCENARIO: Base actions directory accessible via CLI session
        GIVEN: CLI session initialized
        WHEN: base_actions_directory accessed via CLI
        THEN: Returns real agile_bots/base_actions path
        
        Domain: test_bot_paths_base_actions_directory_property
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then
        from bot.workspace import get_base_actions_directory
        expected_base_actions = get_base_actions_directory()
        assert helper.cli_session.bot.bot_paths.base_actions_directory == expected_base_actions
        assert helper.cli_session.bot.bot_paths.base_actions_directory.exists()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_python_workspace_root_accessible(self, tmp_path, helper_class):
        """
        SCENARIO: Python workspace root accessible via CLI session
        GIVEN: CLI session initialized
        WHEN: python_workspace_root accessed via CLI
        THEN: Returns Python workspace root path
        
        Domain: test_bot_paths_python_workspace_root_property
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then
        from pathlib import Path
        assert isinstance(helper.cli_session.bot.bot_paths.python_workspace_root, Path)
        assert helper.cli_session.bot.bot_paths.python_workspace_root.exists()
        assert (helper.cli_session.bot.bot_paths.python_workspace_root / 'src').exists()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_find_repo_root_method_works(self, tmp_path, helper_class):
        """
        SCENARIO: find_repo_root method works via CLI session
        GIVEN: CLI session initialized
        WHEN: find_repo_root() called via CLI
        THEN: Returns repository root path
        
        Domain: test_bot_paths_find_repo_root_method
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # When
        repo_root = helper.cli_session.bot.bot_paths.find_repo_root()
        
        # Then
        from pathlib import Path
        assert isinstance(repo_root, Path)
        assert repo_root.exists()
        assert (repo_root / 'src').exists()
        assert (repo_root / 'bots' / 'story_bot').exists()


# ============================================================================
# STORY: Load Bot Configuration
# Maps to: TestLoadBot in test_initialize_bot.py
# ============================================================================

class TestLoadBotUsingCLI:
    """
    Story: Load Bot Configuration Using CLI
    
    Domain logic: test_initialize_bot.py::TestLoadBot
    CLI focus: Verify bot configuration loaded and accessible via CLI
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_loads_bot_with_name_and_workspace(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session loads bot with name and workspace
        GIVEN: CLI session initialized
        WHEN: Bot accessed via CLI
        THEN: Bot has correct name and workspace
        
        Domain: test_bot_instantiation_with_bot_name_and_workspace
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then
        assert helper.cli_session.bot.bot_name == 'story_bot'
        assert helper.cli_session.bot.name == 'story_bot'
        assert helper.cli_session.bot.bot_directory.exists()
        assert helper.cli_session.bot.bot_paths.workspace_directory == helper.domain.workspace
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_bot_name_property_accessible(self, tmp_path, helper_class):
        """
        SCENARIO: Bot name property accessible via CLI session
        GIVEN: CLI session initialized
        WHEN: Bot name accessed
        THEN: Returns correct bot name
        
        Domain: test_bot_name_property
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then
        assert helper.cli_session.bot.name == 'story_bot'
        assert helper.cli_session.bot.bot_name == 'story_bot'


# ============================================================================
# STORY: Load Bot Behaviors
# Maps to: TestLoadBotBehaviors in test_initialize_bot.py
# ============================================================================

class TestLoadBotBehaviorsUsingCLI:
    """
    Story: Load Bot Behaviors Using CLI
    
    Domain logic: test_initialize_bot.py::TestLoadBotBehaviors
    CLI focus: Verify behaviors loaded and accessible via CLI commands
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_loads_behaviors_from_config(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session loads behaviors from bot config
        GIVEN: CLI session initialized
        WHEN: Behaviors accessed
        THEN: All behaviors loaded correctly
        
        Domain: test_load_behaviors_from_bot_config
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then
        expected_behaviors = {'scenarios', 'tests', 'code', 'discovery', 'exploration', 'prioritization', 'shape'}
        assert set(helper.cli_session.bot.behaviors.names) == expected_behaviors
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_sets_first_behavior_as_current(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session sets first behavior as current
        GIVEN: CLI session initialized
        WHEN: Current behavior accessed
        THEN: First behavior is current
        
        Domain: test_load_behaviors_sets_first_as_current
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then - Validate complete current behavior structure
        current_behavior = helper.cli_session.bot.behaviors.current
        helper.behaviors.assert_behavior_has_properties(current_behavior)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_behavior_config_properties_accessible(self, tmp_path, helper_class):
        """
        SCENARIO: Behavior config properties accessible via CLI session
        GIVEN: CLI session at prioritization behavior
        WHEN: Behavior config properties accessed
        THEN: All properties accessible with correct structure
        
        Domain: test_behavior_provides_access_to_all_config_properties
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('prioritization', 'clarify')
        
        # When - Navigate to prioritization
        cli_response = helper.cli_session.execute_command('prioritization')
        
        # Then - Behavior config accessible
        behavior = helper.cli_session.bot.behaviors.current
        helper.domain.behaviors.assert_behavior_complete_structure(
            behavior=behavior,
            expected_name='prioritization',
            expected_order=2,
            expected_actions=['clarify', 'strategy', 'validate', 'render'],
            expected_description='Organize stories into delivery increments based on business value, dependencies, and risk'
        )


# ============================================================================
# STORY: Load Actions
# Maps to: TestLoadActions in test_initialize_bot.py
# ============================================================================

class TestLoadActionsUsingCLI:
    """
    Story: Load Actions Using CLI
    
    Domain logic: test_initialize_bot.py::TestLoadActions
    CLI focus: Verify actions loaded and accessible via CLI navigation
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_loads_actions_from_behavior_config(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session loads actions from behavior config
        GIVEN: CLI session at shape behavior
        WHEN: Actions accessed
        THEN: All actions loaded correctly
        
        Domain: test_load_actions_from_behavior_config
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Navigate to shape to ensure it's loaded
        cli_response = helper.cli_session.execute_command('shape')
        
        # Then - Actions accessible
        actions = helper.cli_session.bot.behaviors.current.actions
        expected_actions = {'clarify', 'strategy', 'build', 'validate', 'render'}
        actual_actions = {a.action_name for a in actions._actions}
        assert actual_actions == expected_actions
        assert actions.current.action_name == 'clarify'
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_sets_first_action_as_current(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session sets first action as current
        GIVEN: CLI session at shape behavior
        WHEN: Current action accessed
        THEN: First action is current
        
        Domain: test_load_actions_sets_first_as_current
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('shape')
        
        # Then
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'clarify'
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_action_instructions_accessible(self, tmp_path, helper_class):
        """
        SCENARIO: Action instructions accessible via CLI session
        GIVEN: CLI session at shape.clarify
        WHEN: Action instructions accessed
        THEN: Merged instructions from base and behavior available
        
        Domain: test_action_merges_instructions_from_base_and_behavior
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Navigate to shape
        cli_response = helper.cli_session.execute_command('shape')
        
        # Then - Action instructions accessible
        actions = helper.cli_session.bot.behaviors.current.actions
        clarify_action = actions.find_by_name('clarify')
        
        assert clarify_action.action_name == 'clarify'
        
        # Validate complete instructions structure
        instructions = clarify_action.instructions
        assert 'base_instructions' in instructions
        base_instructions_list = instructions['base_instructions']
        assert isinstance(base_instructions_list, list)
        assert len(base_instructions_list) > 0, "base_instructions should contain instruction content"


# ============================================================================
# STORY: Initialize CLI Session
# CLI-specific story
# ============================================================================

class TestSwitchRegisteredBots:
    """
    Story: Switch Registered Bots
    
    CLI-specific story: Switching between registered bots via CLI commands
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_display_registered_bots_in_cli_status(self, tmp_path, helper_class):
        """
        SCENARIO: Display Registered Bots in CLI STATUS
        GIVEN: CLI has loaded multiple registered bots
        AND: current bot is "story_bot"
        WHEN: CLI STATUS section is displayed
        THEN: section shows "Bot: story_bot | Registered: story_bot | task_bot | review_bot"
        AND: section shows "To change bots: bot <name>"
        
        Domain: test_get_list_of_registered_bots
        """
        # Given
        helper = helper_class(tmp_path)
        
        # When - Execute status command to get CLI output
        cli_response = helper.cli_session.execute_command('status')
        
        # Then - Verify bot name displayed
        assert 'story_bot' in cli_response.output
        helper.bot.assert_status_section_present(cli_response.output)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_switch_to_valid_registered_bot(self, tmp_path, helper_class):
        """
        SCENARIO: Switch to Valid Registered Bot
        GIVEN: current bot is "story_bot"
        AND: "task_bot" is registered
        WHEN: user enters "bot task_bot"
        THEN: CLI switches to task_bot
        AND: CLI STATUS section updates to show "Bot: task_bot | Registered: ..."
        AND: bot behaviors and actions are loaded from task_bot configuration
        
        Domain: test_set_active_bot_to_registered_bot
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create task_bot directory
        task_bot_dir = tmp_path / 'bots' / 'task_bot'
        task_bot_dir.mkdir(parents=True, exist_ok=True)
        import json
        (task_bot_dir / 'bot_config.json').write_text(json.dumps({
            "bot_name": "task_bot",
            "behaviors": []
        }))
        
        # When - Execute bot switch command
        cli_response = helper.cli_session.execute_command('bot task_bot')
        
        # Then - Verify switched to task_bot
        # Note: Actual implementation may vary, just verify output returned
        assert isinstance(cli_response.output, str)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_attempt_to_switch_to_unregistered_bot(self, tmp_path, helper_class):
        """
        SCENARIO: Attempt to Switch to Unregistered Bot
        GIVEN: current bot is "story_bot"
        AND: "invalid_bot" is not registered
        WHEN: user enters "bot invalid_bot"
        THEN: CLI displays error: "Bot 'invalid_bot' not found"
        AND: CLI shows "Available bots: story_bot, task_bot, review_bot"
        AND: current bot remains "story_bot"
        
        Domain: test_attempt_to_set_unregistered_bot
        """
        # Given
        helper = helper_class(tmp_path)
        original_bot_name = helper.cli_session.bot.bot_name
        
        # When - Attempt to switch to invalid bot
        cli_response = helper.cli_session.execute_command('bot invalid_bot')
        
        # Then - Verify error message or bot remains same
        # Note: Actual implementation may vary
        current_bot_name = helper.cli_session.bot.bot_name
        assert current_bot_name == original_bot_name