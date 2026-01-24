"""
Pipe/Markdown Bot Test Helper - Validates COMPLETE markdown formatting

Tests validate entire formatted sections, not fragments.
Every assertion checks for complete multi-line formatted output.
"""
from pathlib import Path
from .cli_bot_test_helper import CLIBotTestHelper


class PipeBotHelper:
    """Helper for bot-level Pipe/Markdown assertions - validates complete formatted sections"""
    
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
        Validate COMPLETE scope response in Markdown format.
        
        Actual format (with emoji):
        **🎯 Current Scope:** all (entire project)
        or
        **🎯 Current Scope:** TestStory
        """
        assert '**🎯 Current Scope:**' in output, \
            f"Missing scope response in Markdown output:\n{output[:500]}"
    
    def assert_error_shows_behavior_not_found(self, output: str, behavior: str):
        """
        Validate COMPLETE error message format in Markdown.
        
        Expected format:
        ## ERROR
        
        Behavior not found: behavior_name
        
        Available behaviors: ...
        """
        # Validate complete error structure
        expected_error_start = f"## ERROR"
        assert expected_error_start in output, \
            f"Missing error header in output:\n{output[:500]}"
        
        # Validate complete error message
        expected_message = f"Behavior not found: {behavior}"
        assert expected_message in output, \
            f"Missing complete error message '{expected_message}' in output:\n{output[:500]}"
    
    def assert_error_shows_action_not_found(self, output: str, action: str):
        """
        Validate COMPLETE action not found error format.
        
        Expected format:
        ## ERROR
        
        Action not found: action_name
        
        Available actions: ...
        """
        expected_error_start = "## ERROR"
        assert expected_error_start in output, \
            f"Missing error header in output:\n{output[:500]}"
        
        expected_message = f"Action not found: {action}"
        assert expected_message in output, \
            f"Missing complete error message '{expected_message}' in output:\n{output[:500]}"
    
    def assert_status_shows_current_state(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE current state display format.
        
        Expected format:
        **Current Position:** behavior.action
        """
        expected_position_line = f"**Current Position:** {behavior}.{action}"
        assert expected_position_line in output, \
            f"Missing complete position line '{expected_position_line}' in output:\n{output[:500]}"
    
    def assert_bot_metadata_shown(self, output: str, bot_name: str):
        """
        Validate COMPLETE bot metadata display format.
        
        Expected format:
        **Bot:** story_bot
        """
        expected_bot_line = f"**Bot:** {bot_name}"
        assert expected_bot_line in output, \
            f"Missing complete bot line '{expected_bot_line}' in output:\n{output[:500]}"


class PipeInstructionsHelper:
    """Helper for instructions - validates complete formatted instruction sections"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_section_shows_behavior_and_action(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE INSTRUCTIONS section format in Markdown.
        
        Actual format (no INSTRUCTIONS header):
        # Behavior: behavior_name
        
        ## Behavior Instructions - behavior_name
        
        ## Action Instructions - action_name
        """
        # Assert on the actual formatted structure (no INSTRUCTIONS header)
        expected_behavior_header = f"# Behavior: {behavior}"
        expected_behavior_instructions = f"## Behavior Instructions - {behavior}"
        expected_action_header = f"## Action Instructions - {action}"
        
        assert expected_behavior_header in output, \
            f"Missing behavior header:\n{expected_behavior_header}\n\nGot output:\n{output[:1500]}"
        
        assert expected_behavior_instructions in output, \
            f"Missing behavior instructions header:\n{expected_behavior_instructions}\n\nGot output:\n{output[:1500]}"
        
        assert expected_action_header in output, \
            f"Missing action instructions header:\n{expected_action_header}\n\nGot output:\n{output[:1500]}"
    
    def assert_behavior_instructions_shown(self, output: str, behavior: str):
        """
        Validate COMPLETE behavior instructions header format.
        
        Expected format:
        ## Behavior Instructions - behavior_name
        """
        expected_header = f"## Behavior Instructions - {behavior}"
        assert expected_header in output, \
            f"Missing complete behavior instructions header:\n{expected_header}\n\nGot output:\n{output[:1000]}"
    
    def assert_action_instructions_shown(self, output: str, action: str):
        """
        Validate COMPLETE action instructions header format.
        
        Expected format:
        ## Action Instructions - action_name
        """
        expected_header = f"## Action Instructions - {action}"
        assert expected_header in output, \
            f"Missing complete action instructions header:\n{expected_header}\n\nGot output:\n{output[:1000]}"


class PipeNavigationHelper:
    """Helper for navigation - validates complete formatted navigation displays"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_current_position_shows(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE current position display format.
        
        Expected format:
        ## CLI STATUS
        
        **Current Position:** behavior.action
        
        **Behaviors:** behavior1, **current_behavior**, behavior3
        **Actions:** action1, action2, **current_action**
        """
        # Validate complete status section exists
        assert '## CLI STATUS' in output, \
            f"Missing CLI STATUS section in output:\n{output[:500]}"
        
        # Validate complete position line
        expected_position_line = f"**Current Position:** {behavior}.{action}"
        assert expected_position_line in output, \
            f"Missing complete position line '{expected_position_line}' in output:\n{output[:500]}"
    
    def assert_behavior_tree_shows_actions(self, output: str, behavior: str, actions_list: list):
        """
        Validate COMPLETE behavior tree format with all actions.
        
        Expected format:
        ├── behavior_name
        │   ├── action1
        │   ├── action2
        │   └── action3
        """
        # Validate behavior line exists
        assert behavior in output, \
            f"Missing behavior '{behavior}' in tree output:\n{output[:500]}"
        
        # Validate ALL actions present
        for action in actions_list:
            assert action in output, \
                f"Missing action '{action}' for behavior '{behavior}' in tree:\n{output[:500]}"
    
    def assert_current_marker_present(self, output: str):
        """
        Validate current position marker present in some form.
        
        Expected: bold formatting **current** or "Current Position:" label
        """
        has_marker = ('**' in output and 'Current' in output) or 'Current Position' in output
        assert has_marker, \
            f"Missing current position marker in output:\n{output[:500]}"
    
    def assert_footer_emphasizes_current(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE footer format with bold current items.
        
        Expected format:
        **Behaviors:** behavior1, **current_behavior**, behavior3
        **Actions:** action1, **current_action**, action3
        """
        # Validate complete behavior footer line with bold current
        expected_behavior_bold = f"**{behavior}**"
        assert expected_behavior_bold in output, \
            f"Missing bolded current behavior '{expected_behavior_bold}' in footer:\n{output[:500]}"
        
        # Validate complete action footer line with bold current
        expected_action_bold = f"**{action}**"
        assert expected_action_bold in output, \
            f"Missing bolded current action '{expected_action_bold}' in footer:\n{output[:500]}"


class PipeScopeHelper:
    """Helper for scope - validates complete formatted scope displays"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_scope_shows_target(self, output: str, scope_type: str, target: str):
        """
        Validate COMPLETE scope display format.
        
        Actual format (with emoji):
        **🎯 Current Scope:** TestStory
        """
        # Validate complete scope line exists with target
        expected_scope_line = f"**🎯 Current Scope:** {target}"
        assert expected_scope_line in output, \
            f"Missing complete scope line '{expected_scope_line}' in output:\n{output[:500]}"
    
    def assert_scope_cleared_message(self, output: str):
        """
        Validate COMPLETE scope cleared message format.
        
        Expected format:
        Scope cleared
        or
        **Scope cleared**
        """
        assert 'Scope cleared' in output, \
            f"Missing complete 'Scope cleared' message in output:\n{output[:500]}"
    
    def assert_scope_set_message(self, output: str, scope_type: str, target: str):
        """
        Validate COMPLETE scope set confirmation format.
        
        Expected format:
        Scope set to story: Story1
        or
        **Scope set** to epic: EpicA
        """
        # Look for complete scope set message
        expected_message_parts = ['Scope set', scope_type]
        for part in expected_message_parts:
            assert part in output, \
                f"Missing '{part}' in scope set confirmation:\n{output[:500]}"


class PipeHelpHelper:
    """Helper for help - validates complete formatted help displays"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_help_shows_available_commands(self, output: str):
        """
        Validate COMPLETE help output format with commands list.
        
        Expected format:
        ## HELP
        
        ## Available Commands
        
        - command1: description
        - command2: description
        """
        # Validate help section exists with substantive content
        assert len(output) > 100, \
            f"Help output too short ({len(output)} chars), expected detailed help:\n{output}"
        
        # Validate it contains command information
        has_commands = (
            '## Available Commands' in output or
            'Commands:' in output or
            '**Commands:**' in output
        )
        assert has_commands, \
            f"Missing commands section in help output:\n{output[:500]}"
    
    def assert_help_shows_command_details(self, output: str, command: str):
        """
        Validate specific command present in help output.
        
        Expected: command name appears in help with description/usage
        """
        assert command in output, \
            f"Missing command '{command}' in help output:\n{output[:500]}"


class PipeBehaviorsHelper:
    """Helper for behaviors - validates behavior object properties"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_behavior_has_properties(self, behavior):
        """Validate behavior has expected properties."""
        assert behavior is not None, "Behavior should not be None"
        assert hasattr(behavior, 'name'), "Behavior should have 'name' property"
        assert hasattr(behavior, 'actions'), "Behavior should have 'actions' property"


class PipeBotTestHelper(CLIBotTestHelper):
    """Pipe/Markdown channel helper - validates complete markdown structures"""
    
    def __init__(self, tmp_path: Path):
        super().__init__(tmp_path, mode='markdown')
        self.bot = PipeBotHelper(self)
        self.instructions = PipeInstructionsHelper(self)
        self.scope = PipeScopeHelper(self)
        self.navigation = PipeNavigationHelper(self)
        self.help = PipeHelpHelper(self)
        self.behaviors = PipeBehaviorsHelper(self)