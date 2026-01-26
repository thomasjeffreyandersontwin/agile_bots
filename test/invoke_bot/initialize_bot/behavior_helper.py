"""
Behavior Test Helper
Handles all behavior and action management, workflows, verification
"""
import json
from pathlib import Path
from helpers.base_helper import BaseHelper


def _setup_build_action_prerequisites(bot_directory: Path, behavior: str = 'exploration'):
    """Set up directory structure and config files needed for build action tests.
    
    Creates the knowledge graph directory structure and basic config/template files
    that BuildAction expects to find.
    
    Args:
        bot_directory: Path to bot directory
        behavior: Name of the behavior (default: 'exploration')
    
    Returns:
        Path to the knowledge graph directory
    """
    # Create knowledge graph directory structure
    kg_dir = bot_directory / 'behaviors' / behavior / 'knowledge_graph'
    kg_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a minimal config file
    config_file = kg_dir / 'story_graph_config.json'
    config_data = {
        'template': 'story_graph_template.md',
        'output_path': 'docs/stories'
    }
    config_file.write_text(json.dumps(config_data, indent=2), encoding='utf-8')
    
    # Create a minimal template file
    template_file = kg_dir / 'story_graph_template.md'
    template_file.write_text('# Story Graph Template\n\n{{content}}', encoding='utf-8')
    
    return kg_dir


class BehaviorTestHelper(BaseHelper):
    """Helper for behavior and action management, workflows, and verification"""
    
    def create_base_action_instructions(self, action: str) -> Path:
        """Get base action config path for specific action.
        
        Args:
            action: Action name
        
        Returns:
            Path to action_config.json file
        
        Raises:
            RuntimeError: If base action folder or config doesn't exist
        """
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        base_actions_dir = repo_root / 'agile_bots' / 'base_actions'
        action_dir = base_actions_dir / action
        if not action_dir.exists():
            raise RuntimeError(f"Base action folder missing: {action_dir}. Tests should rely on existing base actions.")
        config_file = action_dir / 'action_config.json'
        if not config_file.exists():
            raise RuntimeError(f"Base action config missing: {config_file}. Tests should rely on existing base actions.")
        return config_file
    
    def assert_at_behavior_action(self, behavior_name: str, action_name: str):
        """Assert bot is at specified behavior and action."""
        assert self.parent.bot.behaviors.current.name == behavior_name
        assert self.parent.bot.behaviors.current.actions.current_action_name == action_name
    
    def assert_shape_behavior_structure(self):
        """
        Assert shape behavior is loaded with correct complete structure.
        
        Shape has exactly 5 actions in specific order with specific configurations.
        """
        shape = self.parent.bot.behaviors.find_by_name('shape')
        assert shape is not None, "Shape behavior not found"
        assert shape.name == 'shape'
        assert isinstance(shape.order, (int, float))
        assert isinstance(shape.description, str) and len(shape.description) > 0
        
        # Assert exact action count and names
        action_names = shape.actions.names
        assert len(action_names) == 5, f"Expected 5 actions, got {len(action_names)}: {action_names}"
        assert action_names == ['clarify', 'strategy', 'build', 'validate', 'render'], \
            f"Expected ['clarify', 'strategy', 'build', 'validate', 'render'], got {action_names}"
    
    def assert_discovery_behavior_structure(self):
        """
        Assert discovery behavior is loaded with correct complete structure.
        
        Discovery has exactly 5 actions in specific order.
        """
        discovery = self.parent.bot.behaviors.find_by_name('discovery')
        assert discovery is not None, "Discovery behavior not found"
        assert discovery.name == 'discovery'
        assert isinstance(discovery.order, (int, float))
        
        # Assert exact action count and names
        action_names = discovery.actions.names
        assert len(action_names) == 5, f"Expected 5 actions, got {len(action_names)}: {action_names}"
        assert action_names == ['clarify', 'strategy', 'build', 'validate', 'render'], \
            f"Expected ['clarify', 'strategy', 'build', 'validate', 'render'], got {action_names}"
    
    def assert_current_behavior_and_action(self, behavior: str, action: str):
        """
        Assert bot is at specific behavior and action - comprehensive check.
        
        Checks both bot's current state AND state file for consistency.
        """
        # Check bot's in-memory state
        assert self.parent.bot.behaviors.current is not None, "No current behavior set"
        assert self.parent.bot.behaviors.current.name == behavior, \
            f"Expected current behavior '{behavior}', got '{self.parent.bot.behaviors.current.name}'"
        
        assert self.parent.bot.behaviors.current.actions.current is not None, "No current action set"
        assert self.parent.bot.behaviors.current.actions.current.action_name == action, \
            f"Expected current action '{action}', got '{self.parent.bot.behaviors.current.actions.current.action_name}'"
        
        # Check state file matches
        state = self.parent.state.get_state()
        if state:  # Only check if state file exists
            assert state['current_behavior'] == f'story_bot.{behavior}', \
                f"State file current_behavior mismatch: expected 'story_bot.{behavior}', got '{state['current_behavior']}'"
            assert f'story_bot.{behavior}.{action}' in state['current_action'], \
                f"State file current_action mismatch: expected to contain 'story_bot.{behavior}.{action}', got '{state['current_action']}'"
    
    def assert_bot_result_success(self, result, behavior: str, action: str):
        """
        Assert bot execute result has complete success structure.
        
        bot.execute() returns Instructions object with instruction data.
        Validates that instructions were returned successfully.
        """
        # Assert result exists and has instruction data
        assert result is not None, "Result should not be None"
        
        # Instructions are returned as Instructions object or dict
        from instructions.instructions import Instructions
        if isinstance(result, Instructions):
            # Instructions object has _data attribute
            assert hasattr(result, '_data'), \
                f"Expected Instructions object to have '_data' attribute"
        elif isinstance(result, dict):
            # Dict should have instruction data
            assert len(result) > 0, "Expected non-empty dict"
        else:
            raise AssertionError(f"Expected Instructions or dict, got {type(result)}")
        
        # Verify bot is at correct behavior/action
        assert self.parent.bot.behaviors.current.name == behavior, \
            f"Expected behavior '{behavior}', got '{self.parent.bot.behaviors.current.name}'"
        
        assert self.parent.bot.behaviors.current.actions.current_action_name == action, \
            f"Expected action '{action}', got '{self.parent.bot.behaviors.current.actions.current_action_name}'"
    
    def assert_bot_result_error_behavior_not_found(self, result: dict, behavior: str):
        """Assert bot execute result shows behavior not found error."""
        assert result['status'] == 'error', f"Expected status='error', got '{result['status']}'"
        assert result['message'] == f'Behavior not found: {behavior}', \
            f"Expected message='Behavior not found: {behavior}', got '{result['message']}'"
        assert 'available_behaviors' in result, "Missing 'available_behaviors' key"
        assert isinstance(result['available_behaviors'], list), \
            "available_behaviors should be a list"
    
    def assert_bot_result_error_action_not_found(self, result: dict, action: str):
        """Assert bot execute result shows action not found error."""
        assert result['status'] == 'error', f"Expected status='error', got '{result['status']}'"
        assert result['message'] == f'Action not found: {action}', \
            f"Expected message='Action not found: {action}', got '{result['message']}'"
        assert 'available_actions' in result, "Missing 'available_actions' key"
        assert isinstance(result['available_actions'], list), \
            "available_actions should be a list"
    
    def assert_bot_result_error_no_actions(self, result: dict, behavior: str):
        """Assert bot execute result shows no actions error."""
        assert result['status'] == 'error', f"Expected status='error', got '{result['status']}'"
        assert result['message'] == f'Behavior {behavior} has no actions', \
            f"Expected message='Behavior {behavior} has no actions', got '{result['message']}'"
    
    def assert_behavior_complete_structure(self, behavior, expected_name: str, expected_order: int, 
                                           expected_actions: list, expected_description: str = None):
        """
        Assert behavior has complete structure with ALL properties validated.
        
        This is a comprehensive check that validates:
        - name (exact match)
        - order (exact value)
        - description (non-empty string)
        - goal (non-empty string)
        - inputs (correct type)
        - outputs (correct type)
        - trigger_words (exists and has patterns)
        - actions (exact list, exact order, exact count)
        
        Args:
            behavior: The behavior object to check
            expected_name: Expected behavior name (exact match)
            expected_order: Expected order number (exact match)
            expected_actions: Expected list of action names (exact match, exact order)
            expected_description: Optional expected description (exact match)
        """
        assert behavior is not None, f"Behavior '{expected_name}' not found"
        assert behavior.name == expected_name, \
            f"Expected name='{expected_name}', got '{behavior.name}'"
        assert behavior.order == expected_order, \
            f"Expected order={expected_order}, got {behavior.order}"
        assert isinstance(behavior.description, str) and len(behavior.description) > 0, \
            f"Expected non-empty description string, got {type(behavior.description).__name__}: {behavior.description}"
        
        if expected_description:
            assert behavior.description == expected_description, \
                f"Expected description='{expected_description}', got '{behavior.description}'"
        
        # Goal, inputs, and outputs are optional (can be empty strings or lists)
        assert isinstance(behavior.goal, str), \
            f"Expected goal to be string, got {type(behavior.goal).__name__}: {behavior.goal}"
        assert isinstance(behavior.inputs, (str, list)), \
            f"Expected inputs to be string or list, got {type(behavior.inputs).__name__}"
        assert isinstance(behavior.outputs, (str, list)), \
            f"Expected outputs to be string or list, got {type(behavior.outputs).__name__}"
        
        # Check trigger words
        assert hasattr(behavior, 'trigger_words') and behavior.trigger_words is not None, \
            "Expected trigger_words to exist"
        
        # Check actions - exact list, exact order, exact count
        action_names = behavior.actions.names
        assert len(action_names) == len(expected_actions), \
            f"Expected {len(expected_actions)} actions, got {len(action_names)}: {action_names}"
        assert action_names == expected_actions, \
            f"Expected actions {expected_actions}, got {action_names}"
    
    def assert_actions_complete_structure(self, actions, expected_actions: list):
        """
        Assert actions collection has complete structure with ALL action properties validated.
        
        This is a comprehensive check that validates:
        - Exact action count
        - Exact action names (in order)
        - Each action's properties (order, next_action, name, description)
        
        Args:
            actions: The actions collection to check
            expected_actions: List of dicts with expected action properties:
                [
                    {"name": "clarify", "order": 1, "next_action": "strategy"},
                    {"name": "strategy", "order": 2, "next_action": "build"},
                    ...
                ]
        """
        # Get actual action names
        action_names = actions.names
        expected_names = [a['name'] for a in expected_actions]
        
        # Assert exact count
        assert len(action_names) == len(expected_names), \
            f"Expected {len(expected_names)} actions, got {len(action_names)}: {action_names}"
        
        # Assert exact names in exact order
        assert action_names == expected_names, \
            f"Expected actions {expected_names}, got {action_names}"
        
        # Assert each action has correct properties
        for expected_action in expected_actions:
            action_name = expected_action['name']
            action = actions.find_by_name(action_name)
            
            assert action is not None, f"Action '{action_name}' not found"
            assert action.action_name == action_name, \
                f"Expected action_name='{action_name}', got '{action.action_name}'"
            
            # Check order
            expected_order = expected_action.get('order')
            if expected_order is not None:
                assert action.order == expected_order, \
                    f"Action '{action_name}': expected order={expected_order}, got {action.order}"
            
            # Check next_action
            expected_next = expected_action.get('next_action')
            if expected_next is not None:
                assert action.next_action == expected_next, \
                    f"Action '{action_name}': expected next_action='{expected_next}', got '{action.next_action}'"
            elif 'next_action' in expected_action and expected_next is None:
                # Explicitly expecting None
                assert action.next_action is None, \
                    f"Action '{action_name}': expected next_action=None, got '{action.next_action}'"
            
            # Check description exists
            assert isinstance(action.description, str), \
                f"Action '{action_name}': expected description to be string, got {type(action.description).__name__}"
            
            # Check workflow property (should always be True for workflow actions)
            assert hasattr(action, 'workflow'), \
                f"Action '{action_name}': missing workflow property"
    
    def verify_action_tracks_start(self, action_class, action_name: str, 
                                   behavior: str = 'exploration'):
        """Verify that action tracks start in activity log."""
        from types import SimpleNamespace
        
        # Create activity log file
        self.parent.activity.create_activity_log_file()
        
        # If action is 'build', create story graph config structure
        if action_name == 'build':
            from domain.test_build_knowledge import given_setup
            kg_dir = given_setup('directory_structure', self.parent.bot_directory, behavior=behavior)
            given_setup('config_and_template', self.parent.bot_directory, kg_dir=kg_dir)
        
        # Create mock behavior object
        class MockBotPath:
            def __init__(self, bot_dir, workspace_dir):
                self.bot_directory = bot_dir
                self.workspace_directory = workspace_dir
                self.documentation_path = workspace_dir / 'docs'
        
        behavior_folder = self.parent.bot_directory / 'behaviors' / behavior
        behavior_obj = SimpleNamespace()
        behavior_obj.folder = behavior_folder
        behavior_obj.name = behavior
        behavior_obj.bot_name = 'story_bot'
        behavior_obj.bot_paths = MockBotPath(self.parent.bot_directory, self.parent.workspace)
        behavior_obj.bot = None
        
        # Create action
        action = action_class(
            behavior=behavior_obj,
            action_config=None
        )
        action.track_activity_on_start()
        
        # Verify in activity log
        log_data = self.parent.activity.get_activity_log()
        assert any(
            e.get('action_state') == f'story_bot.{behavior}.{action_name}'
            for e in log_data
        ), f"Action start not found in activity log: {log_data}"
    
    def verify_action_tracks_completion(self, action_class, action_name: str,
                                       behavior: str = 'exploration',
                                       outputs: dict = None, duration: int = None):
        """Verify that action tracks completion in activity log."""
        from types import SimpleNamespace
        
        # Create activity log file
        self.parent.activity.create_activity_log_file()
        
        # If action is 'build', create story graph config structure
        if action_name == 'build':
            _setup_build_action_prerequisites(self.parent.bot_directory, behavior=behavior)
        
        # Create mock behavior object
        class MockBotPath:
            def __init__(self, bot_dir, workspace_dir):
                self.bot_directory = bot_dir
                self.workspace_directory = workspace_dir
                self.documentation_path = workspace_dir / 'docs'
        
        behavior_folder = self.parent.bot_directory / 'behaviors' / behavior
        behavior_obj = SimpleNamespace()
        behavior_obj.folder = behavior_folder
        behavior_obj.name = behavior
        behavior_obj.bot_name = 'story_bot'
        behavior_obj.bot_paths = MockBotPath(self.parent.bot_directory, self.parent.workspace)
        behavior_obj.bot = None
        
        # Create action
        action = action_class(
            behavior=behavior_obj,
            action_config=None
        )
        action.track_activity_on_completion(
            outputs=outputs or {},
            duration=duration
        )
        
        # Verify in activity log
        log_data = self.parent.activity.get_activity_log()
        completion_entry = next((e for e in log_data if 'outputs' in e or 'duration' in e), None)
        assert completion_entry is not None, f"No completion entry found in activity log: {log_data}"
        if outputs:
            assert completion_entry.get('outputs') == outputs, \
                f"Expected outputs {outputs}, got {completion_entry.get('outputs')}"
        if duration:
            assert completion_entry.get('duration') == duration, \
                f"Expected duration {duration}, got {completion_entry.get('duration')}"
    
    def verify_workflow_transition(self, source_action: str, dest_action: str,
                                   behavior: str = 'exploration'):
        """Verify workflow transitions from source to dest action.
        
        NOTE: This method uses production story_bot behaviors. It does not create
        custom behavior.json files. If you need custom workflows, use production
        behaviors or create test behaviors in temporary directories.
        """
        from bot.bot import Bot
        
        # Use production behaviors - no need to create behavior.json files
        # Production story_bot already has all behaviors configured
        
        # If build action is involved, create story graph config structure
        if source_action == 'build' or dest_action == 'build':
            from domain.test_build_knowledge import given_setup
            kg_dir = given_setup('directory_structure', self.parent.bot_directory, behavior=behavior)
            given_setup('config_and_template', self.parent.bot_directory, kg_dir=kg_dir)
        
        # Reload bot to get updated behavior
        config_path = self.parent.bot_directory / 'bot_config.json'
        # Pass workspace_path explicitly so tests use temp workspace, not production
        bot = Bot(
            bot_name='story_bot', 
            bot_directory=self.parent.bot_directory, 
            config_path=config_path,
            workspace_path=self.parent.workspace
        )
        
        # Navigate to behavior and action
        behavior_obj = bot.behaviors.find_by_name(behavior)
        behavior_obj.actions.navigate_to(source_action)
        
        # Close current action (this should transition to next)
        behavior_obj.actions.close_current()
        
        # Verify current action is now dest_action
        current_action = behavior_obj.actions.current
        assert current_action is not None, f"Expected current action after transition, got None"
        assert current_action.action_name == dest_action, \
            f"Expected action '{dest_action}', got '{current_action.action_name}'"
    
    def verify_workflow_saves_completed_action(self, action_name: str,
                                               behavior: str = 'exploration'):
        """Verify workflow saves completed action to behavior_action_state.json.
        
        NOTE: This method uses production story_bot behaviors. It does not create
        custom behavior.json files. If you need custom workflows, use production
        behaviors or create test behaviors in temporary directories.
        """
        from bot.bot import Bot
        
        # Use production behaviors - no need to create behavior.json files
        # Production story_bot already has all behaviors configured
        
        # If behavior has 'build' action, create story graph configs
        if action_name == 'build':
            from domain.test_build_knowledge import given_setup
            kg_dir = given_setup('directory_structure', self.parent.bot_directory, behavior=behavior)
            given_setup('config_and_template', self.parent.bot_directory, kg_dir=kg_dir)
        
        # Reload bot to get updated behavior
        config_path = self.parent.bot_directory / 'bot_config.json'
        # Pass workspace_path explicitly so tests use temp workspace, not production
        bot = Bot(
            bot_name='story_bot', 
            bot_directory=self.parent.bot_directory, 
            config_path=config_path,
            workspace_path=self.parent.workspace
        )
        
        # Navigate to action and close it (this saves it as completed)
        behavior_obj = bot.behaviors.find_by_name(behavior)
        assert behavior_obj is not None, \
            f"Behavior '{behavior}' not found in bot. Available behaviors: {[b.name for b in bot.behaviors]}"
        behavior_obj.actions.navigate_to(action_name)
        behavior_obj.actions.close_current()
        
        # Verify completed action is saved in behavior_action_state.json
        state_file = self.parent.workspace / 'behavior_action_state.json'
        assert state_file.exists(), f"State file {state_file} should exist"
        state_data = json.loads(state_file.read_text(encoding='utf-8'))
        
        action_state = f'story_bot.{behavior}.{action_name}'
        completed_actions = state_data.get('completed_actions', [])
        assert any(
            entry.get('action_state') == action_state
            for entry in completed_actions
        ), f"Action {action_state} should be in completed_actions: {completed_actions}"
    
