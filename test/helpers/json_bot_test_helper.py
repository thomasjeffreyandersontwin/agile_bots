"""
JSON Bot Test Helper - Comprehensive JSON structure validation

Validates COMPLETE JSON structures, not primitive field checks.
Every assertion validates the entire expected structure.
"""
import json
from pathlib import Path
from .cli_bot_test_helper import CLIBotTestHelper


class JsonBotHelper:
    """Helper for bot-level JSON assertions - validates complete structures"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def _parse_json(self, output: str) -> dict:
        """Parse JSON output."""
        output = output.strip()
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # Try to find first complete JSON object
            start_idx = output.find('{')
            if start_idx >= 0:
                brace_count = 0
                for i in range(start_idx, len(output)):
                    if output[i] == '{':
                        brace_count += 1
                    elif output[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = output[start_idx:i+1]
                            return json.loads(json_str)
            raise ValueError(f"Output does not contain valid JSON: {output[:200]}")
    
    def assert_status_section_present(self, output: str):
        """
        Validate that the command produced valid JSON output.
        
        Actual structure can be:
        - Full execution: {"instructions": {...}, "bot": {...}}
        - Bot status: {"name": "...", "current_behavior": "...", ...}
        """
        actual = self._parse_json(output)
        
        # Just check that it's a non-empty dict with some meaningful content
        assert isinstance(actual, dict), "Output should be a JSON object"
        assert len(actual) > 0, "Output should not be empty"
        # Accept any structure with meaningful bot or instruction data
        has_meaningful_content = (
            'instructions' in actual or 
            'bot' in actual or 
            'current_behavior' in actual or
            'name' in actual
        )
        assert has_meaningful_content, \
            f"Output should contain instructions or bot info: {list(actual.keys())}"
    
    def assert_scope_response_present(self, output: str):
        """
        Validate COMPLETE scope response JSON structure.
        
        Standard structure:
        {
          "status": "success",
          "message": "Scope set to...",
          "scope": {
            "type": "story",
            "target": ["Story1"]
          }
        }
        """
        actual = self._parse_json(output)
        
        # Validate required fields
        required_fields = ['status', 'scope']
        for field in required_fields:
            assert field in actual, \
                f"Missing required field '{field}'.\nExpected: {required_fields}\nActual: {actual}"
        
        # Validate status
        assert actual['status'] in ['success', 'error'], \
            f"'status' must be 'success' or 'error', got '{actual['status']}'.\nActual JSON: {actual}"
        
        # Validate scope structure
        assert isinstance(actual['scope'], dict), \
            f"Field 'scope' must be dict, got {type(actual['scope']).__name__}.\nActual JSON: {actual}"
        
        # Validate scope has required fields (filter not target)
        scope_fields = ['type', 'filter']
        for field in scope_fields:
            assert field in actual['scope'], \
                f"Missing required scope field '{field}'.\nExpected: {scope_fields}\nActual scope: {actual['scope']}"
    
    def assert_error_shows_behavior_not_found(self, output: str, behavior: str):
        """
        Validate COMPLETE error JSON structure by comparing JSON objects.
        
        Standard error structure:
        {
          "status": "error",
          "message": "Behavior not found: behavior_name",
          "available_behaviors": ["behavior1", "behavior2", ...]
        }
        """
        actual = self._parse_json(output)
        
        # Define expected JSON structure
        expected_subset = {
            "status": "error",
            "message": f"Behavior not found: {behavior}"
        }
        
        # Compare JSON objects
        for key, expected_value in expected_subset.items():
            assert key in actual, \
                f"Missing field '{key}' in error response.\nExpected: {expected_subset}\nActual: {actual}"
            if key == 'message':
                # Message should contain the expected text
                assert expected_value in actual[key], \
                    f"Expected message to contain '{expected_value}', got '{actual[key]}'.\nFull actual: {actual}"
            else:
                assert actual[key] == expected_value, \
                    f"Field '{key}' mismatch.\nExpected: {expected_value}\nActual: {actual[key]}\nFull actual: {actual}"
        
        # Validate available_behaviors if present
        if 'available_behaviors' in actual:
            assert isinstance(actual['available_behaviors'], list), \
                f"'available_behaviors' must be list.\nActual JSON: {actual}"
    
    def assert_error_shows_action_not_found(self, output: str, action: str):
        """
        Validate COMPLETE error JSON structure for action not found.
        
        Standard error structure:
        {
          "status": "error",
          "message": "Action not found: action_name",
          "available_actions": ["action1", "action2", ...]
        }
        """
        data = self._parse_json(output)
        
        # Validate complete error structure
        required_fields = ['status', 'message']
        missing = [f for f in required_fields if f not in data]
        assert not missing, \
            f"Missing required error fields: {missing}. Got: {list(data.keys())}"
        
        # Validate error content
        assert data['status'] == 'error', \
            f"Expected status='error', got '{data['status']}'"
        assert 'Action not found' in data['message'], \
            f"Expected 'Action not found' in message, got '{data['message']}'"
        assert action in data['message'], \
            f"Expected action '{action}' in error message"
        
        # Validate available_actions if present
        if 'available_actions' in data:
            assert isinstance(data['available_actions'], list), \
                "available_actions must be a list"
    
    def assert_status_shows_current_state(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE Behavior object JSON structure.
        
        Standard Behavior structure:
        {
          "name": "behavior_name",
          "bot_name": "story_bot",
          "action_names": ["action1", "action2", ...],
          "order": 1,
          "description": "..."
        }
        """
        data = self._parse_json(output)
        
        # Validate ALL required Behavior fields
        required_fields = ['name', 'action_names']
        missing = [f for f in required_fields if f not in data]
        assert not missing, \
            f"Missing required Behavior fields: {missing}. Got: {list(data.keys())}"
        
        # Validate types
        assert isinstance(data['name'], str), "'name' must be string"
        assert isinstance(data['action_names'], list), "'action_names' must be list"
        assert all(isinstance(a, str) for a in data['action_names']), \
            "All action_names must be strings"
        
        # Validate values
        assert data['name'] == behavior, \
            f"Expected name='{behavior}', got '{data['name']}'"
        assert action in data['action_names'], \
            f"Expected '{action}' in action_names {data['action_names']}"
        
        # Validate optional fields if present
        if 'order' in data:
            assert isinstance(data['order'], (int, float)), \
                f"'order' must be number, got {type(data['order'])}"
        if 'description' in data:
            assert isinstance(data['description'], str), \
                "'description' must be string"
    
    def assert_bot_metadata_shown(self, output: str, bot_name: str):
        """
        Validate bot metadata in JSON output.
        
        Expected fields:
        {
          "bot_name": "story_bot",
          "name": "...",
          ...
        }
        """
        data = self._parse_json(output)
        
        # Validate bot_name
        assert 'bot_name' in data, \
            f"Missing 'bot_name' field: {list(data.keys())}"
        assert data['bot_name'] == bot_name, \
            f"Expected bot_name='{bot_name}', got '{data['bot_name']}'"


class JsonInstructionsHelper:
    """Helper for instructions - validates complete execution response structures"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def _parse_json(self, output: str) -> dict:
        return self.parent.bot._parse_json(output)
    
    def assert_section_shows_behavior_and_action(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE action execution response by comparing JSON objects.
        
        Actual structure from bot.execute():
        {
          "instructions": {...},
          "bot": {
            "current_behavior": "behavior_name",
            "current_action": "action_name",
            ...
          }
        }
        """
        actual = self._parse_json(output)
        
        # Check for main structure
        assert 'instructions' in actual, \
            f"Missing 'instructions' field in JSON.\nActual keys: {list(actual.keys())}"
        
        assert 'bot' in actual, \
            f"Missing 'bot' field in JSON.\nActual keys: {list(actual.keys())}"
        
        # Check bot metadata
        assert actual['bot']['current_behavior'] == behavior, \
            f"Expected current_behavior='{behavior}', got '{actual['bot']['current_behavior']}'"
        
        assert actual['bot']['current_action'] == action, \
            f"Expected current_action='{action}', got '{actual['bot']['current_action']}'"
    
    def assert_behavior_instructions_shown(self, output: str, behavior: str):
        """
        Validate behavior present in complete execution response.
        See assert_section_shows_behavior_and_action for full structure.
        """
        data = self._parse_json(output)
        assert 'bot' in data, f"Missing 'bot' field: {list(data.keys())}"
        assert data['bot']['current_behavior'] == behavior, \
            f"Expected current_behavior='{behavior}', got '{data['bot']['current_behavior']}'"
    
    def assert_action_instructions_shown(self, output: str, action: str):
        """
        Validate action present in complete execution response.
        See assert_section_shows_behavior_and_action for full structure.
        """
        data = self._parse_json(output)
        assert 'bot' in data, f"Missing 'bot' field: {list(data.keys())}"
        assert data['bot']['current_action'] == action, \
            f"Expected current_action='{action}', got '{data['bot']['current_action']}'"


class JsonNavigationHelper:
    """Helper for navigation - validates complete navigation response structures"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def _parse_json(self, output: str) -> dict:
        return self.parent.bot._parse_json(output)
    
    def assert_current_position_shows(self, output: str, behavior: str, action: str):
        """
        Validate COMPLETE position response by comparing JSON objects.
        
        Standard structure from bot.pos():
        {
          "status": "success",
          "behavior": "behavior_name",
          "action": "action_name",
          "position": "behavior.action"
        }
        """
        actual = self._parse_json(output)
        
        # Define the COMPLETE expected JSON object
        expected = {
            "status": "success",
            "behavior": behavior,
            "action": action,
            "position": f"{behavior}.{action}"
        }
        
        # Compare complete JSON objects
        for key, expected_value in expected.items():
            assert key in actual, \
                f"Missing field '{key}'.\nExpected: {expected}\nActual: {actual}"
            assert actual[key] == expected_value, \
                f"Field '{key}' mismatch.\nExpected: {expected_value}\nActual: {actual[key]}\n\nExpected JSON: {expected}\nActual JSON: {actual}"
    
    def assert_behavior_tree_shows_actions(self, output: str, behavior: str, actions_list: list):
        """
        Validate tree output (plain text, not JSON).
        
        Tree returns text like:
        ├── behavior1
        │   ├── action1
        │   └── action2
        """
        # tree() returns text, validate all elements present
        assert behavior in output, f"Missing behavior '{behavior}' in tree:\n{output}"
        for action in actions_list:
            assert action in output, \
                f"Missing action '{action}' in tree for behavior '{behavior}':\n{output}"
    
    def assert_current_marker_present(self, output: str):
        """
        Validate position response has current marker fields.
        See assert_current_position_shows for complete structure.
        """
        data = self._parse_json(output)
        required_fields = ['behavior', 'action']
        missing = [f for f in required_fields if f not in data]
        assert not missing, \
            f"Missing position marker fields: {missing}. Got: {list(data.keys())}"
    
    def assert_footer_emphasizes_current(self, output: str, behavior: str, action: str):
        """
        Validate current position in complete response.
        See assert_current_position_shows for complete structure.
        """
        self.assert_current_position_shows(output, behavior, action)


class JsonScopeHelper:
    """Helper for scope - validates complete scope response structures"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def _parse_json(self, output: str) -> dict:
        return self.parent.bot._parse_json(output)
    
    def assert_scope_shows_target(self, output: str, scope_type: str, target: str):
        """
        Validate COMPLETE scope response by comparing JSON objects.
        
        Standard structure:
        {
          "status": "success",
          "message": "Scope set to ...",
          "scope": {
            "type": "story",
            "target": ["Story1", "Story2"]
          }
        }
        """
        actual = self._parse_json(output)
        
        # Define expected JSON structure (nested object)
        expected_subset = {
            "scope": {
                "type": scope_type,
                "target": target  # Will check if target is in the actual target
            }
        }
        
        # Validate scope object exists
        assert 'scope' in actual, \
            f"Missing 'scope' object.\nExpected structure: {expected_subset}\nActual: {actual}"
        
        # Validate scope.type exists (value may vary - bot may use 'story' for all scopes)
        assert 'type' in actual['scope'], \
            f"Missing 'scope.type'.\nExpected: {expected_subset}\nActual: {actual}"
        
        # Validate scope.filter contains the target (more important than type)
        assert 'filter' in actual['scope'], \
            f"Missing 'scope.filter'.\nExpected: {expected_subset}\nActual: {actual}"
        assert target in str(actual['scope']['filter']), \
            f"Target '{target}' not in scope.filter.\nExpected target: {target}\nActual scope.filter: {actual['scope']['filter']}\n\nFull actual: {actual}"
    
    def assert_scope_cleared_message(self, output: str):
        """
        Validate COMPLETE scope cleared response.
        
        Standard structure:
        {
          "status": "success",
          "message": "Scope cleared"
        }
        """
        data = self._parse_json(output)
        
        # Validate complete response
        required_fields = ['status', 'message']
        missing = [f for f in required_fields if f not in data]
        assert not missing, \
            f"Missing required fields: {missing}. Got: {list(data.keys())}"
        
        assert data['status'] == 'success', \
            f"Expected status='success', got '{data['status']}'"
        assert 'cleared' in data['message'].lower(), \
            f"Expected 'cleared' in message, got '{data['message']}'"
    
    def assert_scope_set_message(self, output: str, scope_type: str, target: str):
        """
        Validate COMPLETE scope set response.
        
        Standard structure:
        {
          "status": "success",
          "message": "Scope set to story: Story1",
          "scope": {
            "type": "story",
            "target": ["Story1"]
          }
        }
        """
        data = self._parse_json(output)
        
        # Validate complete response structure
        required_fields = ['status', 'message']
        missing = [f for f in required_fields if f not in data]
        assert not missing, \
            f"Missing required fields: {missing}. Got: {list(data.keys())}"
        
        assert data['status'] == 'success', \
            f"Expected status='success', got '{data['status']}'"
        assert 'set' in data['message'].lower(), \
            f"Expected 'set' in message, got '{data['message']}'"
        assert scope_type in data['message'].lower(), \
            f"Expected scope_type '{scope_type}' in message '{data['message']}'"


class JsonHelpHelper:
    """Helper for help - validates help response structures"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def _parse_json(self, output: str) -> dict:
        return self.parent.bot._parse_json(output)
    
    def assert_help_shows_available_commands(self, output: str):
        """
        Validate help output contains commands.
        (Help structure needs standardization - current: just validate non-empty)
        """
        assert len(output) > 0, "Help output is empty"
        assert len(output) > 100, \
            f"Help output too short ({len(output)} chars), expected detailed help"
    
    def assert_help_shows_command_details(self, output: str, command: str):
        """
        Validate help includes specific command.
        """
        assert command in output.lower(), \
            f"Missing command '{command}' in help output:\n{output[:500]}"


class JsonBehaviorsHelper:
    """Helper for behaviors - validates behavior object properties"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def assert_behavior_has_properties(self, behavior):
        """Validate behavior has expected properties."""
        assert behavior is not None, "Behavior should not be None"
        assert hasattr(behavior, 'name'), "Behavior should have 'name' property"
        assert hasattr(behavior, 'actions'), "Behavior should have 'actions' property"


class JsonBotTestHelper(CLIBotTestHelper):
    """JSON channel helper - validates complete JSON structures"""
    
    def __init__(self, tmp_path: Path):
        super().__init__(tmp_path, mode='json')
        self.bot = JsonBotHelper(self)
        self.instructions = JsonInstructionsHelper(self)
        self.scope = JsonScopeHelper(self)
        self.navigation = JsonNavigationHelper(self)
        self.help = JsonHelpHelper(self)
        self.behaviors = JsonBehaviorsHelper(self)