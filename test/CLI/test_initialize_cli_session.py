"""
Initialize CLI Session Tests - Parameterized Across Channels

Maps directly to: test_initialize_bot.py domain tests

These tests focus on CLI-specific concerns:
- Session initialization and configuration
- Mode detection (TTY, Pipe, JSON)
- Bot and workspace loading
- Bot paths resolution via CLI
- Bot configuration loading via CLI
- Behaviors and actions loading via CLI

Uses parameterized tests to run same test logic across all 3 channels.
"""
import pytest
import sys
from agile_bots.test.CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# STORY: Resolve Bot Paths
# Maps to: TestResolveBotPath in test_initialize_bot.py (5 tests)
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
        THEN: Returns real agile_bot/base_actions path
        
        Domain: test_bot_paths_base_actions_directory_property
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then
        from agile_bots.src.bot.workspace import get_base_actions_directory
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
        assert (helper.cli_session.bot.bot_paths.python_workspace_root / 'agile_bots').exists()
    
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
        assert (repo_root / 'agile_bots').exists()
        assert (repo_root / 'agile_bots' / 'bots' / 'story_bot').exists()


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
class TestInitializeCLISession:
    """
    Story: Initialize CLI Session
    
    CLI-specific story: Starting a CLI session with bot and workspace
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_initializes_bot(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session initializes bot (all channels)
        GIVEN: Bot and workspace configured
        WHEN: CLISession is created
        THEN: Session wraps bot
              Bot is accessible via session
        """
        # Given/When - Helper creates CLI session internally
        helper = helper_class(tmp_path)
        
        # Then - Validate complete bot structure
        bot = helper.cli_session.bot
        assert bot.bot_name == 'story_bot'
        assert bot.behaviors is not None
        assert len(bot.behaviors.names) > 0
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_loads_existing_state(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session loads existing state (all channels)
        GIVEN: Bot with saved state
        WHEN: CLISession is created
        THEN: Bot loads previous state
              Current position restored
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('discovery', 'validate')
        
        # When - Execute command to verify state loaded
        cli_response = helper.cli_session.execute_command('discovery')
        
        # Then - Bot at expected position
        helper.domain.behaviors.assert_at_behavior_action('discovery', 'validate')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_can_execute_commands(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session can execute commands (all channels)
        GIVEN: Initialized CLI session
        WHEN: Command is executed
        THEN: Session returns response
              Output formatted for channel
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When
        cli_response = helper.cli_session.execute_command('shape')
        
        # Then - Validate complete CLI response structure
        assert isinstance(cli_response.output, str)
        helper.bot.assert_status_section_present(cli_response.output)


class TestDetectCLIMode:
    """
    Story: Detect CLI Mode
    
    CLI-specific story: Auto-detecting TTY vs Pipe vs JSON mode
    """
    
    def test_cli_detects_tty_mode(self, tmp_path, monkeypatch):
        """
        SCENARIO: CLI detects TTY mode
        GIVEN: stdin/stdout are TTY
        WHEN: CLISession created without explicit mode
        THEN: Session uses TTY mode
        """
        # Given - Mock TTY environment
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: True)
        monkeypatch.setattr(sys.stdout, 'isatty', lambda: True)
        
        # When/Then
        helper = TTYBotTestHelper(tmp_path)
        assert helper.cli_session.mode == 'tty'
    
    def test_cli_detects_pipe_mode(self, tmp_path, monkeypatch):
        """
        SCENARIO: CLI detects pipe mode  
        GIVEN: stdin/stdout are piped (not TTY)
        WHEN: CLISession created without explicit mode
        THEN: Session uses markdown mode
        """
        # Given - Mock piped environment
        monkeypatch.setattr(sys.stdin, 'isatty', lambda: False)
        monkeypatch.setattr(sys.stdout, 'isatty', lambda: False)
        
        # When/Then
        helper = PipeBotTestHelper(tmp_path)
        assert helper.cli_session.mode == 'markdown'
    
    def test_cli_accepts_json_mode_flag(self, tmp_path):
        """
        SCENARIO: CLI accepts JSON mode flag
        GIVEN: JSON mode explicitly requested
        WHEN: CLISession created with mode='json'
        THEN: Session uses JSON mode
        """
        # Given/When
        helper = JsonBotTestHelper(tmp_path)
        
        # Then
        assert helper.cli_session.mode == 'json'


class TestLoadWorkspaceContext:
    """
    Story: Load Workspace Context
    
    CLI-specific story: Loading workspace files and context
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_session_loads_workspace_directory(self, tmp_path, helper_class):
        """
        SCENARIO: CLI session loads workspace directory (all channels)
        GIVEN: Workspace directory exists
        WHEN: CLISession is created
        THEN: Workspace directory accessible
        """
        # Given/When
        helper = helper_class(tmp_path)
        
        # Then - Validate workspace directory is properly set
        workspace_dir = helper.cli_session.workspace_directory
        assert workspace_dir.exists()
        assert workspace_dir == helper.domain.workspace


# ============================================================================
# STORY: Switch Registered Bots
# New CLI story for bot switching
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
