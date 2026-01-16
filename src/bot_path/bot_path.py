from pathlib import Path
import os
import json
import logging
from typing import Dict, Any
from ..bot.workspace import get_workspace_directory, get_bot_directory, get_base_actions_directory, get_python_workspace_root
from ..utils import read_json_file

logger = logging.getLogger(__name__)

class BotPath:

    def __init__(self, workspace_path: Path=None, bot_directory: Path=None):
        self._python_workspace_root = get_python_workspace_root()
        self._workspace_directory = Path(workspace_path) if workspace_path else get_workspace_directory()
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_path.parent.mkdir(parents=True, exist_ok=True); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot_path.py:16','message':'BotPath.__init__ setting bot_directory','data':{'bot_directory_param':str(bot_directory) if bot_directory else None,'bot_directory_param_name':bot_directory.name if bot_directory else None,'BOT_DIRECTORY_env':__import__('os').environ.get('BOT_DIRECTORY')},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H2'})+'\n'); log_file.close()
        self._bot_directory = Path(bot_directory) if bot_directory else get_bot_directory()
        import json; from pathlib import Path as P; log_path = P(r'c:\dev\augmented-teams\.cursor\debug.log'); log_file = open(log_path, 'a', encoding='utf-8'); log_file.write(json.dumps({'location':'bot_path.py:17','message':'BotPath.__init__ bot_directory set','data':{'final_bot_directory':str(self._bot_directory),'final_bot_directory_name':self._bot_directory.name},'timestamp':__import__('time').time()*1000,'sessionId':'debug-session','hypothesisId':'H2'})+'\n'); log_file.close()
        self._base_actions_directory = self._load_base_actions_directory()
        self._documentation_path = self._load_documentation_path()

    def _load_base_actions_directory(self) -> Path:
        config_paths = [
            self._bot_directory / 'bot_config.json',
            self._bot_directory / 'config' / 'bot_config.json'
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    config = read_json_file(config_path)
                    base_actions_path = config.get('baseActionsPath')
                    if base_actions_path:
                        path = Path(base_actions_path)
                        if not path.is_absolute():
                            path = self._python_workspace_root / base_actions_path
                        return path
                except Exception as e:
                    logger.debug(f'Failed to load baseActionsPath from {config_path}: {e}')
        
        return self._python_workspace_root / 'agile_bots' / 'base_actions'
    
    def _load_documentation_path(self) -> Path:
        bot_config_path = self._bot_directory / 'config' / 'bot_config.json'
        if not bot_config_path.exists():
            bot_config_path = self._bot_directory / 'bot_config.json'
        
        if bot_config_path.exists():
            try:
                config = read_json_file(bot_config_path)
                docs_path = config.get('docs_path', 'docs/stories')
                return Path(docs_path)
            except Exception as e:
                logging.getLogger(__name__).debug(f'Failed to load documentation path from {bot_config_path}: {e}')
                raise
        return Path('docs/stories')

    @property
    def workspace_directory(self) -> Path:
        return self._workspace_directory

    @property
    def bot_directory(self) -> Path:
        return self._bot_directory

    @property
    def base_actions_directory(self) -> Path:
        return self._base_actions_directory

    @property
    def python_workspace_root(self) -> Path:
        return self._python_workspace_root

    @property
    def documentation_path(self) -> Path:
        return self._documentation_path

    @property
    def test_path(self) -> Path:
        return Path('test')

    def find_repo_root(self) -> Path:
        return self.python_workspace_root

    def resolve_path_to_absolute(self, path_str: str) -> str:
        path = Path(path_str)
        if path.is_absolute():
            return str(path.resolve())
        absolute_path = path.resolve()
        return str(absolute_path)

    def update_workspace_directory(self, new_path: Path, persist: bool=True) -> Path:
        resolved_path = Path(new_path).expanduser().resolve()
        previous = getattr(self, '_workspace_directory', None)
        os.environ['WORKING_AREA'] = str(resolved_path)
        self._workspace_directory = resolved_path
        if persist:
            self._persist_workspace_directory(resolved_path)
        logger.info(f'Updated working directory to {resolved_path} (previous={previous})')
        return resolved_path

    def is_path_like(self, value: str) -> bool:
        return '/' in value or '\\' in value or ('.' in value and any((value.endswith(ext) for ext in ('.py', '.md', '.json', '.txt', '.yaml', '.yml'))))

    def resolve_path_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        resolved = params.copy()
        self._resolve_list_param(resolved, 'src')
        self._resolve_list_param(resolved, 'test')
        self._resolve_exclude_param(resolved)
        self._resolve_list_param(resolved, 'context_files')
        if 'increment_file' in resolved and isinstance(resolved['increment_file'], str):
            resolved['increment_file'] = self.resolve_path_to_absolute(resolved['increment_file'])
        return resolved

    def _persist_workspace_directory(self, resolved_path: Path) -> None:
        candidate_paths = [
            self._bot_directory / 'bot_config.json',
            self._bot_directory / 'config' / 'bot_config.json'
        ]
        for config_path in candidate_paths:
            if config_path.exists():
                config = read_json_file(config_path)
                self._write_workspace_to_config(config_path, config, resolved_path)
                return
        default_config_path = candidate_paths[0]
        default_config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {'name': self._bot_directory.name, 'mcp': {'env': {}}}
        self._write_workspace_to_config(default_config_path, config, resolved_path)

    def _write_workspace_to_config(self, config_path: Path, config: Dict[str, Any], resolved_path: Path) -> None:
        config.setdefault('mcp', {}).setdefault('env', {})
        config['mcp']['env']['WORKING_AREA'] = str(resolved_path)
        config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')

    def _resolve_list_param(self, resolved: Dict[str, Any], key: str) -> None:
        if key not in resolved:
            return
        value = resolved[key]
        paths = [value] if isinstance(value, str) else value
        resolved[key] = [self.resolve_path_to_absolute(p) for p in paths]

    def _resolve_exclude_param(self, resolved: Dict[str, Any]) -> None:
        if 'exclude' not in resolved:
            return
        value = resolved['exclude']
        if isinstance(value, str):
            resolved['exclude'] = [self.resolve_path_to_absolute(value) if self.is_path_like(value) else value]
        elif isinstance(value, list):
            resolved['exclude'] = [self.resolve_path_to_absolute(p) if self.is_path_like(p) else p for p in value]