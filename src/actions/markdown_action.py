
from agile_bots.src.cli.adapters import MarkdownAdapter

class MarkdownAction(MarkdownAdapter):
    
    def __init__(self, action, is_current: bool = False, is_completed: bool = False):
        self.action = action
        self.is_current = is_current
        self.is_completed = is_completed
    
    @property
    def action_name(self):
        is_completed = getattr(self.action, 'is_completed', False)
        
        if self.is_current:
            marker = "➤"
        elif is_completed:
            marker = "[X]"
        else:
            marker = "[ ]"
        
        description = getattr(self.action, 'description', '')
        
        if description and self.is_current:
            return f"  {marker} **{self.action.action_name}** - {description}"
        elif self.is_current:
            return f"  {marker} **{self.action.action_name}**"
        else:
            return f"  {marker} {self.action.action_name}"
    
    
    def serialize(self) -> str:
        return self.action_name
