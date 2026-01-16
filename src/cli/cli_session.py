
import sys
import logging
from pathlib import Path
from typing import Any, Dict

from agile_bots.src.cli.adapter_factory import AdapterFactory
from agile_bots.src.cli.cli_results import CLICommandResponse

class CLISession:
    
    def __init__(self, bot, workspace_directory: Path, mode: str = None):
        self.bot = bot
        self.workspace_directory = Path(workspace_directory)
        self.mode = mode
    
    def execute_command(self, command: str) -> CLICommandResponse:
        verb, args = self._parse_command(command)
        
        if args and ('--format json' in args or '--format=json' in args):
            self.mode = 'json'
            args = args.replace('--format json', '').replace('--format=json', '').strip()
        
        cli_terminated = verb == 'exit'
        
        is_navigation_command = verb in ('next', 'back', 'current', 'scope', 'path', 'workspace')
        
        if verb == 'status':
            result = self.bot
        elif verb == 'bot':
            if not args:
                result = {
                    'status': 'info',
                    'current_bot': self.bot.bot_name,
                    'registered_bots': self.bot.bots,
                    'message': f"Current bot: {self.bot.bot_name}. Available bots: {', '.join(self.bot.bots)}. Usage: bot <name>"
                }
            else:
                target_bot_name = args.strip()
                try:
                    self.bot.active_bot = target_bot_name
                    self.bot = self.bot.active_bot
                    result = {
                        'status': 'success',
                        'message': f'Switched to bot: {target_bot_name}',
                        'bot_name': target_bot_name
                    }
                except ValueError as e:
                    result = {
                        'status': 'error',
                        'message': str(e)
                    }
        elif verb == 'save':
            params = self._parse_save_params(args)
            result = self.bot.save(**params)
            if self.mode == 'json':
                import json
                output = json.dumps(result, indent=2)
                return CLICommandResponse(
                    output=output,
                    status=result.get('status', 'success'),
                    cli_terminated=False
                )
        # Special case: "submitrules:behavior" calls bot.submit_behavior_rules()
        elif verb.startswith('submitrules:') or verb.startswith('submitrules '):
            behavior_name = verb.split(':', 1)[1] if ':' in verb else verb.split(' ', 1)[1]
            behavior_name = behavior_name.strip()
            result = self.bot.submit_behavior_rules(behavior_name)
            # Submit returns a dict - serialize based on mode
            if self.mode == 'json':
                import json
                output = json.dumps(result, indent=2)
                return CLICommandResponse(
                    output=output,
                    status=result.get('status', 'success'),
                    cli_terminated=False
                )
            else:
                if result.get('status') == 'success':
                    output_lines = [
                        f"✓ {behavior_name} rules submitted to chat!",
                        f"  Behavior: {result.get('behavior')}",
                        f"  Action: {result.get('action')}",
                        f"  Length: {result.get('instructions_length', 0)} characters"
                    ]
                    
                    if result.get('cursor_status') == 'opened':
                        output_lines.append("  ✓ Cursor chat opened")
                    
                    return CLICommandResponse(
                        output='\n'.join(output_lines),
                        status='success',
                        cli_terminated=False
                    )
                else:
                    return CLICommandResponse(
                        output=f"Error: {result.get('message', 'Unknown error')}",
                        status='error',
                        cli_terminated=False
                    )
        # Special case: "submit" calls bot.submit_current_action() and returns result with instructions
        elif verb == 'submit':
            result = self.bot.submit_current_action()
            # Submit returns a dict - serialize based on mode
            if self.mode == 'json':
                import json
                output = json.dumps(result, indent=2)
                return CLICommandResponse(
                    output=output,
                    status=result.get('status', 'success'),
                    cli_terminated=False
                )
            else:
                if result.get('status') == 'success':
                    output_lines = [
                        f"✓ Instructions copied to clipboard!",
                        f"  Behavior: {result.get('behavior')}",
                        f"  Action: {result.get('action')}",
                        f"  Length: {result.get('instructions_length', 0)} characters"
                    ]
                    
                    if result.get('cursor_status') == 'opened':
                        output_lines.append("  ✓ Cursor chat opened")
                    elif result.get('cursor_status', '').startswith('failed'):
                        output_lines.append(f"  ⚠ Could not open Cursor chat automatically")
                        output_lines.append("  → Open Cursor chat manually and paste (Ctrl+V)")
                    else:
                        output_lines.append("  → Paste into Cursor chat (Ctrl+V)")
                    
                    output = '\n'.join(output_lines)
                else:
                    output = f"✗ {result.get('message', 'Submit failed')}"
                
                return CLICommandResponse(
                    output=output,
                    status=result.get('status', 'success'),
                    cli_terminated=False
                )
        elif hasattr(self.bot, verb):
            attr = getattr(self.bot, verb)
            if callable(attr):
                result = attr(args) if args else attr()
            else:
                result = attr
                
                from agile_bots.src.behaviors.behavior import Behavior
                is_behavior = isinstance(result, Behavior)
                
                if is_behavior:
                    result = self.bot.execute(result.name, None)
                    is_navigation_command = True
        else:
            result = self._handle_action_shortcut(verb, args)
            
            # Special case: if action is 'rules', automatically submit to chat
            if verb == 'rules' and result is not None:
                from agile_bots.src.instructions.instructions import Instructions
                if isinstance(result, Instructions):
                    # Submit the RULES instructions using behavior.submitRules()
                    if self.bot.behaviors.current:
                        submit_result = self.bot.behaviors.current.submitRules()
                    else:
                        submit_result = {
                            'status': 'error',
                            'message': 'No current behavior set'
                        }
                    
                    if submit_result.get('status') == 'success' and self.mode != 'json':
                        output_lines = [
                            f"✓ Rules submitted to chat!",
                            f"  Behavior: {submit_result.get('behavior')}",
                            f"  Action: {submit_result.get('action')}",
                            f"  Length: {submit_result.get('instructions_length', 0)} characters"
                        ]
                        
                        if submit_result.get('cursor_status') == 'opened':
                            output_lines.append("  ✓ Cursor chat opened")
                        
                        # Return submit result instead of instructions
                        return CLICommandResponse(
                            output='\n'.join(output_lines),
                            status='success',
                            cli_terminated=False
                        )
            
            if result is None:
                try:
                    result = self._route_to_behavior_action(command)
                    is_navigation_command = False
                    
                    # Special case: if action is 'rules', automatically submit to chat
                    if '.rules' in command.lower():
                        from agile_bots.src.instructions.instructions import Instructions
                        if isinstance(result, Instructions):
                            # Submit the RULES instructions using behavior.submitRules()
                            if self.bot.behaviors.current:
                                submit_result = self.bot.behaviors.current.submitRules()
                            else:
                                submit_result = {
                                    'status': 'error',
                                    'message': 'No current behavior set'
                                }
                            
                            if submit_result.get('status') == 'success' and self.mode != 'json':
                                output_lines = [
                                    f"✓ Rules submitted to chat!",
                                    f"  Behavior: {submit_result.get('behavior')}",
                                    f"  Action: {submit_result.get('action')}",
                                    f"  Length: {submit_result.get('instructions_length', 0)} characters"
                                ]
                                
                                if submit_result.get('cursor_status') == 'opened':
                                    output_lines.append("  ✓ Cursor chat opened")
                                
                                # Return submit result instead of instructions
                                return CLICommandResponse(
                                    output='\n'.join(output_lines),
                                    status='success',
                                    cli_terminated=False
                                )
                except ValueError:
                    error_message = f"Unknown command '{verb}'"
                    if self.mode == 'json':
                        import json
                        error_dict = {
                            'status': 'error',
                            'message': error_message,
                            'command': verb
                        }
                        output = json.dumps(error_dict, indent=2)
                    else:
                        output = f"ERROR: {error_message}"
                    return CLICommandResponse(
                        output=output,
                        status='error',
                        cli_terminated=False
                    )
            else:
                from agile_bots.src.instructions.instructions import Instructions
                if isinstance(result, Instructions):
                    adapter = self._get_adapter_for_domain(result)
                    output = adapter.serialize()
                    status_adapter = self._get_adapter_for_domain(self.bot)
                    status_output = status_adapter.serialize()
                    output = '\n'.join([
                        output,
                        "",
                        status_output
                    ])
                    return CLICommandResponse(
                        output=output,
                        cli_terminated=False
                    )
                else:
                    is_navigation_command = True
        
        adapter = self._get_adapter_for_domain(result)
        output = adapter.serialize()
        
        from agile_bots.src.instructions.instructions import Instructions
        if isinstance(result, Instructions) and self.mode == 'json':
            import json
            instructions_data = json.loads(output) if isinstance(output, str) else output
            status_adapter = self._get_adapter_for_domain(self.bot)
            status_json = status_adapter.serialize()
            status_data = json.loads(status_json) if isinstance(status_json, str) else status_json
            
            unified_response = {
                'instructions': instructions_data,
                'bot': status_data
            }
            output = json.dumps(unified_response, indent=2)
            return CLICommandResponse(
                output=output,
                cli_terminated=False
            )
        
        if is_navigation_command and not cli_terminated:
            if self.mode == 'json':
                import json
                result_data = json.loads(output) if isinstance(output, str) else output
                unified_response = {}
                
                if isinstance(result_data, dict):
                    unified_response.update(result_data)
                
                navigation_succeeded = True
                if isinstance(result, dict) and 'status' in result:
                    navigation_succeeded = result['status'] not in ['error', 'at_start', 'at_end']
                
                from agile_bots.src.instructions.instructions import Instructions
                result_is_instructions = isinstance(result, Instructions)
                
                if navigation_succeeded and not result_is_instructions:
                    instructions_result = self.bot.current()
                    
                    if isinstance(instructions_result, dict) and 'status' in instructions_result and instructions_result['status'] == 'error':
                        unified_response['instructions_error'] = instructions_result.get('message', 'Unknown error')
                    else:
                        instructions_adapter = self._get_adapter_for_domain(instructions_result)
                        instructions_json = instructions_adapter.serialize()
                        instructions_data = json.loads(instructions_json) if isinstance(instructions_json, str) else instructions_json
                        unified_response['instructions'] = instructions_data
                
                status_adapter = self._get_adapter_for_domain(self.bot)
                status_json = status_adapter.serialize()
                status_data = json.loads(status_json) if isinstance(status_json, str) else status_json
                unified_response['bot'] = status_data
                
                output = json.dumps(unified_response, indent=2)
            else:
                output_parts = [output]
                
                navigation_succeeded = True
                if isinstance(result, dict) and 'status' in result:
                    navigation_succeeded = result['status'] not in ['error', 'at_start', 'at_end']
                
                from agile_bots.src.instructions.instructions import Instructions
                result_is_instructions = isinstance(result, Instructions)
                
                if navigation_succeeded and not result_is_instructions:
                    instructions_result = self.bot.current()
                    
                    if isinstance(instructions_result, dict) and 'status' in instructions_result and instructions_result['status'] == 'error':
                        error_message = instructions_result.get('message', 'Unknown error')
                        output_parts.append("")
                        output_parts.append(f"ERROR: {error_message}")
                    else:
                        output_parts.append("")
                        output_parts.append("=" * 100)
                        output_parts.append("INSTRUCTIONS")
                        output_parts.append("=" * 100)
                        
                        instructions_adapter = self._get_adapter_for_domain(instructions_result)
                        output_parts.append(instructions_adapter.serialize())
                
                status_adapter = self._get_adapter_for_domain(self.bot)
                status_output = status_adapter.serialize()
                output_parts.append("")
                output_parts.append(status_output)
                
                output = '\n'.join(output_parts)
        
        return CLICommandResponse(
            output=output,
            cli_terminated=cli_terminated
        )
    
    def _parse_command(self, command: str) -> tuple[str, str]:
        parts = command.split(maxsplit=1)
        verb = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return verb, args
    
    def _parse_save_params(self, args_string: str) -> Dict[str, Any]:
        return self._parse_action_params(args_string)
    
    def _parse_action_params(self, args_string: str) -> Dict[str, Any]:
        import re
        import json
        
        params = {}
        
        answers_match = re.search(r"--answers\s+'([^']+)'", args_string)
        if answers_match:
            try:
                params['answers'] = json.loads(answers_match.group(1))
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse --answers: {e}")
        
        decisions_match = re.search(r"--decisions\s+'([^']+)'", args_string)
        if decisions_match:
            try:
                params['decisions'] = json.loads(decisions_match.group(1))
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse --decisions: {e}")
        
        assumptions_match = re.search(r"--assumptions\s+'([^']+)'", args_string)
        if assumptions_match:
            try:
                params['assumptions'] = json.loads(assumptions_match.group(1))
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse --assumptions: {e}")
        
        evidence_match = re.search(r"--evidence_provided\s+'([^']+)'", args_string)
        if evidence_match:
            try:
                params['evidence_provided'] = json.loads(evidence_match.group(1))
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse --evidence_provided: {e}")
        
        return params
    
    def _route_to_behavior_action(self, command: str) -> Any:
        parts = command.split(maxsplit=1)
        command_core = parts[0]
        args_string = parts[1] if len(parts) > 1 else ''
        
        params = self._parse_action_params(args_string) if args_string else None
        
        if '.' in command_core:
            command_parts = command_core.split('.')
            behavior_name = command_parts[0]
            action_name = command_parts[1] if len(command_parts) > 1 else None
            
            if hasattr(self.bot, 'execute'):
                return self.bot.execute(behavior_name, action_name, params)
        else:
            if hasattr(self.bot, 'execute'):
                result = self.bot.execute(command_core, None, params)
                if isinstance(result, dict) and result.get('status') == 'error':
                    raise ValueError(result.get('message', 'Unknown error'))
                return result
        raise ValueError(f"Unknown command: {command}")
    
    def _prepare_action_context(self, action, args: str):
        """Prepare action context with optional arguments."""
        from ..actions.action_context import ActionContext
        context = action.context_class() if hasattr(action, 'context_class') else ActionContext()
        
        if args and hasattr(context, 'message'):
            context.message = args
        
        return context
    
    def _build_instructions_from_dict(self, instructions_dict, action):
        """Build Instructions object from result dictionary."""
        from ..instructions.instructions import Instructions
        
        if not isinstance(instructions_dict, dict):
            return instructions_dict
        
        instructions = Instructions(
            base_instructions=instructions_dict.get('base_instructions', []),
            bot_paths=action.behavior.bot_paths,
            scope=action.instructions.scope if hasattr(action, 'instructions') else None
        )
        
        for key, value in instructions_dict.items():
            if key not in ('base_instructions', 'display_content'):
                instructions.set(key, value)
        
        display_content = instructions_dict.get('display_content', [])
        for line in display_content:
            instructions.add_display(line)
        
        return instructions
    
    def _execute_non_workflow_action(self, action, action_name: str, args: str):
        """Execute non-workflow action and return instructions."""
        try:
            context = self._prepare_action_context(action, args)
            result = action.execute(context)
            
            # Check if result contains instructions dict
            if isinstance(result, dict) and 'instructions' in result:
                return self._build_instructions_from_dict(result['instructions'], action)
            
            # Otherwise get instructions normally
            return action.get_instructions(context)
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error executing {action_name}: {str(e)}'
            }
    
    def _handle_action_shortcut(self, action_name: str, args: str) -> Any:
        """Handle shortcut command for executing an action."""
        if not self.bot.behaviors.current:
            return {
                'status': 'error',
                'message': 'No current behavior set. Please select a behavior first.'
            }
        
        behavior = self.bot.behaviors.current
        action = behavior.actions.find_by_name(action_name)
        
        if not action:
            return None
        
        # Check if non-workflow action
        is_non_workflow = action in behavior.actions._non_workflow_actions
        
        if is_non_workflow:
            return self._execute_non_workflow_action(action, action_name, args)
        
        # Workflow action - navigate and route
        behavior.actions.navigate_to(action_name)
        return self._route_to_behavior_action(f"{behavior.name}.{action_name}")
    
    def _get_adapter_for_domain(self, domain_object: Any):
        if self.mode:
            channel = self.mode
        else:
            is_piped = not sys.stdin.isatty()
            channel = 'markdown' if is_piped else 'tty'
        
        return AdapterFactory.create(domain_object, channel)
    
    def run(self):
        try:
            while True:
                try:
                    line = input(f"[{self.bot.name}] > ").strip()
                    if not line:
                        continue
                    
                    response = self.execute_command(line)
                    print(response.output)
                    print("")
                    
                    if response.cli_terminated:
                        break
                    
                except EOFError:
                    print("\nExiting CLI...")
                    break
                except KeyboardInterrupt:
                    print("\n\nInterrupted by user. Exiting CLI...")
                    break
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
                    
        except KeyboardInterrupt:
            pass
