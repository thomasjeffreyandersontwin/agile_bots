
from agile_bots.src.actions.tty_action import TTYAction
from agile_bots.src.actions.render.render_action import RenderOutputAction

class TTYRenderAction(TTYAction):
    
    def __init__(self, action: RenderOutputAction, is_current: bool = False, is_completed: bool = False):
        super().__init__(action, is_current, is_completed)
    
    @property
    def description(self):
        return self.action.description
    
    @property
    def order(self):
        return self.action.order
    
    @property
    def next_action(self):
        return self.action.next_action
    
    @property
    def workflow(self):
        return self.action.workflow
    
    @property
    def auto_confirm(self):
        return self.action.auto_confirm
    
    @property
    def skip_confirm(self):
        return self.action.skip_confirm
    
    @property
    def behavior(self):
        return self.action.behavior
    
    @property
    def render_specs(self):
        return self.action.render_specs
    
    @property
    def templates(self):
        return self.action.templates
    
    @property
    def synchronizers(self):
        return self.action.synchronizers
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
