
import json
from cli.adapters import JSONAdapter
from cli.base_hierarchical_adapter import BaseBotAdapter
from bot.bot import Bot

class JSONBot(BaseBotAdapter, JSONAdapter):
    
    def __init__(self, bot: Bot):
        BaseBotAdapter.__init__(self, bot, 'json')
        self.bot = bot
    
    @property
    def name(self):
        return self.bot.name
    
    @property
    def bot_name(self):
        return self.bot.bot_name
    
    @property
    def bot_directory(self):
        return self.bot.bot_directory
    
    @property
    def workspace_directory(self):
        return self.bot.workspace_directory
    
    @property
    def bot_paths(self):
        return self.bot.bot_paths
    
    @property
    def behaviors(self):
        return self.bot.behaviors
    
    def format_header(self) -> str:
        return ""
    
    def format_bot_info(self) -> str:
        return ""
    
    def format_footer(self) -> str:
        return ""
    
    def serialize(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_dict(self) -> dict:
        result = {
            'name': self.bot.name,
            'bot_directory': str(self.bot.bot_directory),
            'workspace_directory': str(self.bot.workspace_directory),
            'behavior_names': self.bot.behaviors.names if self.bot.behaviors else [],
            'current_behavior': self.bot.behaviors.current.name if self.bot.behaviors and self.bot.behaviors.current else None,
            'current_action': self.bot.current_action_name if hasattr(self.bot, 'current_action_name') else None,
            'available_bots': self.bot.bots,
            'registered_bots': self.bot.bots
        }
        if self._behaviors_adapter:
            result['behaviors'] = self._behaviors_adapter.to_dict() if hasattr(self._behaviors_adapter, 'to_dict') else {}
        
        if hasattr(self.bot, '_scope') and self.bot._scope:
            # Reload scope from file to ensure we have the latest persisted state
            self.bot._scope.load()
            from cli.adapter_factory import AdapterFactory
            scope_adapter = AdapterFactory.create(self.bot._scope, 'json')
            result['scope'] = scope_adapter.to_dict()
        
        return result
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
