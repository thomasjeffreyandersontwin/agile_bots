from pathlib import Path
from typing import Dict, Set, Optional
import json
from cli.base_hierarchical_adapter import BaseBehaviorsAdapter, BaseBehaviorAdapter
from cli.action_data_collector import ActionDataCollector
from cli.description_extractor import DescriptionExtractor
from cli.formatter import CliTerminalFormatter
from utils import read_json_file

class CursorCommandGenerator(BaseBehaviorsAdapter):
    
    def __init__(self, workspace_root: Path, bot_location: Path, bot=None, bot_name: str = None):
        if not bot:
            raise ValueError("bot is required")
        BaseBehaviorsAdapter.__init__(self, bot.behaviors, 'cursor')
        self.workspace_root = workspace_root
        self.bot_location = bot_location
        self.bot = bot
        self.bot_name = bot_name or (bot.name if bot else 'unknown')
        self.commands_dir: Optional[Path] = None
        self.cli_command: Optional[str] = None
        self.commands: Dict[str, Path] = {}
        self.current_command_files: Set[Path] = set()
        self._formatter: Optional[CliTerminalFormatter] = None
        self._description_extractor: Optional[DescriptionExtractor] = None
        self._data_collector: Optional[ActionDataCollector] = None
    
    @property
    def python_path(self) -> Path:
        return self.workspace_root / 'src'
    
    @property
    def formatter(self) -> CliTerminalFormatter:
        if self._formatter is None:
            self._formatter = CliTerminalFormatter()
        return self._formatter
    
    @property
    def description_extractor(self) -> DescriptionExtractor:
        if self._description_extractor is None:
            self._description_extractor = DescriptionExtractor(self.bot_name, self.bot_directory, self.formatter)
        return self._description_extractor
    
    @property
    def data_collector(self) -> ActionDataCollector:
        if self._data_collector is None:
            self._data_collector = ActionDataCollector(
                bot=self.bot,
                bot_name=self.bot_name,
                bot_directory=self.bot_directory,
                description_extractor=self.description_extractor
            )
        return self._data_collector
    
    def _ensure_commands_directory(self) -> Path:
        commands_dir = self.workspace_root / '.cursor' / 'commands'
        commands_dir.mkdir(parents=True, exist_ok=True)
        return commands_dir
    
    def _generate_base_commands(self) -> None:
        base_command_content = self._build_base_command()
        self.commands[f'{self.bot_name}'] = self._write_command_file(
            self.commands_dir / f'{self.bot_name}.md',
            base_command_content
        )
        
        status_command_content = self._build_status_command()
        self.commands[f'{self.bot_name}_status'] = self._write_command_file(
            self.commands_dir / f'{self.bot_name}_status.md',
            status_command_content
        )
    
    def _build_status_command(self) -> str:
        bot_dir_str = str(self.bot_directory).replace('\\', '\\')
        workspace_str = str(self.workspace_root).replace('\\', '\\')
        
        lines = [
            f"# {self.bot_name}_status - Display Current Bot Status",
            "",
            "Display current position in workflow, active scope, and available commands.",
            "",
            "## Show Status",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'status' | python -m agile_bot.src.cli.cli_main",
        ]
        return "\n".join(lines)
    
    def _build_base_command(self) -> str:
        bot_dir_str = str(self.bot_directory).replace('\\', '\\')
        workspace_str = str(self.workspace_root).replace('\\', '\\')
        
        lines = [
            f"# {self.bot_name} - CLI Status and Navigation",
            "",
            "## Status",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'status' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Help",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'help' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Navigation",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'next' | python -m agile_bot.src.cli.cli_main",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'back' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Scope",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'scope all' | python -m agile_bot.src.cli.cli_main",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'scope \"${{1:story_name}}\"' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Path",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'path ${{1:project_path}}' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Change Bot",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'bot ${{1:bot_name}}' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Exit",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo 'exit' | python -m agile_bot.src.cli.cli_main",
        ]
        return "\n".join(lines)
    
    def _build_behavior_command(self, behavior_name: str) -> str:
        bot_dir_str = str(self.bot_directory).replace('\\', '\\')
        workspace_str = str(self.workspace_root).replace('\\', '\\')
        
        behavior = self.bot.behaviors.find_by_name(behavior_name)
        if not behavior:
            return ""
        
        action_names = []
        if self.data_collector:
            action_names = self.data_collector.get_behavior_actions(behavior)
        
        behavior_name_underscore = behavior_name.replace('-', '_')
        action_options = "|".join(action_names) if action_names else "action"
        
        lines = [
            f"# {self.bot_name}_{behavior_name_underscore} - Navigate to {behavior_name.capitalize()} Behavior",
            "",
            "## Navigate to Behavior",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo '{behavior_name}' | python -m agile_bot.src.cli.cli_main",
            "",
            "## Navigate to Specific Action",
            f"$env:BOT_DIRECTORY = '{bot_dir_str}'; $env:PYTHONPATH = '{workspace_str}'; echo '{behavior_name}.${{1|{action_options}|}}' | python -m agile_bot.src.cli.cli_main",
            "",
        ]
        
        if action_names:
            lines.append("## Available Actions:")
            lines.append("")
            for action_name in action_names:
                action_desc = ""
                if self.data_collector:
                    action_desc = self.data_collector.get_action_description(action_name)
                    if action_desc:
                        short_desc = action_desc.split('\n')[0].split('.')[0]
                        lines.append(f"- {action_name} - {short_desc}")
                    else:
                        lines.append(f"- {action_name}")
                else:
                    lines.append(f"- {action_name}")
        
        return "\n".join(lines)
    
    def _format_action_line(self, action_name: str) -> str:
        if not self.data_collector:
            return f"- {action_name}"
        
        action_desc = self.data_collector.get_action_description(action_name)
        if not action_desc:
            return f"- {action_name}"
        
        short_desc = action_desc.split('\n')[0].split('.')[0]
        return f"- {action_name} - {short_desc}"
    
    def _write_command_file(self, file_path: Path, command: str) -> Path:
        file_path.write_text(command, encoding='utf-8')
        return file_path
    
    def _remove_obsolete_command_files(self) -> None:
        current_file_paths = set(self.commands.values())
        for file_path in self.current_command_files:
            if file_path not in current_file_paths:
                file_path.unlink(missing_ok=True)
    
    def get_commands(self) -> Dict[str, Path]:
        return self.commands
    
    def serialize(self) -> str:
        self.commands_dir = self._ensure_commands_directory()
        self._generate_base_commands()
        
        for behavior_adapter in self._behavior_adapters:
            behavior_adapter.generate_command_file(self.commands_dir, self.commands)
        
        self._remove_obsolete_command_files()
        return ""
    
    def generate(self) -> Dict[str, Path]:
        self.serialize()
        return self.commands
    
    def update_bot_registry(self, cli_python_path: str) -> Path:
        registry_path = self._get_registry_path()
        registry = self._load_registry(registry_path)
        
        if self.bot_name not in registry:
            registry[self.bot_name] = {}
        
        registry[self.bot_name]['cli_path'] = cli_python_path
        
        if 'trigger_patterns' not in registry[self.bot_name]:
            registry[self.bot_name]['trigger_patterns'] = self._load_bot_trigger_patterns()
        
        registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding='utf-8')
        return registry_path
    
    def _get_registry_path(self) -> Path:
        registry_path = self.workspace_root / 'agile_bot' / 'bots' / 'registry.json'
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        return registry_path
    
    def _load_registry(self, registry_path: Path) -> dict:
        if registry_path.exists():
            try:
                return read_json_file(registry_path)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _load_bot_trigger_patterns(self) -> list:
        trigger_file = self.workspace_root / self.bot_location / 'trigger_words.json'
        try:
            trigger_data = read_json_file(trigger_file)
            return trigger_data.get('patterns', [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

class CursorBehaviorWrapper(BaseBehaviorAdapter):
    
    def __init__(self, behavior, workspace_root: Path, bot_location: Path, bot_name: str, is_current: bool, bot, generator_ref):
        self.workspace_root = workspace_root
        self.bot_location = bot_location
        self.bot_name = bot_name
        self.bot = bot
        self.generator_ref = generator_ref
        BaseBehaviorAdapter.__init__(self, behavior, 'cursor', is_current)
    
    def format_behavior_name(self) -> str:
        return self._empty_stub()
    
    def serialize(self) -> str:
        return self._empty_stub()
    
    def _empty_stub(self) -> str:
        """Stub method for interface compatibility - Cursor commands generate files, not text output."""
        return ""
    
    def generate_command_file(self, commands_dir: Path, commands: Dict[str, Path]):
        behavior_command = self.generator_ref._build_behavior_command(self.behavior.name)
        behavior_name_underscore = self.behavior.name.replace('-', '_')
        commands[f'{self.bot_name}_{behavior_name_underscore}'] = self.generator_ref._write_command_file(
            commands_dir / f'{self.bot_name}_{behavior_name_underscore}.md',
            behavior_command
        )