"""
Test Initialize Bot Interface

SubEpic: Initialize Bot Interface
Parent Epic: Invoke Bot

CLI tests verify bot initialization and interface rendering.
Uses parameterized tests across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
import sys
import os
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# CLI TESTS - Bot Interface Operations
# ============================================================================

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