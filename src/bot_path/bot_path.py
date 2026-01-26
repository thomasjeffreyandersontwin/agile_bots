from pathlib import Path
import os
import json
import logging
from typing import Dict, Any, Optional
from bot.workspace import get_workspace_directory, get_bot_directory, get_base_actions_directory, get_python_workspace_root
from utils import read_json_file

logger = logging.getLogger(__name__)

class BotPath:

    def __init__(self, workspace_path: Path=None, bot_directory: Path=None):
        self._python_workspace_root = get_python_workspace_root()
        self._bot_directory = Path(bot_directory) if bot_directory else get_bot_directory()
        
        # Determine workspace directory:
        # 1. Use explicitly passed workspace_path (doesn't persist - for tests)
        # 2. Load from bot_config.json (mcp.env.WORKING_AREA)
        # 3. Use environment variable (last resort)
        # NOTE: workspace_directory is independent of bot_directory - don't derive from bot path
        if workspace_path is not None:
            # Explicitly passed - use as-is (for tests, doesn't persist)
            self._workspace_directory = Path(workspace_path).resolve()
        else:
            # Try to load from bot_config.json first
            workspace_from_config = self._load_workspace_from_config()
            if workspace_from_config:
                self._workspace_directory = workspace_from_config
            else:
                # Last resort: use environment variable
                self._workspace_directory = get_workspace_directory()
        self._base_actions_directory = self._load_base_actions_directory()
        self._documentation_path = self._load_documentation_path()

    def _load_workspace_from_config(self) -> Optional[Path]:
        """Load workspace directory from bot_config.json (mcp.env.WORKING_AREA)"""
        if not self._bot_directory:
            return None
            
        config_paths = [
            self._bot_directory / 'bot_config.json',
            self._bot_directory / 'config' / 'bot_config.json'
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    config = read_json_file(config_path)
                    # Check mcp.env.WORKING_AREA first (preferred location)
                    if 'mcp' in config and 'env' in config['mcp']:
                        mcp_env = config['mcp']['env']
                        if 'WORKING_AREA' in mcp_env:
                            workspace_str = mcp_env['WORKING_AREA']
                            if workspace_str:
                                return Path(workspace_str).expanduser().resolve()
                    # Fallback to top-level WORKING_AREA (legacy)
                    if 'WORKING_AREA' in config:
                        workspace_str = config['WORKING_AREA']
                        if workspace_str:
                            return Path(workspace_str).expanduser().resolve()
                except Exception as e:
                    logger.debug(f'Failed to load WORKING_AREA from {config_path}: {e}')
        
        return None
    
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
        
        return self._python_workspace_root / 'base_actions'
    
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
        # Update instance variable only - don't mutate global environment variable
        # This prevents tests from accidentally affecting other instances
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