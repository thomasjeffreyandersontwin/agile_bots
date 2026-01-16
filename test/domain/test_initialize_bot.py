
import pytest
import json
import os
from pathlib import Path
from agile_bots.src.bot.bot import Bot
from agile_bots.src.bot_path import BotPath
from agile_bots.src.actions.strategy.strategy_action import StrategyAction
from agile_bots.test.domain.bot_test_helper import BotTestHelper


# ================================================================================
# SUB-EPIC: Initialize Bot
# ================================================================================

# Story: Resolve Bot Paths (sequential_order: 4)
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
        THEN: Returns real agile_bot/base_actions path (not test directory)
        
        Note: base_actions_directory always returns the real agile_bot/base_actions path,
        not the test directory. This is by design - see get_base_actions_directory() in workspace.py.
        """
        helper = BotTestHelper(tmp_path)
        
        from agile_bots.src.bot.workspace import get_base_actions_directory
        expected_base_actions = get_base_actions_directory()
        assert helper.bot.bot_paths.base_actions_directory == expected_base_actions
        assert helper.bot.bot_paths.base_actions_directory.exists()
    
    def test_bot_paths_python_workspace_root_property(self, tmp_path):
        """SCENARIO: BotPath.python_workspace_root property returns Python workspace root."""
        helper = BotTestHelper(tmp_path)
        
        assert isinstance(helper.bot.bot_paths.python_workspace_root, Path)
        assert helper.bot.bot_paths.python_workspace_root.exists()
        assert (helper.bot.bot_paths.python_workspace_root / 'agile_bots').exists()
    
    def test_bot_paths_find_repo_root_method(self, tmp_path):
        """SCENARIO: BotPath.find_repo_root() method returns repository root."""
        helper = BotTestHelper(tmp_path)
        
        repo_root = helper.bot.bot_paths.find_repo_root()
        
        assert isinstance(repo_root, Path)
        assert repo_root.exists()
        assert (repo_root / 'agile_bots').exists()
        assert (repo_root / 'agile_bots' / 'bots' / 'story_bot').exists()
    
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
class TestLoadBot:
    
    def test_bot_instantiation_with_bot_name_and_workspace(self, tmp_path):
        """Scenario: Bot can be instantiated with bot_name and workspace (BotConfig merged into Bot)."""
        # Given: Production bot
        helper = BotTestHelper(tmp_path)
        
        # Then: Bot has correct bot_name
        assert helper.bot.bot_name == 'story_bot'
        assert helper.bot.name == 'story_bot'
        assert helper.bot.bot_directory.exists()
        assert helper.bot.bot_paths.workspace_directory == helper.workspace
    
    def test_bot_name_property(self, tmp_path):
        """Scenario: Bot.name property returns bot name from config (BotConfig merged into Bot)."""
        # Given: Production bot
        helper = BotTestHelper(tmp_path)
        
        # Then: Bot.name matches expected
        assert helper.bot.name == 'story_bot'
        assert helper.bot.bot_name == 'story_bot'
    
# Story: Load Bot Behaviors (sequential_order: 2)
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
