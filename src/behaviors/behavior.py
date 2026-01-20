from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any
from utils import read_json_file
from bot_path import BotPath
from actions.validate.validation_type import ValidationType
if TYPE_CHECKING:
    from bot import BotResult

class Behavior:

    def __init__(self, name: str, bot_paths: BotPath, bot_instance=None):
        if not isinstance(bot_paths, BotPath):
            raise TypeError('bot_paths must be an instance of BotPath')
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_path.parent.mkdir(parents=True, exist_ok=True); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'behavior.py:15','message':'Behavior.__init__ setting bot_name','data':{'name':name,'bot_directory':str(bot_paths.bot_directory),'bot_directory_name':bot_paths.bot_directory.name},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H2'})+'\n'); log_file.close()
        self.bot_name = bot_paths.bot_directory.name
        self.name = name
        self.bot_paths = bot_paths
        self.bot = bot_instance
        self._load_config()   
        self._initialize_from_config() 
        self._guardrails = None
        self._content = None
        self._rules = None
        self._actions = None
        self._trigger_words_obj = None

    def _load_config(self):
        self.behavior_directory = self.bot_paths.bot_directory / 'behaviors' / self.name
        self.config_path = self.behavior_directory / 'behavior.json'
        if not self.config_path.exists():
            raise FileNotFoundError(f'Behavior config not found at {self.config_path}. Each behavior must define its own behavior.json.')
        self._config = read_json_file(self.config_path)

    def _initialize_from_config(self):
        self.description = self._config.get('description', '')
        self.goal = self._config.get('goal', '')
        self.inputs = self._config.get('inputs', [])
        self.outputs = self._config.get('outputs', [])
        self.instructions = self._config.get('instructions', {})
        self.trigger_words = self._config.get('trigger_words', [])
        self.order = self._config.get('order', 999)

    @property
    def base_actions_path(self) -> Path:
        return self.bot_paths.base_actions_directory

    @property
    def actions_workflow(self) -> list:
        actions = self._config.get('actions_workflow', {}).get('actions', [])
        if not isinstance(actions, list):
            return []
        return sorted(actions, key=lambda a: a.get('order', 0))

    @property
    def action_names(self) -> list:
        return [action.get('name', '') for action in self.actions_workflow if action.get('name')]

    @property
    def folder(self) -> Path:
        return self.behavior_directory

    @property
    def is_completed(self) -> bool:
        return False

    def matches_trigger(self, text: str) -> bool:
        return self.trigger_words.matches(text)

    def does_requested_action_match_current(self, requested_action: str) -> tuple[bool, str | None, str | None]:
        self.actions.load_state()
        current_action = self.actions.current
        current_action_name = current_action.action_name if current_action else None
        if current_action_name == requested_action:
            return (True, current_action_name, None)
        expected_next = None
        if current_action:
            next_action = self.actions.next()
            if next_action:
                expected_next = next_action.action_name
        return (False, current_action_name, expected_next)

    @property
    def guardrails(self):
        if self._guardrails is None:
            from actions.guardrails import Guardrails
            self._guardrails = Guardrails(self)
        return self._guardrails

    @property
    def content(self):
        if self._content is None:
            from actions.content import Content
            self._content = Content(self)
        return self._content

    @property
    def rules(self):
        if self._rules is None:
            from actions.rules.rules import Rules
            self._rules = Rules(behavior=self, bot_paths=self.bot_paths)
        return self._rules

    @property
    def actions(self):
        if self._actions is None:
            from actions.actions import Actions
            self._actions = Actions(self)
        return self._actions

    @property
    def trigger_words_obj(self):
        if self._trigger_words_obj is None:
            from ext.trigger_words import TriggerWords
            self._trigger_words_obj = TriggerWords(self)
        return self._trigger_words_obj

    @property
    def validation_type(self) -> ValidationType:
        story_graph_only = {'shape', 'prioritization', 'discovery', 'exploration', 'scenarios'}
        files_only = {'code', 'tests', 'test'}
        
        if self.name in story_graph_only:
            return ValidationType.STORY_GRAPH
        elif self.name in files_only:
            return ValidationType.FILES
        else:
            return ValidationType.BOTH
    
    def __getattr__(self, name: str):
        """
        Dynamically resolve action names as attributes.
        This allows DomainNavigator to access actions like: behavior.build, behavior.clarify, etc.
        """
        # Avoid infinite recursion by checking if _actions exists
        if name.startswith('_') or name in ('_actions', 'actions'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        # Try to find the action by name
        action = self.actions.find_by_name(name)
        if action:
            return action
        
        # If not found, raise AttributeError as expected
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def submitRules(self) -> Dict[str, Any]:
        """Submit behavior rules instructions to AI chat.
        
        Executes the rules action to get instructions, then submits them to chat.
        
        Returns:
            Status dict with success message and submission details
        """
        if not self.bot:
            return {
                'status': 'error',
                'message': 'No bot instance available'
            }
        
        try:
            rules_action = self.actions.find_by_name('rules')
            if not rules_action:
                return {
                    'status': 'error',
                    'message': 'Rules action not found'
                }
            
            from actions.action_context import ActionContext
            context = rules_action.context_class() if hasattr(rules_action, 'context_class') else ActionContext()
            instructions = rules_action.get_instructions(context)
            
            # Submit the instructions using bot's submit_instructions method
            return self.bot.submit_instructions(instructions, self.name, 'rules')
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in submitRules: {str(e)}', exc_info=True)
            return {
                'status': 'error',
                'message': f'Error submitting rules: {str(e)}'
            }