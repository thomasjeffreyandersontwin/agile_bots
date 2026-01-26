import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
from datetime import datetime
from behaviors import Behaviors, Behavior
from bot_path import BotPath
from scope.scope import Scope
from help import Help
from navigation import NavigationResult
from exit_result import ExitResult
from utils import read_json_file
from story_graph import StoryMap
__all__ = ['Bot', 'BotResult', 'Behavior']

class BotResult:

    def __init__(self, status: str, behavior: str, action: str, data: Dict[str, Any]=None):
        self.status = status
        self.behavior = behavior
        self.action = action
        self.data = data or {}
        self.executed_instructions_from = f'{behavior}/{action}'

class Bot:
    _active_bot_instance: Optional['Bot'] = None
    _active_bot_name: Optional[str] = None

    def __init__(self, bot_name: str, bot_directory: Path, config_path: Path, workspace_path: Path=None):
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_path.parent.mkdir(parents=True, exist_ok=True); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot.py:24','message':'Bot.__init__ entry','data':{'bot_name':bot_name,'bot_directory_param':str(bot_directory),'bot_directory_name':bot_directory.name if bot_directory else None},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H1'})+'\n'); log_file.close()
        self.name = bot_name
        self.bot_name = bot_name
        self.config_path = Path(config_path)
        
        Bot._active_bot_instance = self
        Bot._active_bot_name = bot_name
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot.py:28','message':'Before BotPaths creation','data':{'bot_directory_to_pass':str(bot_directory)},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H1'})+'\n'); log_file.close()
        
        # Pass workspace_path to BotPath - BotPath will load from bot_config.json if None
        # Tests can pass workspace_path explicitly to override without persisting
        self.bot_paths = BotPath(workspace_path=workspace_path, bot_directory=bot_directory)
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot.py:28','message':'After BotPaths creation','data':{},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H1'})+'\n'); log_file.close()
        bot_config_path = self.bot_paths.bot_directory / 'bot_config.json'
        if not bot_config_path.exists():
            raise FileNotFoundError(f'Bot config not found at {bot_config_path}')
        self._config = read_json_file(bot_config_path)
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot.py:33','message':'Before Behaviors creation','data':{},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H1'})+'\n'); log_file.close()
        allowed_behaviors = self._config.get('behaviors')
        self.behaviors = Behaviors(bot_name, self.bot_paths, allowed_behaviors=allowed_behaviors)
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot.py:33','message':'After Behaviors creation','data':{'behavior_count':len(self.behaviors._behaviors) if self.behaviors else 0},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H1'})+'\n'); log_file.close()
        self.behaviors._bot_instance = self
        for behavior in self.behaviors:
            behavior.bot = self
            behavior.bot_name = self.bot_name
        
        self._scope = Scope(self.bot_paths.workspace_directory, self.bot_paths)
        self._scope.load()
        
        self._story_graph = None
        
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot.py:37','message':'Bot.__init__ exit','data':{},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H1'})+'\n'); log_file.close()

    @property
    def base_actions_path(self) -> Path:
        return self.bot_paths.base_actions_directory

    @property
    def description(self) -> str:
        return self._config.get('description', '')

    @property
    def goal(self) -> str:
        return self._config.get('goal', '')

    @property
    def instructions(self) -> List[str]:
        return self._config.get('instructions', [])

    @property
    def mcp(self) -> Dict[str, Any]:
        return self._config.get('mcp', {})

    @property
    def trigger_words(self) -> List[str]:
        return self._config.get('trigger_words', [])

    @property
    def working_area(self) -> Optional[str]:
        return self._config.get('WORKING_AREA')
    
    @property
    def bot_directory(self) -> Path:
        return self.bot_paths.bot_directory
    
    @property
    def workspace_directory(self) -> Path:
        return self.bot_paths.workspace_directory

    @property
    def story_map(self) -> StoryMap:
        """Lazy-load and return the story map from workspace.
        
        Returns:
            StoryMap: The loaded story map with Epic/SubEpic/Story hierarchy
            
        Raises:
            FileNotFoundError: If story-graph.json doesn't exist in workspace
        """
        if self._story_graph is None:
            story_graph_path = self.bot_paths.workspace_directory / 'docs' / 'stories' / 'story-graph.json'
            if not story_graph_path.exists():
                raise FileNotFoundError(
                    f'Story graph not found at {story_graph_path}. '
                    f'Please create a story-graph.json file in the docs/stories directory.'
                )
            
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                story_graph_data = json.load(f)
            
            self._story_graph = StoryMap(story_graph_data, bot=self)
        
        return self._story_graph
    
    def reload_story_graph(self) -> dict:
        """Clear the cached story graph to force reload on next access.
        
        Returns:
            dict: Status message indicating the cache was cleared
        """
        self._story_graph = None
        return {'status': 'success', 'message': 'Story graph cache cleared'}
    
    # Backward compatibility alias
    @property
    def story_graph(self) -> StoryMap:
        """Deprecated: Use story_map instead."""
        return self.story_map

    @property
    def progress_path(self) -> str:
        if self.behaviors.current:
            behavior = self.behaviors.current
            if behavior.actions.current_action_name:
                return f"{behavior.name}.{behavior.actions.current_action_name}"
            else:
                return behavior.name
        return "idle"
    
    @property
    def stage_name(self) -> str:
        if not self.behaviors.current:
            return "Idle"
        elif not self.behaviors.current.actions.current_action_name:
            return "Ready"
        else:
            return "In Progress"
    
    @property
    def commands(self) -> 'Help':
        return self.help()
    
    @property
    def current_behavior_name(self) -> str:
        return self.behaviors.current.name if self.behaviors.current else None
    
    @property
    def current_action_name(self) -> str:
        if self.behaviors.current and self.behaviors.current.actions.current_action_name:
            return self.behaviors.current.actions.current_action_name
        return None
    
    @property
    def bots(self) -> List[str]:
        registered_bots = []
        
        bots_parent_dir = self.bot_paths.bot_directory.parent
        if not (bots_parent_dir.exists() and bots_parent_dir.is_dir()):
            return []
        
        for bot_dir in bots_parent_dir.iterdir():
            if not bot_dir.is_dir():
                continue
            
            bot_config = bot_dir / 'bot_config.json'
            if bot_config.exists():
                registered_bots.append(bot_dir.name)
        
        return sorted(registered_bots)
    
    @property
    def active_bot(self) -> 'Bot':
        return Bot._active_bot_instance if Bot._active_bot_instance else self
    
    @active_bot.setter
    def active_bot(self, bot_name: str):
        registered_bots = self.bots
        
        if bot_name not in registered_bots:
            raise ValueError(
                f"Bot '{bot_name}' not found. Available bots: {', '.join(registered_bots)}"
            )
        
        if bot_name == Bot._active_bot_name:
            return
        
        bots_parent_dir = self.bot_paths.bot_directory.parent
        new_bot_dir = bots_parent_dir / bot_name
        new_config_path = new_bot_dir / 'bot_config.json'
        
        if not new_config_path.exists():
            raise FileNotFoundError(f"Bot config not found at {new_config_path}")
        
        Bot(
            bot_name=bot_name,
            bot_directory=new_bot_dir,
            config_path=new_config_path
        )

    def help(self, topic: Optional[str] = None):
        from help.help import Help
        
        return Help(bot=self)
    
    def exit(self) -> Dict[str, Any]:
        return {
            'status': 'exit',
            'message': 'Exiting bot session. Goodbye!'
        }
    
    
    def current(self) -> Dict[str, Any]:
        if not self.behaviors.current:
            return {
                'status': 'error',
                'message': 'No current behavior'
            }
        
        behavior = self.behaviors.current
        if not behavior.actions.current:
            return {
                'status': 'error',
                'message': 'No current action'
            }
        
        action = behavior.actions.current
        
        try:
            from actions.action_context import ActionContext
            context = action.context_class() if hasattr(action, 'context_class') else ActionContext()
            instructions = action.get_instructions(context)
            
            return instructions
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error getting instructions: {str(e)}'
            }
    
    def _clear_scope_and_return_result(self, message: str):
        self._scope.clear()
        self._scope.save()
        from scope.scope_command_result import ScopeCommandResult
        return ScopeCommandResult(
            status='success',
            message=message,
            scope=self._scope
        )
    
    def _normalize_scope_filter(self, scope_filter: str) -> str:
        scope_filter_lower = scope_filter.lower().strip()
        if scope_filter_lower.startswith('set '):
            scope_filter = scope_filter[4:].strip()
        
        scope_filter = scope_filter.strip()
        if (scope_filter.startswith('"') and scope_filter.endswith('"')) or \
           (scope_filter.startswith("'") and scope_filter.endswith("'")):
            scope_filter = scope_filter[1:-1]
        
        return scope_filter.strip()
    
    def _determine_scope_type(self, prefix: str):
        from scope.scope import ScopeType
        
        if prefix in ('file', 'files'):
            return ScopeType.FILES
        elif prefix in ('story', 'epic'):
            return ScopeType.STORY
        elif prefix == 'increment':
            return ScopeType.INCREMENT
        else:
            return ScopeType.STORY
    
    def _looks_like_file_path(self, values: list) -> bool:
        import os
        return any(os.path.isabs(v) or '\\' in v or '/' in v for v in values)
    
    def _parse_delimited_scope(self, scope_filter: str):
        delimiter = '=' if '=' in scope_filter else ':'
        prefix, value_part = scope_filter.split(delimiter, 1)
        
        prefix = prefix.strip().lower()
        value_part = value_part.strip()
        scope_values = [v.strip() for v in value_part.split(',') if v.strip()]
        
        scope_type = self._determine_scope_type(prefix)
        if prefix in ('story', 'epic'):
            prefix = prefix  # Keep original
        elif prefix not in ('file', 'files', 'increment'):
            prefix = 'story'  # Default
        
        return scope_type, prefix, scope_values
    
    def _parse_spaced_scope(self, scope_filter: str):
        parts = scope_filter.split(None, 1)
        potential_prefix = parts[0].lower()
        
        if potential_prefix in ('story', 'epic', 'increment', 'file', 'files'):
            prefix = potential_prefix
            value_part = parts[1] if len(parts) > 1 else ''
            scope_values = [v.strip() for v in value_part.split(',') if v.strip()]
            scope_type = self._determine_scope_type(prefix)
            return scope_type, prefix, scope_values
        
        # No recognized prefix - auto-detect
        scope_values = [v.strip() for v in scope_filter.split(',') if v.strip()]
        if self._looks_like_file_path(scope_values):
            return self._determine_scope_type('files'), 'files', scope_values
        else:
            return self._determine_scope_type('story'), 'story', scope_values
    
    def _parse_undelimited_scope(self, scope_filter: str):
        scope_values = [v.strip() for v in scope_filter.split(',') if v.strip()]
        
        if self._looks_like_file_path(scope_values):
            return self._determine_scope_type('files'), 'files', scope_values
        else:
            return self._determine_scope_type('story'), 'story', scope_values
    
    def scope(self, scope_filter: Optional[str] = None):
        from scope.scope import ScopeType
        
        if scope_filter is None:
            return self._scope
        
        scope_filter = self._normalize_scope_filter(scope_filter)
        scope_filter_lower = scope_filter.lower()
        
        # Handle special commands
        if scope_filter_lower == 'clear':
            return self._clear_scope_and_return_result('Scope cleared')
        
        if scope_filter_lower == 'all':
            return self._clear_scope_and_return_result('Scope cleared (set to all)')
        
        if scope_filter_lower == 'showall':
            self._scope.filter(ScopeType.SHOW_ALL, [])
            self._scope.save()
            from scope.scope_command_result import ScopeCommandResult
            return ScopeCommandResult(
                status='success',
                message='Scope set to show all',
                scope=self._scope
            )
        
        # Parse scope filter based on format
        if '=' in scope_filter or ':' in scope_filter:
            scope_type, prefix, scope_values = self._parse_delimited_scope(scope_filter)
        elif ' ' in scope_filter:
            scope_type, prefix, scope_values = self._parse_spaced_scope(scope_filter)
        else:
            scope_type, prefix, scope_values = self._parse_undelimited_scope(scope_filter)
        
        self._scope.filter(scope_type, scope_values)
        self._scope.save()
        
        from scope.scope_command_result import ScopeCommandResult
        return ScopeCommandResult(
            status='success',
            message=f'Scope set to {prefix}: {", ".join(scope_values)}',
            scope=self._scope
        )
    
    def workspace(self, directory: Optional[str] = None) -> Dict[str, Any]:
        return self.path(directory)
    
    def path(self, directory: Optional[str] = None) -> Dict[str, Any]:
        if directory is None:
            current_path = self.bot_paths.workspace_directory
            return {
                'status': 'success',
                'path': str(current_path),
                'message': f'Current working directory: {current_path}'
            }
        
        new_path = Path(directory)
        if not new_path.is_absolute():
            new_path = self.bot_paths.workspace_directory / new_path
        
        if not new_path.exists():
            return {
                'status': 'error',
                'message': f'Directory does not exist: {new_path}'
            }
        
        self.bot_paths.update_workspace_directory(new_path, persist=True)
        
        self._scope = Scope(self.bot_paths.workspace_directory, self.bot_paths)
        self._scope.load()
        
        return {
            'status': 'success',
            'path': str(new_path),
            'message': f'Working directory set to: {new_path}'
        }

    def _navigate_and_save(self, behavior, action_name: str, message_prefix: str = "Moved to") -> Dict[str, Any]:
        behavior.actions.navigate_to(action_name)
        self.behaviors.save_state()
        return {
            'status': 'success',
            'message': f'{message_prefix} {behavior.name}.{action_name}',
            'behavior': behavior.name,
            'action': action_name
        }
    
    def next(self) -> Dict[str, Any]:
        if not self.behaviors.current:
            return {
                'status': 'error',
                'message': 'No behavior is currently active. Use a behavior.action command to start.'
            }
        
        behavior = self.behaviors.current
        current_action = behavior.actions.current_action_name
        
        if not current_action:
            if behavior.action_names:
                first_action = behavior.action_names[0]
                return self._navigate_and_save(behavior, first_action)
            else:
                return {
                    'status': 'error',
                    'message': f'Behavior {behavior.name} has no actions'
                }
        
        action_names = behavior.action_names
        try:
            current_index = action_names.index(current_action)
            if current_index < len(action_names) - 1:
                next_action = action_names[current_index + 1]
                return self._navigate_and_save(behavior, next_action)
            else:
                advance_result = self.behaviors.advance()
                return advance_result
        except ValueError:
            return {
                'status': 'error',
                'message': f'Current action {current_action} not found in behavior'
            }
    
    def back(self) -> Dict[str, Any]:
        if not self.behaviors.current:
            return {
                'status': 'error',
                'message': 'No behavior is currently active'
            }
        
        behavior = self.behaviors.current
        current_action = behavior.actions.current_action_name
        
        if not current_action:
            return {
                'status': 'error',
                'message': 'No current action to go back from'
            }
        
        action_names = behavior.action_names
        try:
            current_index = action_names.index(current_action)
            if current_index > 0:
                prev_action = action_names[current_index - 1]
                return self._navigate_and_save(behavior, prev_action, "Moved back to")
            else:
                return {
                    'status': 'info',
                    'message': f'Already at first action in {behavior.name}',
                    'behavior': behavior.name,
                    'action': current_action
                }
        except ValueError:
            return {
                'status': 'error',
                'message': f'Current action {current_action} not found in behavior'
            }
    
    def execute(self, behavior_name: str, action_name: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        behavior = self.behaviors.find_by_name(behavior_name)
        if not behavior:
            return {
                'status': 'error',
                'message': f'Behavior not found: {behavior_name}',
                'available_behaviors': [b.name for b in self.behaviors]
            }
        
        self.behaviors.navigate_to(behavior_name)
        
        if action_name:
            try:
                behavior.actions.navigate_to(action_name)
            except ValueError:
                return {
                    'status': 'error',
                    'message': f'Action not found: {action_name}',
                    'available_actions': behavior.action_names
                }
        else:
            if not behavior.actions.current_action_name:
                if behavior.action_names:
                    behavior.actions.navigate_to(behavior.action_names[0])
                else:
                    return {
                        'status': 'error',
                        'message': f'Behavior {behavior_name} has no actions'
                    }
        
        action = behavior.actions.current
        if not action:
            return {
                'status': 'error',
                'message': f'No current action in {behavior_name}'
            }
        
        self.behaviors.save_state()
        
        try:
            from actions.action_context import ActionContext
            context = action.context_class() if hasattr(action, 'context_class') else ActionContext()
            
            if params:
                for key, value in params.items():
                    setattr(context, key, value)
            
            instructions = action.get_instructions(context)
            
            return instructions
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error executing {behavior_name}.{action.action_name}: {str(e)}'
            }
    
    def save(self, answers: Optional[Dict[str, str]] = None,
             evidence_provided: Optional[Dict[str, str]] = None,
             decisions: Optional[Dict[str, str]] = None,
             assumptions: Optional[List[str]] = None) -> Dict[str, Any]:
        from actions.clarify.requirements_clarifications import RequirementsClarifications
        from actions.clarify.required_context import RequiredContext
        from actions.strategy.strategy_decision import StrategyDecision
        from actions.strategy.strategy import Strategy
        
        current_behavior = self.behaviors.current
        if not current_behavior:
            return {
                'status': 'error',
                'message': 'No current behavior set'
            }
        
        try:
            saved_items = []
            
            if answers or evidence_provided:
                required_context = RequiredContext(current_behavior.folder)
                clarifications = RequirementsClarifications(
                    behavior_name=current_behavior.name,
                    bot_paths=current_behavior.bot_paths,
                    required_context=required_context,
                    key_questions_answered=answers or {},
                    evidence_provided=evidence_provided or {},
                    context=None
                )
                clarifications.save()
                if answers:
                    saved_items.append('answers')
                if evidence_provided:
                    saved_items.append('evidence')
            
            if decisions or assumptions:
                strategy = Strategy(current_behavior.folder)
                strategy_decision = StrategyDecision(
                    behavior_name=current_behavior.name,
                    bot_paths=current_behavior.bot_paths,
                    strategy=strategy,
                    decisions_made=decisions or {},
                    assumptions_made=assumptions or []
                )
                strategy_decision.save()
                if decisions:
                    saved_items.append('decisions')
                if assumptions:
                    saved_items.append('assumptions')
            
            if not saved_items:
                return {
                    'status': 'error',
                    'message': 'No data provided to save'
                }
            
            return {
                'status': 'success',
                'message': f"Saved {', '.join(saved_items)} for {current_behavior.name}",
                'behavior': current_behavior.name,
                'saved': saved_items
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error saving: {str(e)}'
            }
    
    def submit_behavior_rules(self, behavior_name: str) -> Dict[str, Any]:
        saved_behavior = self.behaviors.current.name if self.behaviors.current else None
        saved_action = self.behaviors.current.actions.current_action_name if self.behaviors.current else None
        
        try:
            behavior = self.behaviors.find_by_name(behavior_name)
            if not behavior:
                return {
                    'status': 'error',
                    'message': f'Behavior not found: {behavior_name}'
                }
            
            self.behaviors.navigate_to(behavior_name)
            
            # Submit the rules using behavior.submitRules()
            submit_result = behavior.submitRules()
            
            if saved_behavior and saved_action:
                try:
                    self.execute(saved_behavior, saved_action)
                except Exception as e:
                    logger.warning(f'Failed to restore saved behavior/action state: {str(e)}')
            
            return submit_result
            
        except Exception as e:
            logger.error(f'Error in submit_behavior_rules: {str(e)}', exc_info=True)
            return {
                'status': 'error',
                'message': f'Error getting rules for {behavior_name}: {str(e)}'
            }
    
    def submit_instructions(self, instructions, behavior_name: str = None, action_name: str = None) -> Dict[str, Any]:
        display_content = instructions.display_content
        if not display_content:
            return {
                'status': 'error',
                'message': 'No instructions available to submit'
            }
        
        if isinstance(display_content, list):
            content_str = '\n'.join(display_content)
        else:
            content_str = str(display_content)
        
        clipboard_status = 'failed'
        cursor_status = 'not_attempted'
        
        try:
            import pyperclip
            import pyautogui
            import time
            import platform

            pyperclip.copy(content_str)
            clipboard_status = 'success'
            time.sleep(0.2)

            cursor = os.environ.get('IDE').lower() == 'cursor'
            mac = platform.system().lower() == 'darwin'            

            ## activate copilot chat window
            if (cursor == True): ## we're using cursor
                if (mac == True):
                    pyautogui.hotkey('command', 'l')
                else:
                    pyautogui.hotkey('ctrl', 'l')

            else: # assume we're using VS Code
                if (mac == True):
                    pyautogui.hotkey('ctrl', 'command', 'i')
                else:
                    pyautogui.hotkey('ctrl', 'alt', 'i')
            time.sleep(0.3)

            ## paste
            if (mac == True):
                pyautogui.hotkey('command', 'v')
            else:
                pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            
            cursor_status = 'opened'
            
        except ImportError as e:
            clipboard_status = 'failed'
            cursor_status = f'failed: pyautogui/pyperclip not installed - {str(e)}'
        except Exception as e:
            cursor_status = f'failed: {str(e)}'
        
        if not behavior_name:
            behavior_name = getattr(instructions, 'behavior_name', 
                                   self.behaviors.current.name if self.behaviors.current else 'unknown')
        if not action_name:
            action_name = getattr(instructions, 'action_name', 'unknown')
        
        return {
            'status': 'success',
            'message': f'Instructions submitted for {behavior_name}.{action_name}',
            'behavior': behavior_name,
            'action': action_name,
            'timestamp': datetime.now().isoformat(),
            'clipboard_status': clipboard_status,
            'cursor_status': cursor_status,
            'instructions_length': len(content_str),
            'instructions': content_str
        }
    
    def submit_current_action(self) -> Dict[str, Any]:
        current_behavior = self.behaviors.current
        if not current_behavior:
            return {
                'status': 'error',
                'message': 'No current behavior set'
            }
        
        current_action_name = current_behavior.actions.current_action_name
        if not current_action_name:
            return {
                'status': 'error',
                'message': 'No current action set'
            }
        
        try:
            action = current_behavior.actions.find_by_name(current_action_name)
            if not action:
                return {
                    'status': 'error',
                    'message': f'Action {current_action_name} not found'
                }
            
            instructions = action.get_instructions()
            
            # Use the submit_instructions method to do the actual submission
            return self.submit_instructions(instructions, current_behavior.name, current_action_name)
            
        except Exception as e:
            logger.error(f'Error in submit_current_action: {str(e)}', exc_info=True)
            return {
                'status': 'error',
                'message': f'Error submitting instructions: {str(e)}'
            }
    

    def tree(self) -> str:
        lines = []
        behaviors_list = list(self.behaviors)
        
        for i, behavior in enumerate(behaviors_list):
            is_last_behavior = (i == len(behaviors_list) - 1)
            behavior_prefix = "Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬" if is_last_behavior else "Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬"
            is_current_behavior = (self.behaviors.current and behavior.name == self.behaviors.current.name)
            behavior_marker = "➤ " if is_current_behavior else ""
            lines.append(f"{behavior_prefix} {behavior_marker}{behavior.name}")
            
            action_names = behavior.action_names
            for j, action in enumerate(action_names):
                is_last_action = (j == len(action_names) - 1)
                action_prefix = "    Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬" if is_last_behavior else "Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬" if is_last_action else "Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬"
                if not is_last_behavior and not is_last_action:
                    action_prefix = "Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬"
                is_current_action = (is_current_behavior and 
                                   behavior.actions.current_action_name == action)
                action_marker = "➤ " if is_current_action else ""
                lines.append(f"{action_prefix} {action_marker}{action}")
        
        return "\n".join(lines)
    
    def pos(self) -> Dict[str, Any]:
        if not self.behaviors.current:
            return {
                'status': 'error',
                'message': 'No behavior is currently active'
            }
        
        behavior = self.behaviors.current
        action = behavior.actions.current_action_name
        
        if not action:
            return {
                'status': 'error',
                'message': f'No action is currently active in {behavior.name}'
            }
        
        return {
            'status': 'success',
            'behavior': behavior.name,
            'action': action,
            'position': f'{behavior.name}.{action}'
        }

    def __getattr__(self, name: str):
        # Special handling for story_map/story_graph property
        # This shouldn't be needed, but there seems to be an issue with property lookup
        # in certain test scenarios where __getattr__ is called before the property is found
        if name == 'story_map':
            # Directly call the property getter using type(self) to avoid recursion
            return type(self).story_map.fget(self)
        if name == 'story_graph':
            # Backward compatibility: redirect to story_map
            return type(self).story_map.fget(self)
        
        behavior = self.behaviors.find_by_name(name)
        if behavior:
            # Navigate to the behavior when accessed
            self.behaviors.navigate_to(name)
            return behavior
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
