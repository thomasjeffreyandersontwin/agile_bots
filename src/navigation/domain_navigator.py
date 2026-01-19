"""Domain Navigator - Executes dot notation commands on domain objects"""
import re
from typing import Any


class DomainNavigator:
    """Navigate and execute methods on domain objects via dot notation"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def navigate(self, command: str) -> Any:
        """Parse and execute a domain object command
        
        Examples:
            story_graph.create_epic name:"User Management"
            story_graph."Epic Name".create_sub_epic name:"Auth"
        """
        command_part, params_part = self._split_command_and_params(command)
        
        current_object = self.bot
        parts = self._parse_dot_notation(command_part)
        
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            
            if hasattr(current_object, part):
                attr = getattr(current_object, part)
                
                if is_last and callable(attr):
                    params = self._parse_parameters(params_part)
                    try:
                        result = attr(**params)
                        return self._format_result(part, result, params)
                    except ValueError as e:
                        return {'status': 'error', 'message': str(e)}
                elif is_last:
                    return self._format_object_result(attr)
                else:
                    current_object = attr
            elif hasattr(current_object, '__getitem__'):
                try:
                    current_object = current_object[part]
                except (KeyError, TypeError):
                    return {
                        'status': 'error',
                        'message': f"Cannot access '{part}' on {type(current_object).__name__}"
                    }
            else:
                return {
                    'status': 'error',
                    'message': f"'{part}' not found on {type(current_object).__name__}"
                }
        
        return current_object
    
    def _split_command_and_params(self, command: str) -> tuple:
        """Split command into dot notation part and parameters part
        
        Example: 
            'story_graph.create_epic name:"User" at_position:1'
            -> ('story_graph.create_epic', 'name:"User" at_position:1')
        """
        match = re.match(r'([a-zA-Z0-9_."]+)\s*(.*)', command)
        if match:
            return match.group(1), match.group(2).strip()
        return command, ''
    
    def _parse_dot_notation(self, path: str) -> list:
        """Parse dot notation into parts, handling quoted strings
        
        Example:
            'story_graph."Epic Name".create_sub_epic'
            -> ['story_graph', 'Epic Name', 'create_sub_epic']
        """
        parts = []
        current = ''
        in_quotes = False
        
        for char in path:
            if char == '"':
                in_quotes = not in_quotes
            elif char == '.' and not in_quotes:
                if current:
                    parts.append(current)
                    current = ''
            else:
                current += char
        
        if current:
            parts.append(current)
        
        return parts
    
    def _parse_parameters(self, params_str: str) -> dict:
        """Parse parameters from string like: name:"User Management" at_position:1
        
        Returns:
            dict with parameter names and values
        """
        if not params_str:
            return {}
        
        params = {}
        
        pattern = r'(\w+):(?:"([^"]*)"|(\d+)|(\w+))'
        matches = re.findall(pattern, params_str)
        
        for match in matches:
            param_name = match[0]
            
            if param_name == 'at_position':
                param_name = 'position'
            
            if match[1]:
                params[param_name] = match[1]
            elif match[2]:
                params[param_name] = int(match[2])
            elif match[3]:
                params[param_name] = match[3]
        
        return params
    
    def _format_result(self, method_name: str, result: Any, params: dict) -> dict:
        """Format domain object method result as serializable dict"""
        if result is None:
            return {'status': 'success', 'message': f'{method_name} completed'}
        
        if hasattr(result, 'name'):
            return {
                'status': 'success',
                'message': f'Created {type(result).__name__} "{result.name}"',
                'node_name': result.name,
                'node_type': type(result).__name__
            }
        
        if isinstance(result, (str, int, float, bool, list, dict)):
            return {'status': 'success', 'result': result}
        
        return {'status': 'success', 'message': f'{method_name} completed', 'result_type': type(result).__name__}
    
    def _format_object_result(self, obj: Any) -> dict:
        """Format a domain object (like StoryMap) as serializable dict"""
        if hasattr(obj, 'story_graph') and isinstance(getattr(obj, 'story_graph'), dict):
            return {'status': 'success', 'result': obj.story_graph}
        
        if isinstance(obj, (str, int, float, bool, list, dict)):
            return {'status': 'success', 'result': obj}
        
        return {'status': 'success', 'message': f'Retrieved {type(obj).__name__}', 'result_type': type(obj).__name__}
