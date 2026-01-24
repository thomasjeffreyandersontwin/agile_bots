"""
File Test Helper
Handles file and directory operations for testing
"""
import json
from pathlib import Path
from .base_helper import BaseHelper


class FileTestHelper(BaseHelper):
    """Helper for file and directory testing"""
    
    def assert_file_updated(self, file_path, expected_content):
        """Assert file updated with expected content."""
        file_path = Path(file_path)
        assert file_path.exists(), f"File should exist: {file_path}"
        
        if isinstance(expected_content, dict):
            actual_content = json.loads(file_path.read_text(encoding='utf-8'))
            assert actual_content == expected_content, f"Expected {expected_content}, got {actual_content}"
        else:
            actual_content = file_path.read_text(encoding='utf-8')
            assert actual_content == expected_content, f"Expected {expected_content}, got {actual_content}"
    
    def given_directory_created(self, directory, **params):
        """Create directory structure."""
        directory_type = params.get('directory_type', 'workspace')
        behavior = params.get('behavior')
        
        if directory_type == 'workspace':
            directory.mkdir(parents=True, exist_ok=True)
            return directory
        
        elif directory_type == 'docs_stories':
            docs_dir = directory / 'docs' / 'stories'
            docs_dir.mkdir(parents=True, exist_ok=True)
            return docs_dir
        
        elif directory_type == 'story_graph':
            if not behavior:
                raise ValueError("behavior parameter required for story_graph directory")
            behavior_dir = directory / 'behaviors' / behavior
            kg_dir = behavior_dir / 'content' / 'story_graph'
            kg_dir.mkdir(parents=True, exist_ok=True)
            return kg_dir
        
        elif directory_type == 'docs':
            docs_dir = directory / "docs" / "stories"
            docs_dir.mkdir(parents=True, exist_ok=True)
            return docs_dir
        
        elif directory_type == 'story_graph_prioritization':
            if not behavior:
                raise ValueError("behavior parameter required for story_graph_prioritization directory")
            behavior_dir = directory / 'behaviors' / behavior
            kg_dir = behavior_dir / 'content' / 'story_graph'
            kg_dir.mkdir(parents=True, exist_ok=True)
            return kg_dir
        
        elif directory_type == 'behavior_render':
            if not behavior:
                raise ValueError("behavior parameter required for behavior_render directory")
            behavior_dir = directory / 'behaviors' / behavior
            render_dir = behavior_dir / 'content' / 'render'
            render_dir.mkdir(parents=True, exist_ok=True)
            instructions_file = render_dir / 'instructions.json'
            if not instructions_file.exists():
                instructions_file.write_text(
                    json.dumps({
                        'behaviorName': behavior,
                        'instructions': [f'Render outputs for {behavior} behavior']
                    }),
                    encoding='utf-8'
                )
            return render_dir
        
        else:
            raise ValueError(f"Unknown directory_type: {directory_type}")
    
    def given_file_created(self, directory: Path, filename: str, content, file_type: str = 'json') -> Path:
        """Create file in directory."""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / filename
        
        if file_type == 'json':
            if isinstance(content, dict):
                file_path.write_text(json.dumps(content, indent=2), encoding='utf-8')
            elif isinstance(content, str):
                file_path.write_text(content, encoding='utf-8')
            else:
                file_path.write_text(json.dumps(content, indent=2), encoding='utf-8')
        else:
            file_path.write_text(str(content), encoding='utf-8')
        
        return file_path
    
    def given_files_created(self, directory: Path, filenames: list, file_type: str = 'json') -> list:
        """Create multiple files in directory."""
        created_files = []
        for item in filenames:
            if isinstance(item, tuple):
                filename, content = item
            else:
                filename = item
                content = '' if file_type == 'text' else {}
            
            file_path = self.given_file_created(directory, filename, content, file_type=file_type)
            created_files.append(file_path)
        
        return created_files
    
    def given_config_dict(self, config_type: str, **config_data) -> dict:
        """Create config dictionary."""
        if config_type == 'state_file':
            return {
                'current_behavior': config_data.get('current_behavior', ''),
                'current_action': config_data.get('current_action', ''),
                'completed_actions': config_data.get('completed_actions', []),
                'timestamp': config_data.get('timestamp', '2025-12-04T16:00:00.000000')
            }
        elif config_type == 'file_paths':
            files = config_data.get('files', [])
            if isinstance(files, list):
                return {'files': files}
            return files if isinstance(files, dict) else {}
        elif config_type == 'actions_workflow':
            actions = config_data.get('actions', [])
            return {'actions': actions}
        elif config_type == 'behavior_config':
            behavior_config = {
                'description': config_data.get('description', ''),
                'goal': config_data.get('goal', ''),
                'inputs': config_data.get('inputs', []),
                'outputs': config_data.get('outputs', []),
            }
            if 'actions' in config_data:
                behavior_config['actions_workflow'] = {'actions': config_data['actions']}
            elif 'actions_workflow' in config_data:
                behavior_config['actions_workflow'] = config_data['actions_workflow']
            if 'instructions' in config_data:
                behavior_config['instructions'] = config_data['instructions']
            if 'trigger_words' in config_data:
                behavior_config['trigger_words'] = config_data['trigger_words']
            if 'behaviorName' in config_data:
                behavior_config['behaviorName'] = config_data['behaviorName']
            if 'order' in config_data:
                behavior_config['order'] = config_data['order']
            return behavior_config
        elif config_type == 'action_config':
            if 'config' in config_data:
                return config_data['config']
            action_name = config_data.get('action_name', 'clarify')
            return {
                'name': action_name,
                'workflow': config_data.get('workflow', True),
                'order': config_data.get('order', 1),
                'instructions': config_data.get('instructions', [f'{action_name} instructions'])
            }
        else:
            raise ValueError(f"Unknown config_type: {config_type}")
    
    def then_environment_variables_not_set(self, var_names):
        """Assert environment variables are not set."""
        import os
        if isinstance(var_names, str):
            var_names = [var_names]
        for var_name in var_names:
            assert var_name not in os.environ or os.environ[var_name] == '', \
                f"Environment variable {var_name} should not be set, but has value: {os.environ.get(var_name)}"
    
    def then_environment_variable_matches(self, var_name, expected_value):
        """Assert environment variable matches expected value."""
        import os
        actual_value = os.environ.get(var_name)
        if isinstance(expected_value, Path):
            expected_value = str(expected_value)
        if isinstance(actual_value, Path):
            actual_value = str(actual_value)
        assert actual_value == expected_value, \
            f"Environment variable {var_name} mismatch: expected {expected_value}, got {actual_value}"
    
    def then_function_returns_same_value(self, func, value):
        """Assert function returns same value on multiple calls."""
        result1 = func()
        result2 = func()
        result3 = func()
        assert result1 == value and result2 == value and result3 == value, \
            f"Function should return {value} consistently, got {result1}, {result2}, {result3}"
    
    def then_function_returns_path(self, func, expected_path):
        """Assert function returns expected path."""
        actual_path = func()
        if isinstance(actual_path, str):
            actual_path = Path(actual_path)
        if isinstance(expected_path, str):
            expected_path = Path(expected_path)
        assert actual_path == expected_path, \
            f"Function should return {expected_path}, got {actual_path}"
    
    def then_item_matches(self, item, expected=None, item_type=None, **checks):
        """Assert item matches expected values."""
        if item_type is None:
            if hasattr(item, 'action'):
                item_type = 'result'
            elif isinstance(item, dict) and 'current_behavior' in item:
                item_type = 'state_file'
            elif isinstance(item, dict):
                item_type = 'dict'
        
        if item_type == 'result':
            if expected is not None:
                assert item == expected
            for key, value in checks.items():
                assert getattr(item, key, None) == value, f"Expected {key}={value}, got {getattr(item, key, None)}"
        
        elif item_type == 'state_file' or item_type == 'dict':
            if expected is not None:
                assert item == expected
            for key, value in checks.items():
                assert item.get(key) == value, f"Expected {key}={value}, got {item.get(key)}"
        
        else:
            if expected is not None:
                assert item == expected
    
    def then_violation_has_field(self, violation, field, value):
        """Assert violation has expected field value."""
        field_mapping = {
            'line_number': 'line_number',
            'location': 'location',
            'message': 'violation_message',
            'violation_message': 'violation_message',
            'severity': 'severity'
        }
        actual_field = field_mapping.get(field, field)
        assert actual_field in violation, f"Violation missing field '{actual_field}': {violation}"
        
        if actual_field == 'violation_message':
            assert value in violation[actual_field], \
                f"Expected message '{value}' not found in '{violation[actual_field]}'"
        else:
            assert violation[actual_field] == value, \
                f"Violation {actual_field} mismatch: expected {value}, got {violation[actual_field]}"
