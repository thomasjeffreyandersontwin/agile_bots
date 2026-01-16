
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.cli.base_hierarchical_adapter import BaseActionsAdapter

class TTYActions(BaseActionsAdapter, TTYAdapter):
    
    def __init__(self, actions):
        BaseActionsAdapter.__init__(self, actions, 'tty')
        self.actions = actions
    
    @property
    def current(self):
        if self.actions.current:
            from agile_bots.src.actions.tty_action import TTYAction
            action_adapter = TTYAction(self.actions.current, is_current=True)
            return action_adapter.serialize()
        return ""
    
    @property
    def names(self):
        current_action_name = self.actions.current.action_name if self.actions.current else None
        names_list = []
        
        for name in self.actions.names:
            if name == current_action_name:
                names_list.append(self.add_bold(name))
            else:
                names_list.append(name)
        
        if hasattr(self.actions, '_non_workflow_actions'):
            for action in self.actions._non_workflow_actions:
                name = action.action_name
                names_list.append(name)
        
        return " | ".join(names_list)
    
    @property
    def all_actions(self):
        return self.serialize()
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
