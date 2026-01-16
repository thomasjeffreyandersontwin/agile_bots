import dataclasses
from typing import List, Dict
from .description_extractor import DescriptionExtractor
from agile_bots.bots.base_bot.src.actions.help_action import TypeHintConverter
from agile_bots.bots.base_bot.src.actions.action_factory import ActionFactory
from agile_bots.bots.base_bot.src.utils import read_json_file

class ActionDataCollector:
    
    def __init__(self, bot, bot_name: str, bot_directory, description_extractor: DescriptionExtractor):
        self.bot = bot
        self.bot_name = bot_name
        self.bot_directory = bot_directory
        self.description_extractor = description_extractor
        self.action_order = ['clarify', 'strategy', 'build', 'validate', 'render']
    
    def get_behavior_order(self, behavior) -> int:
        return behavior.order
    
    def sort_behaviors_for_display(self, behaviors):
        behaviors_list = list(behaviors)
        behaviors_with_order = []
        for behavior in behaviors_list:
            order = self.get_behavior_order(behavior)
            behaviors_with_order.append((order, behavior))
        behaviors_with_order.sort(key=lambda x: x[0])
        return [behavior for _, behavior in behaviors_with_order]
    
    def get_behavior_actions(self, behavior) -> List[str]:
        return behavior.action_names
    
    def get_action_parameters(self, action_name: str) -> List[str]:
        action_class = ActionFactory.get_action_class(action_name)
        if not action_class:
            return []
        
        context_class = getattr(action_class, 'context_class', None)
        if not context_class or not dataclasses.is_dataclass(context_class):
            return []
        
        params = []
        for field_info in dataclasses.fields(context_class):
            cli_name = f'--{field_info.name.replace("_", "-")}'
            type_hint = TypeHintConverter.to_cli_type(field_info.type)
            params.append(f'{cli_name} <{type_hint}>')
        
        return params
    
    def get_parameter_descriptions(self, action_name: str, parameters: List[str]) -> Dict[str, str]:
        descriptions = {}
        for param in parameters:
            description = self._get_single_parameter_description(action_name, param)
            descriptions[param] = description
        return descriptions
    
    def _get_single_parameter_description(self, action_name: str, param: str) -> str:
        if 'answers' in param or 'key_questions_answered' in param:
            return "Dict mapping question keys to answer strings"
        if 'evidence_provided' in param:
            return "Dict mapping evidence types to evidence content"
        if 'choices' in param or 'decisions_made' in param:
            return "Dict mapping decision criteria keys to selected options/values"
        if 'assumptions' in param or 'assumptions_made' in param:
            return "List of assumption strings"
        if 'scope' in param:
            return self._get_scope_description(action_name)
        return "Optional parameter"
    
    def _get_scope_description(self, action_name: str) -> str:
        if action_name == 'validate':
            return "Scope structure:\n{'type': 'story'|'epic'|'increment'|'all'|'files', 'value': <names|priorities|files>, 'exclude': <patterns>}"
        return "Scope structure:\n{'type': 'story'|'epic'|'increment'|'all', 'value': <names|priorities>}"
    
    def get_action_description(self, action_name: str) -> str:
        description = self.description_extractor.get_action_description(action_name)
        if action_name == 'validate':
            description += '\n\n**NOTE:** For code behavior, validation runs in background. You MUST poll the status file every 10 seconds and report progress until complete.'
        return description
    
    def get_behavior_description(self, behavior_name: str) -> str:
        return self.description_extractor.get_behavior_description(f'{self.bot_name}-{behavior_name}')
