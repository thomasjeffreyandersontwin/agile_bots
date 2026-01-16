from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..bot_path import BotPath

try:
    from tinydb import TinyDB
    TINYDB_AVAILABLE = True
except ImportError:
    TINYDB_AVAILABLE = False
    TinyDB = None

def make_json_serializable(obj: Any) -> Any:
    from agile_bots.src.instructions.instructions import Instructions
    
    if isinstance(obj, Instructions):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    else:
        return obj

@dataclass
class ActionState:
    bot_name: str
    behavior: str
    action: str
    outputs: Optional[Dict[str, Any]] = None
    duration: Optional[int] = None

    @property
    def state_key(self) -> str:
        return f'{self.bot_name}.{self.behavior}.{self.action}'

class ActivityTracker:

    def __init__(self, bot_paths: BotPath, bot_name: str):
        self._bot_paths = bot_paths
        self.bot_name = bot_name

    @property
    def workspace_dir(self) -> Path:
        return self._bot_paths.workspace_directory

    @property
    def file(self) -> Path:
        return self._bot_paths.workspace_directory / 'activity_log.json'

    def track_start(self, state: ActionState):
        if not TINYDB_AVAILABLE:
            return
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with TinyDB(self.file) as db:
            db.insert({'action_state': state.state_key, 'status': 'started', 'timestamp': datetime.now().isoformat()})

    def track_completion(self, state: ActionState):
        if not TINYDB_AVAILABLE:
            return
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with TinyDB(self.file) as db:
            entry = {'action_state': state.state_key, 'status': 'completed', 'timestamp': datetime.now().isoformat()}
            if state.outputs:
                entry['outputs'] = make_json_serializable(state.outputs)
            if state.duration:
                entry['duration'] = state.duration
            db.insert(entry)