
from agile_bots.src.cli.adapters import TTYAdapter

class TTYAction(TTYAdapter):
    
    def __init__(self, action, is_current: bool = False, is_completed: bool = False):
        self.action = action
        self.is_current = is_current
        self._is_completed = is_completed
    
    @property
    def action_name(self):
        if self.is_current:
            icon = "➤ "
        elif self._is_completed:
            icon = "☑ "
        else:
            icon = "☐ "
        
        description = getattr(self.action, 'description', '')
        
        if description and self.is_current:
            return f"  {icon}{self.add_bold(self.action.action_name)} - {description}"
        elif self.is_current:
            return f"  {icon}{self.add_bold(self.action.action_name)}"
        else:
            return f"  {icon}{self.action.action_name}"
    
    
    @property
    def name(self):
        return self.action.action_name
    
    @property
    def domain_action(self):
        return self.action
    
    def serialize(self) -> str:
        return self.action_name
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
