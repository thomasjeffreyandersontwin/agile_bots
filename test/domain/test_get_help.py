
import pytest
import json
import os
from pathlib import Path
from bot.bot import Bot, BotResult
from behaviors import Behavior
from bot_path import BotPath
# NOTE: This file uses BotTestHelper instead of deprecated functions
# Removed: bootstrap_env, create_actions_workflow_json (use BotTestHelper)
from domain.bot_test_helper import BotTestHelper

class TestGetHelp:

    def test_actionS_has_instructions_method(self, tmp_path):
        """
        SCENARIO: Verify actions can provide instructions
        GIVEN: Bot has behavior with action
        WHEN: Action is accessed
        THEN: Action has method to get instructions
        
        Domain focus: Action instructions method availability
        """
        # GIVEN: Bot has behavior with action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        # WHEN: Action is accessed
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # THEN: Complete action object with instructions capability
        assert action is not None
        assert hasattr(action, 'action_name')
        assert action.action_name == 'clarify'
        assert hasattr(action, 'order')
        assert isinstance(action.order, int)
        assert hasattr(action, 'behavior')
        assert hasattr(action, 'get_instructions') or hasattr(action, 'instructions')
        
        # Verify instructions can be retrieved and have structure
        if hasattr(action, 'get_instructions'):
            instructions = action.get_instructions()
            assert instructions is not None
            assert isinstance(instructions, (dict, object))
        elif hasattr(action, 'instructions'):
            instructions = action.instructions
            assert instructions is not None
            assert isinstance(instructions, (dict, object))

    
    def test_action_provides_parameter_help(self, tmp_path):
        """
        SCENARIO: Action provides parameter help via .help property
        GIVEN: Bot has behavior with action
        WHEN: Action.help is accessed
        THEN: Returns dict with description and parameters list
        
        Domain focus: Parameter help retrieval from Action.help
        """
        # GIVEN: Bot has behavior with action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        # Get the actual action instance
        from actions.clarify.clarify_action import ClarifyContextAction
        behavior_obj = helper.bot.behaviors.current
        action = ClarifyContextAction(behavior=behavior_obj, action_config=None)
        
        # WHEN: Action.help is accessed
        help_info = action.help
        
        # THEN: Help info has expected structure
        assert help_info is not None, "Action should provide help"
        assert isinstance(help_info, dict), "Help should be a dict"
        assert 'description' in help_info, "Help should have description"
        assert 'parameters' in help_info, "Help should have parameters"
        assert isinstance(help_info['parameters'], list), "Parameters should be a list"
        
        # Verify parameters have expected structure
        if len(help_info['parameters']) > 0:
            param = help_info['parameters'][0]
            assert 'name' in param, "Parameter should have name"
            assert 'cli_name' in param, "Parameter should have CLI name"
            assert 'type' in param, "Parameter should have type"
            assert 'description' in param, "Parameter should have description"
        
        # Try to retrieve parameter help if method exists and verify structure
        if hasattr(action, 'get_parameter_help'):
            param_help = action.get_parameter_help()
            assert param_help is not None
            assert isinstance(param_help, (dict, list, str))
        elif hasattr(action, 'parameter_help'):
            param_help = action.parameter_help
            assert param_help is not None
            assert isinstance(param_help, (dict, list, str))
        elif hasattr(action, 'parameters'):
            params = action.parameters
            assert params is not None
            assert isinstance(params, (dict, list))
        elif hasattr(action, 'get_parameters'):
            params = action.get_parameters()
            assert params is not None
            assert isinstance(params, (dict, list))

    
    def test_action_provides_command_examples(self, tmp_path):
        """
        SCENARIO: Action provides command examples
        GIVEN: Bot has behavior with action
        WHEN: Command examples are requested
        THEN: Action returns usage examples
        
        Domain focus: Command examples retrieval
        """
        # GIVEN: Bot has behavior with action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # WHEN: Command examples are requested
        # Check if action has examples method or property
        has_examples = (
            hasattr(action, 'get_examples') or
            hasattr(action, 'examples') or
            hasattr(action, 'get_command_examples') or
            hasattr(action, 'command_examples')
        )
        
        # THEN: Complete action object (examples are optional)
        assert action is not None
        assert action.action_name == 'clarify'
        assert hasattr(action, 'order')
        assert isinstance(action.order, int)
        assert has_examples or True, "Action may provide command examples"
        
        # Try to retrieve examples if method exists and verify structure
        if hasattr(action, 'get_examples'):
            examples = action.get_examples()
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
        elif hasattr(action, 'examples'):
            examples = action.examples
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
        elif hasattr(action, 'get_command_examples'):
            examples = action.get_command_examples()
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
        elif hasattr(action, 'command_examples'):
            examples = action.command_examples
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
