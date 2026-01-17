import sys
import re
import logging
import dataclasses
from pathlib import Path
from typing import Dict, Any, Type, get_origin
from actions.action import Action
from actions.action_context import ActionContext
from actions.action_factory import ActionFactory
from bot.workspace import get_python_workspace_root, get_base_actions_directory

logger = logging.getLogger(__name__)

class TypeHintConverter:
    
    TYPE_MAP = {
        str: "string",
        Path: "path",
        int: "int",
        float: "float",
        bool: "bool",
        dict: "dict",
        list: "list",
        tuple: "tuple",
        set: "set",
    }
    
    ORIGIN_MAP = {
        dict: "dict",
        list: "list",
        tuple: "tuple",
        set: "set",
    }
    
    @classmethod
    def to_cli_type(cls, python_type) -> str:
        if python_type is type(None):
            return "none"
        
        if python_type in cls.TYPE_MAP:
            return cls.TYPE_MAP[python_type]
        
        origin = get_origin(python_type)
        if origin in cls.ORIGIN_MAP:
            return cls.ORIGIN_MAP[origin]
        
        return "value"

class HelpAction(Action):
    context_class: Type[ActionContext] = ActionContext
    
    def do_execute(self, context: ActionContext) -> Dict[str, Any]:
        instructions = self.instructions.copy()
        self._add_help_content_to_display(instructions)
        return {'instructions': instructions.to_dict()}
    
    def _add_help_content_to_display(self, instructions):
        instructions.add_display(f"## Available Cursor Commands for {self.behavior.bot_name}:")
        instructions.add_display('')
        instructions.add_display('---')
        instructions.add_display('')
        command_files = self._get_cursor_command_files()
        if command_files:
            self._add_all_command_help(command_files, instructions)
        instructions.add_display('---')
        instructions.add_display('')
        instructions.add_display('## Action Help')
        instructions.add_display('')
        self._add_action_help(instructions)
        instructions.add_display('---')
        instructions.add_display('')
    
    def _get_cursor_command_files(self):
        repo_root = get_python_workspace_root()
        commands_dir = repo_root / '.cursor' / 'commands'
        if not commands_dir.exists():
            return []
        return list(commands_dir.glob(f'{self.behavior.bot_name}*.md'))
    
    def _add_all_command_help(self, command_files, instructions):
        sorted_commands = self._sort_commands_by_behavior_order(command_files)
        for cmd_file in sorted_commands:
            self._add_command_help(cmd_file, instructions)
    
    def _sort_commands_by_behavior_order(self, command_files):
        from utils import read_json_file
        bot_name = self.behavior.bot_name
        bot_directory = self.behavior.bot_paths.bot_directory
        
        def get_command_order(cmd_file: Path) -> tuple:
            cmd_name = cmd_file.stem
            behavior_name = cmd_name.replace(f'{bot_name}-', '').replace('-', '_')
            if behavior_name in ['', 'continue', 'help', 'get_working_dir', 'set_working_dir'] or cmd_name == bot_name:
                return (0, cmd_name)
            order = self._get_behavior_order(bot_directory, behavior_name)
            return (1, order, cmd_name)
        return sorted(command_files, key=get_command_order)
    
    def _get_behavior_order(self, bot_directory: Path, behavior_name: str) -> int:
        from utils import read_json_file
        behavior_json_path = bot_directory / 'behaviors' / behavior_name / 'behavior.json'
        if not behavior_json_path.exists():
            return 999
        try:
            config = read_json_file(behavior_json_path)
            return config.get('order', 999)
        except Exception:
            logger.debug(f'Failed to read behavior order for {behavior_name}')
            return 999
    
    def _add_command_help(self, cmd_file: Path, instructions):
        cmd_name = cmd_file.stem
        try:
            description = self._get_command_description(cmd_name)
            instructions.add_display(f'## {cmd_name}')
            instructions.add_display('')
            instructions.add_display(description)
            instructions.add_display('')
            instructions.add_display('```')
            instructions.add_display(f'/{cmd_name}')
            instructions.add_display('```')
            instructions.add_display('')
        except Exception as e:
            instructions.add_display(f'## {cmd_name}')
            instructions.add_display('')
            instructions.add_display(f'[ERROR] Error reading command: {e}')
            instructions.add_display('')
    
    def _get_command_description(self, cmd_name: str) -> str:
        bot_name = self.behavior.bot_name
        if cmd_name == bot_name:
            return f"Execute the current action and current behavior in the {bot_name} workflow."
        if cmd_name == f'{bot_name}-continue':
            return "Close current action and continue to next action in workflow"
        if cmd_name == f'{bot_name}-help':
            return "List all available cursor commands and their parameters"
        if cmd_name == f'{bot_name}-get_working_dir':
            return "Get Working Dir"
        if cmd_name == f'{bot_name}-set_working_dir':
            return "Set Working Dir"
        behavior_name = cmd_name.replace(f'{bot_name}-', '')
        description = self._extract_description_from_command_file(cmd_name)
        if description:
            return description
        return self._get_behavior_description(behavior_name)
    
    def _get_behavior_description(self, behavior_name: str) -> str:
        try:
            behavior = self.behavior.bot.behaviors.find_by_name(behavior_name)
            if behavior:
                description = getattr(behavior, 'description', None)
                if description:
                    return description
        except Exception:
            logger.debug(f'Failed to get description for behavior {behavior_name}')
        
        description = self._extract_description_from_command_file(behavior_name)
        if description:
            return description
        
        return f'{behavior_name} behavior'
    
    def _extract_description_from_command_file(self, cmd_name: str) -> str:
        try:
            repo_root = get_python_workspace_root()
            commands_dir = repo_root / '.cursor' / 'commands'
            cmd_file = commands_dir / f'{cmd_name}.md'
            
            if not cmd_file.exists():
                return None
            
            content = cmd_file.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            
            if len(lines) < 3:
                return None
            
            desc_line = lines[2].strip()
            
            if not desc_line or desc_line.startswith('#'):
                return None
            
            return desc_line
        except Exception:
            logger.debug(f'Failed to extract description from command file for {cmd_name}')
            return None
    
    def _add_action_help(self, instructions):
        base_actions_dir = get_base_actions_directory()
        action_order = ['clarify', 'strategy', 'build', 'validate', 'render']
        for action_name in action_order:
            self._add_single_action_help(instructions, base_actions_dir, action_name)
    
    def _get_parameters_from_context_class(self, action_name: str) -> list:
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
            description = self._get_parameter_description(action_name, field_info.name)
            params.append((f'{cli_name} <{type_hint}>', description))
        
        return params
    
    def _get_scope_description(self, action_name: str) -> str:
        if action_name == 'validate':
            return "Scope structure: {'type': 'story'|'epic'|'increment'|'all'|'files', 'value': <names|priorities|files>, 'exclude': <patterns>}"
        return "Scope structure: {'type': 'story'|'epic'|'increment'|'all', 'value': <names|priorities>}"
    
    def _get_parameter_description(self, action_name: str, param_name: str) -> str:
        from actions.clarify.requirements_clarifications import RequirementsClarifications
        from actions.strategy.strategy_decision import StrategyDecision
        
        # Registry mapping parameter name patterns to domain object description methods
        description_registry = [
            (['answers', 'key_questions_answered'], RequirementsClarifications.get_answers_parameter_description),
            (['evidence_provided', 'evidence'], RequirementsClarifications.get_evidence_parameter_description),
            (['choices', 'decisions_made', 'decisions'], StrategyDecision.get_decisions_parameter_description),
            (['assumptions', 'assumptions_made'], StrategyDecision.get_assumptions_parameter_description),
        ]
        
        # Check each pattern in registry
        for patterns, description_method in description_registry:
            if any(pattern in param_name for pattern in patterns):
                return description_method()
        
        # Handle special cases
        if 'scope' in param_name:
            return self._get_scope_description(action_name)
        
        if 'path' in param_name or 'directory' in param_name:
            return "Path to working directory or file"
        
        return "Optional parameter"
    
    def _add_single_action_help(self, instructions, base_actions_dir: Path, action_name: str):
        action_dir = base_actions_dir / action_name
        if not action_dir.exists() or not action_dir.is_dir():
            return
        action_config_file = action_dir / 'action_config.json'
        if not action_config_file.exists():
            return
        try:
            from utils import read_json_file
            action_config = read_json_file(action_config_file)
            description = action_config.get('description', f'{action_name} action')
            instructions.add_display(f'### {action_name}')
            instructions.add_display('')
            instructions.add_display(description)
            instructions.add_display('')
            if action_name == 'validate':
                instructions.add_display('**NOTE:** For code behavior, validation runs in background. You MUST poll the status file every 10 seconds and report progress until complete.')
                instructions.add_display('')
            instructions.add_display('```')
            instructions.add_display(f'/{self.behavior.bot_name}-<behavior> {action_name} [parameters]')
            
            params = self._get_parameters_from_context_class(action_name)
            if params:
                instructions.add_display('')
                for param_name, param_desc in params:
                    instructions.add_display(f'{param_name}:   {param_desc}')
            instructions.add_display('```')
            instructions.add_display('')
        except Exception:
            logger.debug(f'Failed to load action config for {action_name}')
