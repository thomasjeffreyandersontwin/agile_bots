"""
State Test Helper

Helper for state file management and assertions.
"""
import json
from pathlib import Path

from .base_helper import BaseTestHelper


class StateTestHelper(BaseTestHelper):
    """Helper for state management - setting/getting/asserting state files."""
    
    def set_state(self, behavior: str, action: str, completed_actions: list = None):
        """Set bot state to specific behavior/action."""
        from datetime import datetime
        
        state_data = {
            'current_behavior': f'story_bot.{behavior}',
            'current_action': f'story_bot.{behavior}.{action}',
            'operation': 'instructions',
            'working_directory': str(self.workspace),
            'timestamp': datetime.now().isoformat()
        }
        
        if completed_actions:
            state_data['completed_actions'] = [
                {'action_state': action_state, 'timestamp': datetime.now().isoformat()}
                for action_state in completed_actions
            ]
        
        state_file = self.workspace / 'behavior_action_state.json'
        state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
        
        # Reload the bot state from the file
        self.parent.bot.behaviors.load_state()
        
        return state_file
    
    def get_state(self) -> dict:
        """Read current bot state from workspace."""
        state_file = self.workspace / 'behavior_action_state.json'
        if not state_file.exists():
            return {}
        return json.loads(state_file.read_text(encoding='utf-8'))
    
    def add_completed(self, action_state: str):
        """Add action to completed list."""
        from datetime import datetime
        
        state = self.get_state()
        if 'completed_actions' not in state:
            state['completed_actions'] = []
        
        if not any(a.get('action_state') == action_state for a in state['completed_actions']):
            state['completed_actions'].append({
                'action_state': action_state,
                'timestamp': datetime.now().isoformat()
            })
        
        state_file = self.workspace / 'behavior_action_state.json'
        state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
    
    def clear_state(self):
        """Clear/delete behavior_action_state.json file."""
        state_file = self.workspace / 'behavior_action_state.json'
        if state_file.exists():
            state_file.unlink()
    
    def assert_state_shows(self, behavior: str, action: str):
        """Assert state file shows expected behavior and action."""
        state = self.get_state()
        assert state['current_behavior'] == f'story_bot.{behavior}'
        assert state['current_action'].startswith(f'story_bot.{behavior}.{action}')
    
    def assert_action_completed(self, action_state: str):
        """Assert action appears in completed_actions list."""
        state = self.get_state()
        completed = [a.get('action_state') for a in state.get('completed_actions', [])]
        assert action_state in completed, f"Action {action_state} not in completed list: {completed}"
    
    def assert_action_not_completed(self, action_state: str):
        """Assert action does NOT appear in completed_actions list."""
        state = self.get_state()
        completed = [a.get('action_state') for a in state.get('completed_actions', [])]
        assert action_state not in completed, f"Action {action_state} should not be in completed list"
