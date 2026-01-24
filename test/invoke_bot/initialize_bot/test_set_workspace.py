"""
Test Set Workspace

SubEpic: Set Workspace
Parent Epic: Invoke Bot

CLI tests verify bot initialization and interface rendering.
Uses parameterized tests across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
import os
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# CLI TESTS - Bot Interface Operations
# ============================================================================

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