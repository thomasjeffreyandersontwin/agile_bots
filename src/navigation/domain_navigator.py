"""Domain Navigator - Executes dot notation commands on domain objects"""
import re
import inspect
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
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[DomainNavigator] navigate() called with command: '{command}'")
        
        command_part, params_part = self._split_command_and_params(command)
        logger.info(f"[DomainNavigator] Split command: part='{command_part}', params='{params_part}'")
        
        current_object = self.bot
        parts = self._parse_dot_notation(command_part)
        logger.info(f"[DomainNavigator] Parsed parts: {parts}")
        
        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1
            
            # Strip trailing () from method calls (e.g., 'delete()' -> 'delete')
            if is_last and part.endswith('()'):
                part = part[:-2]
                logger.info(f"[DomainNavigator] Stripped () from method name, using: '{part}'")
            
            if hasattr(current_object, part):
                attr = getattr(current_object, part)
                
                # Check if this is a callable followed by a value (e.g., rename."New Name" or move_to."Target")
                if callable(attr) and not is_last and i + 1 < len(parts):
                    next_part = parts[i + 1]
                    # If the next part looks like a value (not a method/property), treat it as a parameter
                    if not hasattr(attr, next_part): 
                        # Get the first parameter name from the method signature
                        try:
                            sig = inspect.signature(attr)
                            # Get first parameter (excluding 'self')
                            param_names = [p for p in sig.parameters.keys() if p != 'self']
                            if param_names:
                                first_param_name = param_names[0]
                                # Call the method with the next part as the first parameter
                                params = {first_param_name: next_part}
                                # Merge with any other parameters
                                params.update(self._parse_parameters(params_part))
                                try:
                                    result = attr(**params)
                                    return self._format_result(part, result, params)
                                except ValueError as e:
                                    return {'status': 'error', 'message': str(e)}
                        except (ValueError, TypeError):
                            pass  # Fall through to normal navigation
                
                if is_last and callable(attr):
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"[DomainNavigator] Found callable method: '{part}'")
                    
                    params = self._parse_parameters(params_part)
                    logger.info(f"[DomainNavigator] Parsed params: {params}")
                    
                    # If it's an Action and no params, return its instructions instead of executing
                    if type(attr).__name__ == 'Action' and not params:
                        # Just return the action's instructions, don't execute it
                        return self._format_object_result(attr)
                    # For other callables or actions with params, execute them
                    try:
                        logger.info(f"[DomainNavigator] Calling {part} with params: {params}")
                        result = attr(**params)
                        logger.info(f"[DomainNavigator] Method {part} returned: {type(result)}")
                        return self._format_result(part, result, params)
                    except ValueError as e:
                        logger.error(f"[DomainNavigator] ValueError calling {part}: {str(e)}")
                        return {'status': 'error', 'message': str(e)}
                    except Exception as e:
                        logger.error(f"[DomainNavigator] Exception calling {part}: {str(e)}", exc_info=True)
                        return {'status': 'error', 'message': f'Error calling {part}: {str(e)}'}
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
        """
        # Split by finding where the parameters start (looking for param_name:)
        # Parameters follow pattern: word:value (with optional quotes around value)
        param_pattern = r'\s+\w+:(?:"[^"]*"|\d+|\w+)'
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
        Also handles dotted paths like: target:"Epic1"."Child1"
        
        Returns:
            dict with parameter names and values
        """
        if not params_str:
            return {}
        
        params = {}
        
        # Modified pattern to handle dotted notation within parameter values
        # Matches: param_name:"value" or param_name:"Epic1"."Child1" or param_name:123 or param_name:word
        # Use lookahead to match quoted string potentially followed by more quoted strings with dots
        pattern = r'(\w+):(?:"([^"]*)"(?:\."([^"]*)")*|(\d+)|(\w+))'
        
        i = 0
        while i < len(params_str):
            # Find next parameter name
            param_match = re.match(r'(\w+):', params_str[i:])
            if not param_match:
                i += 1
                continue
            
            param_name = param_match.group(1)
            if param_name == 'at_position':
                param_name = 'position'
            
            i += param_match.end()
            
            # Check what type of value follows
            if i < len(params_str) and params_str[i] == '"':
                # Quoted value - may have dotted notation like "Epic1"."Child1"
                value_parts = []
                segment_count = 0
                while i < len(params_str) and params_str[i] == '"':
                    # Find closing quote, skipping escaped quotes
                    j = i + 1
                    while j < len(params_str):
                        if params_str[j] == '"' and (j == 0 or params_str[j-1] != '\\'):
                            # Found unescaped closing quote
                            break
                        j += 1
                    
                    if j >= len(params_str):
                        # No closing quote found
                        break
                    
                    segment_count += 1
                    # Extract value - include quotes for dotted paths, strip for single values
                    value_parts.append(params_str[i:j+1])  # Keep quotes for now
                    i = j + 1
                    # Check for dot continuation
                    if i < len(params_str) and params_str[i:i+2] == '."':
                        value_parts.append('.')
                        i += 1  # Skip the dot
                    else:
                        break
                # Join all parts
                full_value = ''.join(value_parts)
                # Strip quotes only for single-segment values (not dotted paths)
                if segment_count == 1:
                    # Single segment like name:"aaa" -> strip quotes to get "aaa"
                    stripped_value = full_value[1:-1]  # Remove first and last quote
                    # Unescape any escaped quotes or backslashes
                    unescaped_value = stripped_value.replace('\\\"', '"').replace('\\\\', '\\')
                    params[param_name] = unescaped_value
                else:
                    # Dotted path like target:"Epic1"."Child1" -> keep quotes
                    params[param_name] = full_value
            else:
                # Unquoted value - could be digit or word
                value_match = re.match(r'(\d+|\w+)', params_str[i:])
                if value_match:
                    value = value_match.group(1)
                    if value.isdigit():
                        params[param_name] = int(value)
                    else:
                        params[param_name] = value
                    i += value_match.end()
            
            # Skip whitespace between parameters
            while i < len(params_str) and params_str[i].isspace():
                i += 1
        
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
        
        # If result is already a dict with status, return it as-is (like submit_instructions result)
        if isinstance(result, dict) and 'status' in result:
            return result
        
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
