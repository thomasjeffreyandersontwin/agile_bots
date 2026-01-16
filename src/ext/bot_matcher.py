from pathlib import Path
from typing import Dict, Optional
import json
from .trigger_domain import BotTriggers

class BotMatcher:

    def __init__(self, bot_paths, bot_name: Optional[str]=None):
        self.bot_paths = bot_paths
        self.bot_name = bot_name
        self._bot_registry = self._load_bot_registry()

    def match_bot_from_registry(self, message: str) -> Optional[str]:
        for registry_bot_name, bot_info in self._bot_registry.items():
            patterns = bot_info.get('trigger_patterns', [])
            if not patterns:
                self.bot_name = registry_bot_name
                bot_triggers = self._load_bot_triggers()
                patterns = bot_triggers.patterns
            if self._message_matches_patterns(message, patterns):
                return registry_bot_name
        return None

    def _message_matches_patterns(self, message: str, patterns: list) -> bool:
        for pattern in patterns:
            if pattern.lower().strip() in message or message in pattern.lower().strip():
                return True
        return False

    def _load_bot_registry(self) -> Dict[str, Dict]:
        registry_path = self.bot_paths.python_workspace_root / 'agile_bots' / 'bots' / 'registry.json'
        try:
            content = registry_path.read_text(encoding='utf-8')
            return json.loads(content)
        except (json.JSONDecodeError, IOError, FileNotFoundError):
            return {}

    def _load_bot_triggers(self) -> BotTriggers:
        trigger_file = self.bot_paths.python_workspace_root / 'agile_bots' / 'bots' / self.bot_name / 'trigger_words.json'
        patterns = self._load_patterns_from_file(trigger_file)
        return BotTriggers(patterns=patterns)

    def _load_patterns_from_file(self, file_path: Path) -> list:
        try:
            content = file_path.read_text(encoding='utf-8')
            data = json.loads(content)
            return data.get('patterns', [])
        except (json.JSONDecodeError, IOError, FileNotFoundError):
            return []
