"""
Strategy Test Helper
Handles strategy action-specific methods and instruction assertions
"""
import json
from pathlib import Path
from helpers.base_helper import BaseHelper


class StrategyTestHelper(BaseHelper):
    """Helper for strategy action-specific testing"""
    
    def given_strategy_guardrails_in_workspace(self, behavior_name: str) -> Path:
        """Create strategy guardrails files in bot_directory with fixed sample template data.
        
        Guardrails are templates: typical assumptions available for selection.
        They do NOT contain chosen assumptions - those go in workspace clarification.json.
        
        Args:
            behavior_name: Behavior name (e.g., 'shape', 'discovery')
            
        Returns:
            Path to assumptions file
        """
        # Fixed sample strategy assumptions (available options - not chosen yet)
        sample_assumptions = [
            'Focus on user flow over internal systems',
            'Cover the end-to-end scenario from user perspective',
            'Prioritize customer-facing features in early increments'
        ]
        
        guardrails_dir = self.parent.bot_directory / 'behaviors' / behavior_name / 'guardrails' / 'strategy'
        guardrails_dir.mkdir(parents=True, exist_ok=True)
        
        assumptions_file = guardrails_dir / 'typical_assumptions.json'
        assumptions_file.write_text(json.dumps({'typical_assumptions': sample_assumptions}, indent=2), encoding='utf-8')
        
        return assumptions_file
    
    def assert_strategy_guardrails_loaded_correctly(self, guardrails):
        """Assert strategy guardrails contain expected assumptions.
        
        Uses same fixed sample data as given_strategy_guardrails_in_workspace.
        
        Args:
            guardrails: Guardrails object from behavior
        """
        # Expected data matches what given_strategy_guardrails_in_workspace creates
        expected_assumptions = [
            'Focus on user flow over internal systems',
            'Cover the end-to-end scenario from user perspective',
            'Prioritize customer-facing features in early increments'
        ]
        
        assert hasattr(guardrails, 'strategy'), "Guardrails should have strategy"
        strategy = guardrails.strategy
        assert hasattr(strategy, 'instructions'), "Strategy should have instructions"
        
        instructions = strategy.instructions
        assert 'assumptions' in instructions, "Instructions should contain assumptions"
        
        actual_assumptions = instructions['assumptions']
        
        assert len(actual_assumptions) == len(expected_assumptions), \
            f"Expected {len(expected_assumptions)} assumptions, got {len(actual_assumptions)}"
        
        for expected_a in expected_assumptions:
            assert expected_a in actual_assumptions, \
                f"Expected assumption '{expected_a}' not found in {actual_assumptions}"
    
    def assert_strategy_instructions(self, instructions):
        """Assert StrategyAction injected all required fields.
        
        Args:
            instructions: Instructions object from StrategyAction
        """
        # Check base instructions exist
        base_instructions = instructions.get('base_instructions', [])
        assert base_instructions, "base_instructions should be present"
        
        # Check StrategyAction-specific fields
        strategy_criteria = instructions.get('strategy_criteria')
        assert strategy_criteria is not None, "strategy_criteria should be set"
        assert isinstance(strategy_criteria, dict), "strategy_criteria should be a dict"
        
        # assumptions is a dict with 'typical_assumptions' and 'assumptions_made'
        assumptions = instructions.get('assumptions')
        assert assumptions is not None, "assumptions should be set"
        assert isinstance(assumptions, dict), "assumptions should be a dict"
        assert 'typical_assumptions' in assumptions, "assumptions should have 'typical_assumptions'"
    
    def get_strategy_file_path(self) -> Path:
        """Get path to strategy.json file in workspace.
        
        Returns:
            Path to strategy.json
        """
        from bot_path import BotPath
        bot_paths = BotPath(workspace_path=self.parent.workspace, bot_directory=self.parent.bot_directory)
        documentation_path = bot_paths.documentation_path
        return self.parent.workspace / documentation_path / 'strategy.json'
    
    def given_existing_strategy_data(self, data: dict) -> Path:
        """Create existing strategy.json file with data.
        
        Args:
            data: Dict containing strategy data (behavior sections)
            
        Returns:
            Path to created file
        """
        strategy_file = self.get_strategy_file_path()
        strategy_file.parent.mkdir(parents=True, exist_ok=True)
        strategy_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return strategy_file
    
    def assert_strategy_file_exists(self):
        """Assert strategy.json file exists."""
        strategy_file = self.get_strategy_file_path()
        assert strategy_file.exists(), f"strategy.json should exist at {strategy_file}"
    
    def assert_strategy_file_not_exists(self):
        """Assert strategy.json file does not exist."""
        strategy_file = self.get_strategy_file_path()
        assert not strategy_file.exists(), f"strategy.json should not exist at {strategy_file}"
    
    def assert_strategy_contains_behavior(self, behavior_name: str, expected_decisions: dict = None, expected_assumptions: list = None):
        """Assert strategy file contains behavior section with expected data.
        
        Args:
            behavior_name: Behavior name (e.g., 'shape', 'discovery')
            expected_decisions: Expected decisions dict (optional)
            expected_assumptions: Expected assumptions list (optional)
        
        Note: Actual save format is:
        {
          "behavior": {
            "decisions": {...},
            "assumptions": [...]
          }
        }
        """
        strategy_file = self.get_strategy_file_path()
        assert strategy_file.exists(), f"strategy.json should exist at {strategy_file}"
        
        strategy_data = json.loads(strategy_file.read_text(encoding='utf-8'))
        assert behavior_name in strategy_data, f"Behavior '{behavior_name}' should be in strategy data"
        
        behavior_data = strategy_data[behavior_name]
        
        if expected_decisions:
            # Actual format: behavior_data['decisions'] = {...}
            assert 'decisions' in behavior_data, "Behavior should have 'decisions'"
            for key, value in expected_decisions.items():
                assert behavior_data['decisions'][key] == value, \
                    f"Expected decision '{key}' = '{value}', got '{behavior_data['decisions'].get(key)}'"
        
        if expected_assumptions:
            # Actual format: behavior_data['assumptions'] = [...]
            assert 'assumptions' in behavior_data, "Behavior should have 'assumptions'"
            assert behavior_data['assumptions'] == expected_assumptions, \
                f"Expected assumptions = {expected_assumptions}, got {behavior_data['assumptions']}"