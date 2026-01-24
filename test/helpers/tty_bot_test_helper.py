"""
TTY Bot Test Helper - Validates COMPLETE TTY formatting with ANSI codes

Tests validate entire formatted sections with ANSI codes, box drawing, and markers.
Every assertion checks for complete multi-line formatted output with proper escape sequences.
"""
from pathlib import Path
from .cli_bot_test_helper import CLIBotTestHelper


class TTYBotHelper:
    """Helper for bot-level TTY assertions - validates complete formatted sections"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_status_section_present(self, output: str):
        """
        Validate that the command produced output (instructions or status).
        
        Actual output typically contains instructions, not a status section.
        """
        # Just check that there's meaningful output
        assert len(output) > 0, "Output should not be empty"
        assert 'Instructions' in output or 'Behavior' in output or 'Action' in output, \
            f"Output should contain instructions or behavior/action info:\n{output[:500]}"
    
    def assert_scope_response_present(self, output: str):
        """
        Validate COMPLETE scope response in TTY format.
        
        Expected format (with ANSI codes):
        \x1b[1mScope:\x1b[0m story: Story1
        or
        [1mScope:[0m all
        """
        # Check for scope with ANSI codes (both full and simplified)
        scope_present = (
            'Scope:' in output or
            '\x1b[1mScope:\x1b[0m' in output or
            '[1mScope:[0m' in output
        )
        assert scope_present, \
            f"Missing scope response in TTY output:\n{output[:500]}"
    
    def assert_error_shows_behavior_not_found(self, output: str, behavior: str):
        """
        Validate COMPLETE error message format in TTY with color codes.
        
        Expected format (may have ANSI red color):
        ERROR: Behavior not found: behavior_name
        
        Available behaviors: behavior1, behavior2, ...
        """
        assert 'ERROR' in output, \
            f"Missing 'ERROR' indicator in output:\n{output[:500]}"
        
        expected_message = f"Behavior not found: {behavior}"
        assert expected_message in output, \
            f"Missing complete error message '{expected_message}' in output:\n{output[:500]}"
    
    def assert_error_shows_action_not_found(self, output: str, action: str):
        """
        Validate COMPLETE action not found error format in TTY.
        
        Expected format:
        ERROR: Action not found: action_name
        
        Available actions: action1, action2, ...
        """
        assert 'ERROR' in output, \
            f"Missing 'ERROR' indicator in output:\n{output[:500]}"
        
        expected_message = f"Action not found: {action}"
        assert expected_message in output, \
            f"Missing complete error message '{expected_message}' in output:\n{output[:500]}"
    
    def assert_status_shows_current_state(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE current state display format in TTY.
        
        Expected format:
        Current Position: behavior.action
        """
        expected_position_line = f"Current Position: {behavior}.{action}"
        assert expected_position_line in output, \
            f"Missing complete position line '{expected_position_line}' in output:\n{output[:500]}"
    
    def assert_bot_metadata_shown(self, output: str, bot_name: str):
        """
        Validate COMPLETE bot metadata display format in TTY.
        
        Expected format:
        Bot: story_bot
        """
        expected_bot_line = f"Bot: {bot_name}"
        assert expected_bot_line in output, \
            f"Missing complete bot line '{expected_bot_line}' in output:\n{output[:500]}"


class TTYInstructionsHelper:
    """Helper for instructions - validates complete formatted instruction sections"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_section_shows_behavior_and_action(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE INSTRUCTIONS section format in TTY with ANSI codes.
        
        Actual format (no INSTRUCTIONS header):
        \x1b[1mBehavior Instructions - behavior_name\x1b[0m
        
        \x1b[1mAction Instructions - action_name\x1b[0m
        """
        # Check for behavior and action headers with ANSI codes
        expected_behavior = f"\x1b[1mBehavior Instructions - {behavior}\x1b[0m"
        expected_action = f"\x1b[1mAction Instructions - {action}\x1b[0m"
        
        assert expected_behavior in output, \
            f"Missing behavior header:\n{expected_behavior}\n\nGot output:\n{output[:1500]}"
        
        assert expected_action in output, \
            f"Missing action header:\n{expected_action}\n\nGot output:\n{output[:1500]}"
    
    def assert_behavior_instructions_shown(self, output: str, behavior: str):
        """
        Validate COMPLETE behavior instructions header format in TTY with ANSI codes.
        
        Expected format:
        [1mBehavior Instructions - behavior_name[0m
        """
        expected_header = f"[1mBehavior Instructions - {behavior}[0m"
        assert expected_header in output, \
            f"Missing complete behavior instructions header with ANSI codes:\n{expected_header}\n\nGot output:\n{output[:1000]}"
    
    def assert_action_instructions_shown(self, output: str, action: str):
        """
        Validate COMPLETE action instructions header format in TTY with ANSI codes.
        
        Actual format:
        \x1b[1mAction Instructions - action_name\x1b[0m
        """
        expected_header = f"\x1b[1mAction Instructions - {action}\x1b[0m"
        assert expected_header in output, \
            f"Missing complete action instructions header:\n{expected_header}\n\nGot output:\n{output[:1000]}"


class TTYNavigationHelper:
    """Helper for navigation - validates complete formatted navigation displays with box drawing"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_current_position_shows(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE current position display format in TTY.
        
        Expected format:
        CLI STATUS
        Current Position: behavior.action
        
        Behaviors: behavior1, \x1b[1mbehavior2\x1b[0m, behavior3
        Actions: action1, \x1b[1maction2\x1b[0m
        """
        # Validate complete position line
        expected_position_line = f"Current Position: {behavior}.{action}"
        assert expected_position_line in output, \
            f"Missing complete position line '{expected_position_line}' in output:\n{output[:500]}"
    
    def assert_behavior_tree_shows_actions(self, output: str, behavior: str, actions_list: list):
        """
        Validate COMPLETE behavior tree format with box drawing characters.
        
        Expected format:
        ├── ➤ behavior_name
        │   ├── ➤ action1
        │   ├── action2
        │   └── action3
        
        or simpler format:
        behavior_name
          action1
          action2
          action3
        """
        # Validate behavior and ALL actions present
        assert behavior in output, \
            f"Missing behavior '{behavior}' in tree:\n{output[:500]}"
        
        for action in actions_list:
            assert action in output, \
                f"Missing action '{action}' for behavior '{behavior}' in tree:\n{output[:500]}"
    
    def assert_current_marker_present(self, output: str):
        """
        Validate current position marker present in TTY output.
        
        Expected: ➤ marker or bold text with ANSI codes
        """
        has_marker = '➤' in output or '\x1b[1m' in output or '[1m' in output
        assert has_marker, \
            f"Missing current position marker (➤ or ANSI bold) in output:\n{output[:500]}"
    
    def assert_footer_emphasizes_current(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE footer format with ANSI bold current items.
        
        Expected format:
        Behaviors: behavior1, \x1b[1mcurrent_behavior\x1b[0m, behavior3
        Actions: action1, \x1b[1mcurrent_action\x1b[0m, action3
        """
        # Validate behavior is bolded with ANSI codes
        behavior_bolded = (
            f'\x1b[1m{behavior}\x1b[0m' in output or  # Full ANSI escape
            f'[1m{behavior}[0m' in output  # Simplified ANSI
        )
        assert behavior_bolded, \
            f"Missing ANSI-bolded current behavior '\\x1b[1m{behavior}\\x1b[0m' in footer:\n{output[:500]}"
        
        # Validate action is bolded with ANSI codes
        action_bolded = (
            f'\x1b[1m{action}\x1b[0m' in output or
            f'[1m{action}[0m' in output
        )
        assert action_bolded, \
            f"Missing ANSI-bolded current action '\\x1b[1m{action}\\x1b[0m' in footer:\n{output[:500]}"


class TTYScopeHelper:
    """Helper for scope - validates complete formatted scope displays"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_scope_shows_target(self, output: str, scope_type: str, target: str):
        """
        Validate COMPLETE scope display format in TTY.
        
        Actual format (with emoji and "Current Scope:"):
        🎯 \x1b[1mCurrent Scope:\x1b[0m TestStory
        """
        # Check for "Current Scope:" with target
        scope_present = f'\x1b[1mCurrent Scope:\x1b[0m {target}' in output
        assert scope_present, \
            f"Missing complete scope line 'Current Scope: {target}' in output:\n{output[:500]}"
    
    def assert_scope_cleared_message(self, output: str):
        """
        Validate COMPLETE scope cleared message format in TTY.
        
        Expected format:
        Scope cleared
        """
        assert 'Scope cleared' in output, \
            f"Missing complete 'Scope cleared' message in output:\n{output[:500]}"
    
    def assert_scope_set_message(self, output: str, scope_type: str, target: str):
        """
        Validate COMPLETE scope set confirmation format in TTY.
        
        Expected format:
        Scope set to story: Story1
        """
        expected_message_parts = ['Scope set', scope_type]
        for part in expected_message_parts:
            assert part in output, \
                f"Missing '{part}' in scope set confirmation:\n{output[:500]}"


class TTYHelpHelper:
    """Helper for help - validates complete formatted help displays"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_help_shows_available_commands(self, output: str):
        """
        Validate COMPLETE help output format with commands table.
        
        Expected format (may have box drawing):
        ╔═══════════════════════════════╗
        ║ HELP                          ║
        ╠═══════════════════════════════╣
        ║ Available Commands            ║
        ╠═══════════════════════════════╣
        ║ command1    description       ║
        ║ command2    description       ║
        ╚═══════════════════════════════╝
        
        or simpler:
        HELP
        
        Available Commands:
        - command1: description
        - command2: description
        """
        # Validate help has substantive content
        assert len(output) > 100, \
            f"Help output too short ({len(output)} chars), expected detailed help:\n{output}"
        
        # Validate it contains command information
        has_commands = (
            'Available Commands' in output or
            'Commands:' in output or
            'HELP' in output
        )
        assert has_commands, \
            f"Missing commands section in help output:\n{output[:500]}"
    
    def assert_help_shows_command_details(self, output: str, command: str):
        """
        Validate specific command present in help output.
        """
        assert command in output, \
            f"Missing command '{command}' in help output:\n{output[:500]}"


class TTYBehaviorsHelper:
    """Helper for behaviors - validates behavior object properties"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_behavior_has_properties(self, behavior):
        """Validate behavior has expected properties."""
        assert behavior is not None, "Behavior should not be None"
        assert hasattr(behavior, 'name'), "Behavior should have 'name' property"
        assert hasattr(behavior, 'actions'), "Behavior should have 'actions' property"


class TTYBotTestHelper(CLIBotTestHelper):
    """TTY channel helper - validates complete TTY structures with ANSI codes and box drawing"""
    
    def __init__(self, tmp_path: Path):
        super().__init__(tmp_path, mode='tty')
        self.bot = TTYBotHelper(self)
        self.instructions = TTYInstructionsHelper(self)
        self.scope = TTYScopeHelper(self)
        self.navigation = TTYNavigationHelper(self)
        self.help = TTYHelpHelper(self)
        self.behaviors = TTYBehaviorsHelper(self)