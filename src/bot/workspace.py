from pathlib import Path
import os
from ..utils import read_json_file

def get_python_workspace_root() -> Path:
    return Path(__file__).parent.parent.parent.parent

def get_bot_directory() -> Path:
    bot_dir = os.environ.get('BOT_DIRECTORY')
    if not bot_dir:
        raise RuntimeError('BOT_DIRECTORY environment variable is not set. Entry points must bootstrap this before importing other modules.')
    return Path(bot_dir.strip())

def get_workspace_directory() -> Path:
    workspace = os.environ.get('WORKING_AREA')
    if not workspace:
        raise RuntimeError('WORKING_AREA environment variable is not set. Entry points must bootstrap this before importing other modules.')
    return Path(workspace.strip())

def get_base_actions_directory(bot_directory: Path=None) -> Path:
    from ..utils import read_json_file
    
    if bot_directory is None:
        bot_directory = get_bot_directory()
    
    config_paths = [
        bot_directory / 'bot_config.json',
        bot_directory / 'config' / 'bot_config.json'
    ]
    
    python_workspace_root = get_python_workspace_root()
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                config = read_json_file(config_path)
                base_actions_path = config.get('baseActionsPath')
                if base_actions_path:
                    path = Path(base_actions_path)
                    if not path.is_absolute():
                        path = python_workspace_root / base_actions_path
                    return path
            except Exception:
                pass
    
    return python_workspace_root / 'agile_bots' / 'base_actions'

def get_behavior_folder(bot_name: str, behavior: str) -> Path:
    bot_directory = get_bot_directory()
    return bot_directory / 'behaviors' / behavior