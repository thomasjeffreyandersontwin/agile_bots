import logging
import traceback
import sys
from pathlib import Path
from typing import Optional
from agile_bots.bots.base_bot.src.bot.workspace import get_base_actions_directory
from agile_bots.src.utils import read_json_file
import json

class DescriptionExtractor:

    def __init__(self, bot_name: str, bot_directory: Path, formatter):
        self.bot_name = bot_name
        self.bot_directory = bot_directory
        self.formatter = formatter

    def get_behavior_description(self, cmd_name: str) -> str:
        if cmd_name == self.bot_name:
            bot_desc = self.get_bot_description()
            if bot_desc:
                return bot_desc
        behavior_name = cmd_name.replace(f'{self.bot_name}-', '').replace('-', '_')
        if behavior_name in ['continue', 'help']:
            return self.get_special_behavior_description(behavior_name)
        return self.get_behavior_description_from_file(behavior_name)

    def get_bot_description(self) -> Optional[str]:
        bot_config_path = self.bot_directory / 'bot_config.json'
        if not bot_config_path.exists():
            return None
        try:
            bot_config = read_json_file(bot_config_path)
            cmd_desc = bot_config.get('command description.') or bot_config.get('command_description') or bot_config.get('commandDescription')
            return cmd_desc if cmd_desc else None
        except Exception as e:
            logging.getLogger(__name__).debug(f'Failed to read bot config: {e}')
            return None

    def get_special_behavior_description(self, behavior_name: str) -> str:
        if behavior_name == 'continue':
            return 'Close current action and continue to next action in workflow'
        if behavior_name == 'help':
            return 'List all available cursor commands and their parameters'
        return behavior_name.replace('_', ' ').title()

    def get_behavior_description_from_file(self, behavior_name: str) -> str:
        behavior_file_path = self.bot_directory / 'behaviors' / behavior_name / 'behavior.json'
        if not behavior_file_path.exists():
            return behavior_name.replace('_', ' ').title()
        try:
            behavior_data = read_json_file(behavior_file_path)
            desc = self.extract_behavior_description_from_data(behavior_data)
            if desc:
                return desc
        except Exception as e:
            fmt = self.formatter
            print(f"\n{fmt.format_error(f'**ERROR in _get_behavior_description for {behavior_name}:**')}")
            traceback.print_exc()
            sys.stdout.flush()
        return behavior_name.replace('_', ' ').title()

    def extract_behavior_description_from_data(self, behavior_data: dict) -> Optional[str]:
        instructions = behavior_data.get('instructions', [])
        if instructions:
            return '\n'.join(instructions) if isinstance(instructions, list) else str(instructions)
        description_parts = []
        if behavior_data.get('description'):
            description_parts.append(behavior_data['description'])
        if behavior_data.get('goal'):
            description_parts.append(behavior_data['goal'])
        if behavior_data.get('outputs') and len(description_parts) < 3:
            outputs = behavior_data['outputs']
            if isinstance(outputs, str):
                first_output = outputs.split(',')[0].strip()
                description_parts.append(f'Outputs: {first_output}')
        return ' | '.join(description_parts[:3]) if description_parts else None

    def get_action_description(self, action_name: str) -> str:
        base_actions_dir = get_base_actions_directory()
        action_prefixes = {'clarify': 'clarify', 'strategy': 'strategy', 'build': 'build', 'render': 'render', 'validate': 'validate'}
        action_folder = action_prefixes.get(action_name, action_name)
        config_path = base_actions_dir / action_folder / 'action_config.json'
        if not config_path.exists():
            return action_name.replace('_', ' ').title()
        try:
            config = json.loads(config_path.read_text(encoding='utf-8'))
            if config.get('description'):
                return config.get('description')
            desc = self.extract_first_instruction(config.get('instructions', []))
            if desc:
                return desc
        except Exception as e:
            print(f'\n**ERROR in _get_action_description for {action_name}:**')
            traceback.print_exc()
            sys.stdout.flush()
        return action_name.replace('_', ' ').title()

    def extract_first_instruction(self, instructions: list) -> Optional[str]:
        if not isinstance(instructions, list):
            return None
        for line in instructions:
            if not line or line.startswith('**') or len(line.strip()) <= 10:
                continue
            desc = line.strip()
            return desc[:77] + '...' if len(desc) > 80 else desc
        return None

    def get_action_names_from_behavior(self, behavior_name: str) -> Optional[str]:
        behavior_file_path = self.bot_directory / 'behaviors' / behavior_name / 'behavior.json'
        if not behavior_file_path.exists():
            return None
        try:
            behavior_data = read_json_file(behavior_file_path)
            actions = behavior_data.get('actions_workflow', {}).get('actions', [])
            action_names = [a.get('name', '') for a in actions if a.get('name')]
            return '|'.join(action_names) if action_names else None
        except Exception:
            return None
