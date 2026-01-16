from pathlib import Path
from typing import Dict, List, Optional
import json
from .trigger_domain import BehaviorTriggers, ActionTriggers

class BehaviorMatcher:

    def __init__(self, bot_paths, bot_name: Optional[str]=None):
        self.bot_paths = bot_paths
        self.bot_name = bot_name
        self._behavior_triggers: Dict[str, BehaviorTriggers] = {}
        self._action_triggers: Dict[str, ActionTriggers] = {}

    def load_triggers_for_bot(self):
        if self.bot_name not in self._behavior_triggers:
            self._behavior_triggers[self.bot_name] = self._load_behavior_triggers()
            self._action_triggers[self.bot_name] = self._load_action_triggers()

    def match_action_explicit(self, message: str) -> Optional[Dict[str, str]]:
        self.load_triggers_for_bot()
        action_triggers_obj = self._action_triggers.get(self.bot_name)
        for behavior, action_patterns in action_triggers_obj.items():
            for action, patterns in action_patterns.items():
                if self._message_matches_patterns(message, patterns):
                    return {'bot_name': self.bot_name, 'behavior_name': behavior, 'action_name': action, 'match_type': 'bot_behavior_action'}
        return None

    def match_behavior(self, message: str, current_action: Optional[str]) -> Optional[Dict[str, str]]:
        self.load_triggers_for_bot()
        behavior_triggers_obj = self._behavior_triggers.get(self.bot_name)
        for behavior, patterns in behavior_triggers_obj.triggers.items():
            if self._message_matches_patterns(message, patterns):
                return {'bot_name': self.bot_name, 'behavior_name': behavior, 'action_name': current_action, 'match_type': 'bot_and_behavior'}
        return None

    def match_close(self, message: str) -> Optional[Dict[str, str]]:
        close_keywords = ['close', 'done', 'continue', 'next', 'finish', 'complete']
        if any((keyword in message for keyword in close_keywords)):
            return {'bot_name': self.bot_name, 'behavior_name': None, 'action_name': 'close_current_action', 'match_type': 'close'}
        return None

    def _message_matches_patterns(self, message: str, patterns: List[str]) -> bool:
        for pattern in patterns:
            if pattern.lower().strip() in message or message in pattern.lower().strip():
                return True
        return False

    def _load_behavior_triggers(self) -> BehaviorTriggers:
        behaviors_dir = self.bot_paths.python_workspace_root / 'agile_bots' / 'bots' / self.bot_name / 'behaviors'
        behavior_triggers = {}
        for behavior_dir in behaviors_dir.iterdir():
            if behavior_dir.is_dir() and not behavior_dir.name.startswith('_'):
                behavior_name = self._extract_behavior_name(behavior_dir.name)
                patterns = self._load_triggers_from_behavior_file(behavior_dir / 'behavior.json')
                if patterns:
                    behavior_triggers[behavior_name] = patterns
        return BehaviorTriggers(triggers=behavior_triggers)

    def _load_action_triggers(self) -> ActionTriggers:
        behaviors_dir = self.bot_paths.python_workspace_root / 'agile_bots' / 'bots' / self.bot_name / 'behaviors'
        action_triggers = {}
        for behavior_dir in behaviors_dir.iterdir():
            if behavior_dir.is_dir() and not behavior_dir.name.startswith('_'):
                behavior_name = self._extract_behavior_name(behavior_dir.name)
                behavior_action_triggers = self._load_action_triggers_for_behavior(behavior_dir)
                if behavior_action_triggers:
                    action_triggers[behavior_name] = behavior_action_triggers
        return ActionTriggers(triggers=action_triggers)

    def _load_action_triggers_for_behavior(self, behavior_dir: Path) -> Dict[str, List[str]]:
        triggers = {}
        for action_dir in behavior_dir.iterdir():
            self._add_action_triggers_if_valid(action_dir, triggers)
        return triggers
    
    def _add_action_triggers_if_valid(self, action_dir: Path, triggers: Dict[str, List[str]]) -> None:
        if not action_dir.is_dir() or action_dir.name.startswith('_'):
            return
        
        trigger_file = action_dir / 'trigger_words.json'
        try:
            action_name = self._extract_action_name(action_dir.name)
            patterns = self._load_patterns_from_file(trigger_file)
            if patterns:
                triggers[action_name] = patterns
        except FileNotFoundError:
            pass

    def _load_json_from_file(self, file_path: Path) -> dict:
        try:
            content = file_path.read_text(encoding='utf-8')
            return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return {}

    def _load_triggers_from_behavior_file(self, behavior_file: Path) -> list:
        behavior_data = self._load_json_from_file(behavior_file)
        return behavior_data.get('trigger_words', {}).get('patterns', [])

    def _extract_dir_name(self, dir_name: str) -> str:
        return dir_name

    def _extract_behavior_name(self, dir_name: str) -> str:
        return self._extract_dir_name(dir_name)

    def _extract_action_name(self, dir_name: str) -> str:
        return self._extract_dir_name(dir_name)

    def _load_patterns_from_file(self, file_path: Path) -> List[str]:
        data = self._load_json_from_file(file_path)
        return data.get('patterns', [])
