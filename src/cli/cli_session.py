
import sys
import logging
from pathlib import Path
from typing import Any, Dict

from cli.adapter_factory import AdapterFactory
from cli.cli_results import CLICommandResponse

class CLISession:
    
    def __init__(self, bot, workspace_directory: Path, mode: str = None):
        self.bot = bot
        self.workspace_directory = Path(workspace_directory)
        self.mode = mode
    
    def execute_command(self, command: str) -> CLICommandResponse:
        # Extract format mode from the entire command first
        command = self._extract_format_mode(command)
        
        verb, args = self._parse_command(command)
        
        handler = self._get_command_handler(verb)
        if handler:
            response = handler(verb, args)
            if response:
                return response
        
        result, is_navigation_command = self._execute_verb(verb, args, command)
        cli_terminated = verb == 'exit'
        
        return self._build_response(result, is_navigation_command, cli_terminated)
    
    def _extract_format_mode(self, args: str) -> str:
        if not args:
            return args
        if '--format json' in args or '--format=json' in args:
            self.mode = 'json'
            return args.replace('--format json', '').replace('--format=json', '').strip()
        return args
    
    def _get_command_handler(self, verb: str):
        handlers = {
            'save': self._handle_save,
            'submit': self._handle_submit,
            'analyze_node': self._handle_analyze_node,
        }
        if verb.startswith('submitrules:') or verb.startswith('submitrules '):
            return self._handle_submitrules
        return handlers.get(verb)
    
    def _handle_save(self, verb: str, args: str) -> CLICommandResponse:
        params = self._parse_save_params(args)
        result = self.bot.save(**params)
        if self.mode == 'json':
            import json
            return CLICommandResponse(
                output=json.dumps(result, indent=2),
                status=result.get('status', 'success'),
                cli_terminated=False
            )
        return None
    
    def _handle_submit(self, verb: str, args: str) -> CLICommandResponse:
        result = self.bot.submit_current_action()
        return self._format_submit_response(result, "Instructions copied to clipboard!")
    
    def _handle_submitrules(self, verb: str, args: str) -> CLICommandResponse:
        behavior_name = verb.split(':', 1)[1] if ':' in verb else verb.split(' ', 1)[1]
        behavior_name = behavior_name.strip()
        result = self.bot.submit_behavior_rules(behavior_name)
        return self._format_submit_response(result, f"{behavior_name} rules submitted to chat!")
    
    def _handle_analyze_node(self, verb: str, args: str) -> CLICommandResponse:
        # Parse node name and type from args
        # Expected format: analyze_node "Node Name" type:epic|subepic|story
        import re
        node_name_match = re.search(r'"([^"]+)"', args)
        type_match = re.search(r'type:(\w+)', args)
        
        if not node_name_match:
            return CLICommandResponse(
                output='{"status": "error", "message": "Node name required"}',
                status='error',
                cli_terminated=False
            )
        
        node_name = node_name_match.group(1)
        node_type = type_match.group(1) if type_match else 'epic'
        
        result = self.bot.analyze_node_and_determine_behavior(node_name, node_type)
        
        # Convert ScopeSubmission to dict
        result_dict = result.to_dict() if hasattr(result, 'to_dict') else result
        
        import json
        return CLICommandResponse(
            output=json.dumps(result_dict, indent=2),
            status=result_dict.get('status', 'success'),
            cli_terminated=False
        )
    
    def _format_submit_response(self, result: dict, success_message: str) -> CLICommandResponse:
        if self.mode == 'json':
            import json
            return CLICommandResponse(
                output=json.dumps(result, indent=2),
                status=result.get('status', 'success'),
                cli_terminated=False
            )
        
        if result.get('status') != 'success':
            return CLICommandResponse(
                output=f"Error: {result.get('message', 'Unknown error')}",
                status='error',
                cli_terminated=False
            )
        
        output_lines = self._build_submit_success_lines(result, success_message)
        return CLICommandResponse(
            output='\n'.join(output_lines),
            status='success',
            cli_terminated=False
        )
    
    def _build_submit_success_lines(self, result: dict, header: str) -> list:
        lines = [
            f"[OK] {header}",
            f"  Behavior: {result.get('behavior')}",
            f"  Action: {result.get('action')}",
            f"  Length: {result.get('instructions_length', 0)} characters"
        ]
        cursor_status = result.get('cursor_status', '')
        if cursor_status == 'opened':
            lines.append("  [OK] Cursor chat opened")
        elif cursor_status.startswith('failed'):
            lines.append("  [!] Could not open Cursor chat automatically")
            lines.append("  [!] Open Cursor chat manually and paste (Ctrl+V)")
        elif cursor_status:
            lines.append("  [!] Paste into Cursor chat (Ctrl+V)")
        return lines
    
    def _execute_verb(self, verb: str, args: str, command: str) -> tuple:
        is_navigation_command = verb in ('next', 'back', 'current', 'scope', 'path', 'workspace')
        
        if verb == 'status':
            return self.bot, is_navigation_command
        
        if verb == 'bot':
            return self._handle_bot_command(args), is_navigation_command
        
        if hasattr(self.bot, verb):
            return self._execute_bot_attribute(verb, args)
        
        if '.' in verb and hasattr(self.bot, verb.split('.')[0]):
            return self._execute_domain_object_command(command)
        
        return self._execute_action_or_route(verb, args, command)
    
    def _handle_bot_command(self, args: str) -> dict:
        if not args:
            return {
                'status': 'info',
                'current_bot': self.bot.bot_name,
                'registered_bots': self.bot.bots,
                'message': f"Current bot: {self.bot.bot_name}. Available bots: {', '.join(self.bot.bots)}. Usage: bot <name>"
            }
        
        target_bot_name = args.strip()
        try:
            self.bot.active_bot = target_bot_name
            self.bot = self.bot.active_bot
            return {'status': 'success', 'message': f'Switched to bot: {target_bot_name}', 'bot_name': target_bot_name}
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}
    
    def _execute_bot_attribute(self, verb: str, args: str) -> tuple:
        attr = getattr(self.bot, verb)
        if callable(attr):
            result = attr(args) if args else attr()
            return result, False
        
        from behaviors.behavior import Behavior
        if isinstance(attr, Behavior):
            result = self.bot.execute(attr.name, None)
            return result, True
        
        # Special handling for story_graph property - return the dict, not the object
        if verb == 'story_graph' and hasattr(attr, 'story_graph'):
            return {'status': 'success', 'result': attr.story_graph}, False
        
        return attr, False
    
    def _execute_domain_object_command(self, command: str) -> tuple:
        """Execute commands on domain objects like story_graph.create_epic"""
        from navigation.domain_navigator import DomainNavigator
        
        navigator = DomainNavigator(self.bot)
        result = navigator.navigate(command)
        
        if isinstance(result, dict):
            return result, False
        
        # Handle Instructions objects - return them directly for proper CLI formatting
        if type(result).__name__ == 'Instructions':
            return result, False
        
        return {'status': 'success', 'result': result}, False
    
    def _execute_action_or_route(self, verb: str, args: str, command: str) -> tuple:
        result = self._handle_action_shortcut(verb, args)
        
        rules_response = self._check_rules_auto_submit(verb, result)
        if rules_response:
            return rules_response, False
        
        if result is not None:
            return self._wrap_instructions_result(result)
        
        return self._try_route_to_behavior(verb, command)
    
    def _check_rules_auto_submit(self, verb: str, result) -> CLICommandResponse:
        if verb != 'rules' or result is None:
            return None
        return self._handle_rules_submission(result)
    
    def _submit_rules_to_chat(self) -> dict:
        if self.bot.behaviors.current:
            return self.bot.behaviors.current.submitRules()
        return {'status': 'error', 'message': 'No current behavior set'}
    
    def _format_rules_submit_response(self, submit_result: dict) -> CLICommandResponse:
        output_lines = self._build_submit_success_lines(submit_result, "Rules submitted to chat!")
        return CLICommandResponse(output='\n'.join(output_lines), status='success', cli_terminated=False)
    
    def _wrap_instructions_result(self, result) -> tuple:
        from instructions.instructions import Instructions
        if isinstance(result, Instructions):
            adapter = self._get_adapter_for_domain(result)
            output = adapter.serialize()
            status_adapter = self._get_adapter_for_domain(self.bot)
            output = '\n'.join([output, "", status_adapter.serialize()])
            return CLICommandResponse(output=output, cli_terminated=False), False
        return result, True
    
    def _try_route_to_behavior(self, verb: str, command: str) -> tuple:
        try:
            result = self._route_to_behavior_action(command)
            rules_response = self._check_routed_rules_submit(command, result)
            if rules_response:
                return rules_response, False
            
            # Return as Instructions with navigation flag to trigger status tree display
            # This ensures behavior.action commands show the status tree just like individual commands
            return result, True
        except ValueError:
            return self._build_error_response(verb), False
    
    def _check_routed_rules_submit(self, command: str, result) -> CLICommandResponse:
        if '.rules' not in command.lower():
            return None
        return self._handle_rules_submission(result)
    
    def _handle_rules_submission(self, result) -> CLICommandResponse:
        from instructions.instructions import Instructions
        if not isinstance(result, Instructions):
            return None
        
        submit_result = self._submit_rules_to_chat()
        if submit_result.get('status') == 'success' and self.mode != 'json':
            return self._format_rules_submit_response(submit_result)
        return None
    
    def _build_error_response(self, verb: str) -> CLICommandResponse:
        error_message = f"Unknown command '{verb}'"
        if self.mode == 'json':
            import json
            output = json.dumps({'status': 'error', 'message': error_message, 'command': verb}, indent=2)
        else:
            output = f"ERROR: {error_message}"
        return CLICommandResponse(output=output, status='error', cli_terminated=False)
    
    def _build_response(self, result, is_navigation_command: bool, cli_terminated: bool) -> CLICommandResponse:
        if isinstance(result, CLICommandResponse):
            return result
        
        adapter = self._get_adapter_for_domain(result)
        output = adapter.serialize()
        
        from instructions.instructions import Instructions
        if isinstance(result, Instructions) and self.mode == 'json':
            return self._build_json_instructions_response(output)
        
        if is_navigation_command and not cli_terminated:
            output = self._append_navigation_context(result, output)
        
        return CLICommandResponse(output=output, cli_terminated=cli_terminated)
    
    def _build_json_instructions_response(self, output: str) -> CLICommandResponse:
        import json
        instructions_data = json.loads(output) if isinstance(output, str) else output
        status_adapter = self._get_adapter_for_domain(self.bot)
        status_data = json.loads(status_adapter.serialize())
        unified = {'instructions': instructions_data, 'bot': status_data}
        return CLICommandResponse(output=json.dumps(unified, indent=2), cli_terminated=False)
    
    def _append_navigation_context(self, result, output: str) -> str:
        if self.mode == 'json':
            return self._append_json_navigation_context(result, output)
        return self._append_tty_navigation_context(result, output)
    
    def _append_json_navigation_context(self, result, output: str) -> str:
        import json
        from instructions.instructions import Instructions
        
        result_data = json.loads(output) if isinstance(output, str) else output
        unified = dict(result_data) if isinstance(result_data, dict) else {}
        
        if self._navigation_succeeded(result) and not isinstance(result, Instructions):
            self._add_instructions_to_unified(unified)
        
        status_adapter = self._get_adapter_for_domain(self.bot)
        unified['bot'] = json.loads(status_adapter.serialize())
        return json.dumps(unified, indent=2)
    
    def _append_tty_navigation_context(self, result, output: str) -> str:
        from instructions.instructions import Instructions
        
        parts = [output]
        
        if self._navigation_succeeded(result) and not isinstance(result, Instructions):
            self._add_instructions_to_parts(parts)
        
        status_adapter = self._get_adapter_for_domain(self.bot)
        parts.extend(["", status_adapter.serialize()])
        return '\n'.join(parts)
    
    def _navigation_succeeded(self, result) -> bool:
        if not isinstance(result, dict) or 'status' not in result:
            return True
        return result['status'] not in ['error', 'at_start', 'at_end']
    
    def _add_instructions_to_unified(self, unified: dict) -> None:
        import json
        instructions_result = self.bot.current()
        
        if isinstance(instructions_result, dict) and instructions_result.get('status') == 'error':
            unified['instructions_error'] = instructions_result.get('message', 'Unknown error')
            return
        
        adapter = self._get_adapter_for_domain(instructions_result)
        unified['instructions'] = json.loads(adapter.serialize())
    
    def _add_instructions_to_parts(self, parts: list) -> None:
        instructions_result = self.bot.current()
        
        if isinstance(instructions_result, dict) and instructions_result.get('status') == 'error':
            parts.extend(["", f"ERROR: {instructions_result.get('message', 'Unknown error')}"])
            return
        
        parts.extend(["", "=" * 100, "INSTRUCTIONS", "=" * 100])
        adapter = self._get_adapter_for_domain(instructions_result)
        parts.append(adapter.serialize())
    
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
        from ..actions.action_context import ActionContext
        context = action.context_class() if hasattr(action, 'context_class') else ActionContext()
        
        if args and hasattr(context, 'message'):
            context.message = args
        
        return context
    
    def _build_instructions_from_dict(self, instructions_dict, action):
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
            print("\n\nExiting CLI...")
            sys.exit(0)
