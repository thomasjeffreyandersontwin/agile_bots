
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.bot_path.bot_path import BotPath

class JSONBotPath(JSONAdapter):
    
    def __init__(self, bot_path: BotPath):
        self.bot_path = bot_path
    
    @property
    def workspace_directory(self):
        return self.bot_path.workspace_directory
    
    @property
    def bot_directory(self):
        return self.bot_path.bot_directory
    
    @property
    def base_actions_directory(self):
        return self.bot_path.base_actions_directory
    
    @property
    def python_workspace_root(self):
        return self.bot_path.python_workspace_root
    
    @property
    def documentation_path(self):
        return self.bot_path.documentation_path
    
    def to_dict(self) -> dict:
        return {
            'workspace_directory': str(self.bot_path.workspace_directory),
            'bot_directory': str(self.bot_path.bot_directory),
            'base_actions_directory': str(self.bot_path.base_actions_directory),
            'python_workspace_root': str(self.bot_path.python_workspace_root),
            'documentation_path': str(self.bot_path.documentation_path)
        }
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
