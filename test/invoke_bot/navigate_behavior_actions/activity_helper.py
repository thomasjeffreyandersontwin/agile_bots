"""
Activity Test Helper
Handles activity logging, tracking, timestamps
"""
import json
from pathlib import Path
from helpers.base_helper import BaseHelper


class ActivityTestHelper(BaseHelper):
    """Helper for activity logging and tracking testing"""
    
    def get_activity_log(self) -> list:
        """Read and parse activity_log.json (TinyDB format)."""
        log_file = self.parent.workspace / 'activity_log.json'
        if not log_file.exists():
            return []
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            return db.all()
    
    def create_activity_log_file(self):
        """Create activity log file in workspace."""
        log_file = self.parent.workspace / 'activity_log.json'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(json.dumps({'_default': {}}), encoding='utf-8')
        return log_file
    
    def create_activity_log_with_entries(self, entries: list = None):
        """Create activity log file with entries.
        
        Args:
            entries: List of activity log entries (if None, creates default multiple entries)
        
        Returns:
            Path to log file
        """
        log_file = self.create_activity_log_file()
        if entries is None:
            # Default: create multiple entries
            from tinydb import TinyDB
            with TinyDB(log_file) as db:
                db.insert({'action_state': 'story_bot.shape.render', 'timestamp': '09:00'})
                db.insert({'action_state': 'story_bot.discovery.render', 'timestamp': '10:00'})
        elif entries:
            from tinydb import TinyDB
            with TinyDB(log_file) as db:
                for entry in entries:
                    db.insert(entry)
        return log_file
    
    def assert_activity_logged_with_action_state(self, expected_action_state: str):
        """Assert activity logged with expected action_state."""
        activity_log = self.get_activity_log()
        if not any(entry.get('action_state') == expected_action_state for entry in activity_log):
            actual_states = [entry.get('action_state') for entry in activity_log]
            raise AssertionError(
                f"Expected action_state '{expected_action_state}' not found in activity log. "
                f"Actual entries: {actual_states}"
            )
    
    def assert_completion_entry_logged_with_outputs(self, expected_outputs: dict = None, expected_duration: int = None):
        """Assert completion entry logged with outputs and duration."""
        activity_log = self.get_activity_log()
        completion_entry = next((e for e in activity_log if 'outputs' in e), None)
        assert completion_entry is not None, "No completion entry found with outputs"
        if expected_outputs is not None:
            assert completion_entry['outputs'] == expected_outputs
        if expected_duration is not None:
            assert completion_entry['duration'] == expected_duration
    
    def assert_activity_log_matches(self, **checks):
        """Assert activity log matches expected values.
        
        Args:
            **checks: Checks to perform (expected_count, expected_action_state, etc.)
        """
        from tinydb import TinyDB
        
        log_file = self.parent.workspace / 'activity_log.json'
        
        if not log_file.exists():
            if 'expected_count' in checks and checks['expected_count'] == 0:
                return
            assert False, f"Activity log file does not exist at {log_file}"
        
        with TinyDB(log_file) as db:
            entries = db.all()
            
            if 'expected_count' in checks:
                assert len(entries) == checks['expected_count'], \
                    f"Expected {checks['expected_count']} entries, got {len(entries)}"
            
            if 'expected_action_states' in checks:
                expected_states = checks['expected_action_states']
                assert len(entries) == len(expected_states), \
                    f"Expected {len(expected_states)} entries, got {len(entries)}"
                for i, expected_state in enumerate(expected_states):
                    assert entries[i].get('action_state') == expected_state, (
                        f"Entry {i} should have action_state '{expected_state}', got '{entries[i].get('action_state')}'"
                    )
            
            if 'expected_last_action_state' in checks:
                assert len(entries) > 0, "No entries in activity log"
                assert entries[-1].get('action_state') == checks['expected_last_action_state'], (
                    f"Last entry should have action_state '{checks['expected_last_action_state']}', "
                    f"got '{entries[-1].get('action_state')}'"
                )
            
            if 'expected_action_state' in checks:
                matching_entries = [e for e in entries if e.get('action_state') == checks['expected_action_state']]
                assert len(matching_entries) > 0, \
                    f"No entry found with action_state={checks['expected_action_state']}"
                if 'expected_status' in checks:
                    assert matching_entries[0].get('status') == checks['expected_status'], \
                        f"Expected status {checks['expected_status']}, got {matching_entries[0].get('status')}"
            
            if 'workflow_complete' in checks and checks['workflow_complete']:
                completion_entry = next((e for e in entries if 'outputs' in e), None)
                assert completion_entry is not None, "No completion entry found with outputs"
                assert completion_entry['outputs'].get('workflow_complete') is True, \
                    "Completion entry does not have workflow_complete flag set to True"
            
            if 'expected_entries' in checks:
                expected_entries = checks['expected_entries']
                assert len(entries) == len(expected_entries), \
                    f"Expected {len(expected_entries)} entries, got {len(entries)}"
                for expected_entry in expected_entries:
                    expected_action_state = expected_entry.get('action_state')
                    assert any(
                        entry.get('action_state') == expected_action_state
                        for entry in entries
                    ), f"No entry found with action_state '{expected_action_state}'"
    
    def create_activity_tracker(self, bot_name='story_bot'):
        """Create ActivityTracker instance."""
        from actions.activity_tracker import ActivityTracker
        from bot_path.bot_path import BotPath
        bot_paths = BotPath(workspace_path=self.parent.workspace, bot_directory=self.parent.bot_directory)
        return ActivityTracker(bot_paths=bot_paths, bot_name=bot_name)
    
    def track_activity_start(self, tracker, action_state):
        """Track activity start with tracker."""
        from actions.activity_tracker import ActionState
        
        if isinstance(action_state, str):
            parts = action_state.split('.')
            if len(parts) == 3:
                bot_name, behavior, action = parts
                tracker.track_start(ActionState(bot_name, behavior, action))
            else:
                raise ValueError(f"Invalid action_state format: {action_state}")
        elif isinstance(action_state, dict):
            tracker.track_start(ActionState(action_state['bot_name'], action_state['behavior'], action_state['action']))
        else:
            raise ValueError(f"Invalid action_state type: {type(action_state)}")
    
    def assert_activity_logged(self, action_state: str, event_type: str):
        """Assert action is logged in activity log with specified event type."""
        activity_log = self.get_activity_log()
        matching_entries = [
            entry for entry in activity_log
            if entry.get('action_state') == action_state 
            and entry.get('event') == event_type
        ]
        assert len(matching_entries) > 0, \
            f"No {event_type} event found for {action_state} in activity log"
    
    def given_activity_log(self, entries: list = None, **params):
        """Create activity log with entries."""
        log_file = self.parent.workspace / 'activity_log.json'
        from tinydb import TinyDB
        
        with TinyDB(log_file) as db:
            if entries is None:
                db.insert({'action_state': 'story_bot.shape.render', 'timestamp': '09:00'})
                db.insert({'action_state': 'story_bot.discovery.render', 'timestamp': '10:00'})
            else:
                for entry in entries:
                    db.insert(entry)
        
        return log_file
    
    def read_activity_log(self) -> list:
        """Read activity log from workspace directory."""
        log_file = self.parent.workspace / 'activity_log.json'
        from tinydb import TinyDB
        with TinyDB(log_file) as db:
            return db.all()
    
    def then_activity_logged_with_action_state(self, expected_action_state: str):
        """Assert activity logged with expected action_state."""
        from tinydb import TinyDB
        log_file = self.parent.workspace / 'activity_log.json'
        
        with TinyDB(log_file) as db:
            entries = db.all()
            if not any(entry.get('action_state') == expected_action_state for entry in entries):
                actual_states = [entry.get('action_state') for entry in entries]
                raise AssertionError(
                    f"Expected action_state '{expected_action_state}' not found in activity log. "
                    f"Actual entries: {actual_states}"
                )
    
    def then_activity_log_matches(self, log_file=None, **checks):
        """Assert activity log matches expected values."""
        from tinydb import TinyDB
        
        if log_file is None:
            log_file = self.parent.workspace / 'activity_log.json'
        
        if not log_file.exists():
            if 'expected_count' in checks and checks['expected_count'] == 0:
                return
            assert False, f"Activity log file does not exist at {log_file}"
        
        with TinyDB(log_file) as db:
            entries = db.all()
            
            if 'expected_count' in checks:
                assert len(entries) == checks['expected_count'], \
                    f"Expected {checks['expected_count']} entries, got {len(entries)}"
            
            if 'expected_action_state' in checks:
                assert any(entry.get('action_state') == checks['expected_action_state'] for entry in entries), \
                    f"Expected action_state '{checks['expected_action_state']}' not found in entries"
            
            if 'expected_action_states' in checks:
                expected_states = checks['expected_action_states']
                actual_states = [entry.get('action_state') for entry in entries]
                assert len(actual_states) == len(expected_states), \
                    f"Expected {len(expected_states)} entries, got {len(actual_states)}"
                for i, expected_state in enumerate(expected_states):
                    assert actual_states[i] == expected_state, \
                        f"Entry {i}: expected '{expected_state}', got '{actual_states[i]}'"
            
            if 'expected_last_action_state' in checks:
                assert entries[-1].get('action_state') == checks['expected_last_action_state'], \
                    f"Expected last action_state '{checks['expected_last_action_state']}', got '{entries[-1].get('action_state')}'"
            
            if 'expected_status' in checks:
                assert any(entry.get('status') == checks['expected_status'] for entry in entries), \
                    f"Expected status '{checks['expected_status']}' not found in entries"
            
            if 'expected_entries' in checks:
                expected_entries = checks['expected_entries']
                for expected_entry in expected_entries:
                    expected_action_state = expected_entry.get('action_state')
                    matching_entry = next((e for e in entries if e.get('action_state') == expected_action_state), None)
                    assert matching_entry is not None, \
                        f"Expected entry with action_state '{expected_action_state}' not found"
                    for key, value in expected_entry.items():
                        if key != 'action_state':
                            assert matching_entry.get(key) == value, \
                                f"Entry {expected_action_state}: expected {key}='{value}', got '{matching_entry.get(key)}'"
            
            if 'workflow_complete' in checks:
                completion_entry = next((e for e in entries if 'outputs' in e), None)
                assert completion_entry is not None, "No completion entry found in activity log"
                assert completion_entry.get('outputs', {}).get('workflow_complete') == True, \
                    "Completion entry should have workflow_complete=True in outputs"
    
    def given_activity_tracker(self, bot_name='story_bot'):
        """Create activity tracker."""
        from actions.activity_tracker import ActivityTracker
        from bot_path.bot_path import BotPath
        bot_paths = BotPath(workspace_path=self.parent.workspace, bot_directory=self.parent.bot_directory)
        return ActivityTracker(bot_paths=bot_paths, bot_name=bot_name)
    
    def when_activity_tracks_start(self, tracker, action_state):
        """Track activity start."""
        from actions.activity_tracker import ActionState
        
        if isinstance(action_state, str):
            parts = action_state.split('.')
            if len(parts) == 3:
                bot_name, behavior, action = parts
                action_state_obj = ActionState(bot_name=bot_name, behavior=behavior, action=action)
            else:
                raise ValueError(f"Invalid action_state format: {action_state}. Expected 'bot_name.behavior.action'")
        elif isinstance(action_state, dict):
            action_state_obj = ActionState(
                bot_name=action_state.get('bot_name'),
                behavior=action_state.get('behavior'),
                action=action_state.get('action')
            )
        else:
            action_state_obj = action_state
        
        tracker.track_start(action_state_obj)
    
    def then_completion_entry_logged_with_outputs(self, log_file_or_workspace: Path, expected_outputs: dict = None, expected_duration: int = None):
        """Assert completion entry logged with outputs and duration."""
        from tinydb import TinyDB
        if (log_file_or_workspace / 'activity_log.json').exists():
            log_file = log_file_or_workspace / 'activity_log.json'
        else:
            log_file = log_file_or_workspace
        
        with TinyDB(log_file) as db:
            entries = db.all()
            completion_entry = next((e for e in entries if 'outputs' in e), None)
            assert completion_entry is not None
            if expected_outputs is not None:
                assert completion_entry['outputs'] == expected_outputs
            if expected_duration is not None:
                assert completion_entry['duration'] == expected_duration
    
    def given_environment_bootstrapped_and_activity_log_initialized(self, bot_directory: Path, workspace_directory: Path):
        """Bootstrap environment and initialize activity log."""
        import os
        os.environ['BOT_DIRECTORY'] = str(bot_directory)
        os.environ['WORKING_AREA'] = str(workspace_directory)
        self.parent.workspace = workspace_directory
        self.parent.workspace.mkdir(parents=True, exist_ok=True)
        log_file = self.create_activity_log_file()
        return log_file
