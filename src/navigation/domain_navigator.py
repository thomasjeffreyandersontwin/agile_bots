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
                    # Handle Action objects specially
                    if type(attr).__name__ == 'Action' or type(attr).__name__.endswith('Action'):
                        if not params:
                            # No params - return instructions without executing
                            return self._format_object_result(attr)
                        else:
                            # Has params - create context and execute
                            try:
                                # Get the context class from the action
                                context_class = getattr(attr, 'context_class', None)
                                if context_class:
                                    context = context_class()
                                else:
                                    # Fallback to generic context
                                    from actions.action_context import ActionContext
                                    context = ActionContext()
                                
                                # Set params as context attributes
                                for key, value in params.items():
                                    setattr(context, key, value)
                                
                                # Execute the action with context
                                result = attr.do_execute(context)
                                return self._format_result(part, result, params)
                            except Exception as e:
                                return {'status': 'error', 'message': str(e)}
                    
                    # For non-Action callables, use kwargs directly
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
            
            'story_graph."Invoke Bot".create name:"Test"'
            -> ('story_graph."Invoke Bot".create', 'name:"Test"')
            
            'shape.clarify scope="value" depth="Workflow"'
            -> ('shape.clarify', 'scope="value" depth="Workflow"')
        """
        # Split by finding where the parameters start (looking for param_name: or param_name=)
        # Parameters follow pattern: word[:=]value (with optional quotes around value)
        param_pattern = r'\s+[\w\.]+[:=](?:"[^"]*"|\d+|\w+)'
        param_match = re.search(param_pattern, command)
        
        if param_match:
            split_pos = param_match.start()
            command_part = command[:split_pos].strip()
            params_part = command[split_pos:].strip()
            return command_part, params_part
        
        # No parameters found
        return command.strip(), ''
    
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
        Also supports nested params like: scope="value" depth_of_shaping="Workflow"
        For clarify/strategy actions, converts flat params to answers/decisions dict
        
        Returns:
            dict with parameter names and values
        """
        if not params_str:
            return {}
        
        params = {}
        
        # Support both : and = for assignment
        pattern = r'([\w\.]+)[:=](?:"([^"]*)"|(\d+)|(\w+))'
        matches = re.findall(pattern, params_str)
        
        # Track if we're collecting answers or decisions (for clarify/strategy)
        collected_answers = {}
        
        for match in matches:
            param_name = match[0]
            
            if param_name == 'at_position':
                param_name = 'position'
            
            if match[1]:
                value = match[1]
            elif match[2]:
                value = int(match[2])
            elif match[3]:
                value = match[3]
            else:
                continue
            
            # All params become answers by default (to avoid conflicts with internal context attributes)
            # The key is used as-is for the answer
            collected_answers[param_name] = value
        
        # All collected params become the answers dict
        if collected_answers:
            params['answers'] = collected_answers
        
        return params
    
    def _format_result(self, method_name: str, result: Any, params: dict) -> dict:
        """Format domain object method result as serializable dict"""
        if result is None:
            return {'status': 'success', 'message': f'{method_name} completed'}
        
        # Handle Instructions objects - return them directly so they can be rendered
        if type(result).__name__ == 'Instructions':
            return result
        
        # Handle operation results (delete, rename, move_to)
        if isinstance(result, dict) and 'operation' in result:
            operation = result['operation']
            node_type = result.get('node_type', 'Node')
            node_name = result.get('node_name', '')
            
            if operation == 'delete':
                message = f'Deleted {node_type} "{node_name}"'
                children_moved = result.get('children_moved')
                if children_moved:
                    message += f'. Moved {children_moved} children to parent'
                return {
                    'status': 'success',
                    'message': message,
                    'node_name': node_name,
                    'node_type': node_type
                }
            elif operation == 'rename':
                old_name = result.get('old_name', '')
                new_name = result.get('new_name', '')
                return {
                    'status': 'success',
                    'message': f'Renamed {node_type} "{old_name}" to "{new_name}"',
                    'old_name': old_name,
                    'new_name': new_name,
                    'node_type': node_type
                }
            elif operation == 'move':
                source = result.get('source_parent', '')
                target = result.get('target_parent', '')
                position = result.get('position')
                message = f'Moved {node_type} "{node_name}" from "{source}" to "{target}"'
                if position is not None:
                    message += f' at position {position}'
                return {
                    'status': 'success',
                    'message': message,
                    'node_name': node_name,
                    'node_type': node_type,
                    'source_parent': source,
                    'target_parent': target
                }
        
        if hasattr(result, 'name'):
            response = {
                'status': 'success',
                'message': f'Created {type(result).__name__} "{result.name}"',
                'node_name': result.name,
                'node_type': type(result).__name__
            }
            # Include position if available
            if hasattr(result, 'sequential_order') and result.sequential_order is not None:
                actual_position = int(result.sequential_order)
                response['position'] = actual_position
                response['message'] += f' at position {actual_position}'
                # Check if position was adjusted
                requested_position = params.get('position')
                if requested_position is not None and requested_position != actual_position:
                    response['message'] += f' (adjusted from {requested_position})'
            return response
        
        if isinstance(result, (str, int, float, bool, list, dict)):
            return {'status': 'success', 'result': result}
        
        return {'status': 'success', 'message': f'{method_name} completed', 'result_type': type(result).__name__}
    
    def _format_object_result(self, obj: Any) -> dict:
        """Format a domain object (like StoryMap) as serializable dict"""
        # Handle Instructions objects - return them directly so CLI adapter can format them
        if type(obj).__name__ == 'Instructions':
            return obj
        
        if hasattr(obj, 'story_graph') and isinstance(getattr(obj, 'story_graph'), dict):
            return {'status': 'success', 'result': obj.story_graph}
        
        if isinstance(obj, (str, int, float, bool, list, dict)):
            return {'status': 'success', 'result': obj}
        
        return {'status': 'success', 'message': f'Retrieved {type(obj).__name__}', 'result_type': type(obj).__name__}
