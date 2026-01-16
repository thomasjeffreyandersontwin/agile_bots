
from agile_bots.src.actions.tty_action import TTYAction
from agile_bots.src.actions.validate.validate_action import ValidateRulesAction
from agile_bots.src.instructions.instructions import Instructions

class TTYValidateAction(TTYAction):
    
    def __init__(self, action: ValidateRulesAction, is_current: bool = False, is_completed: bool = False):
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
    def rules(self):
        return self.action.rules
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
    
    @staticmethod
    def format_instructions_from_dict(instructions_dict: dict, bot_paths=None, scope=None) -> str:
        instructions_obj = Instructions(
            base_instructions=instructions_dict.get('base_instructions', []),
            bot_paths=bot_paths,
            scope=scope
        )
        for key, value in instructions_dict.items():
            if key != 'base_instructions':
                instructions_obj.set(key, value)
        
        from agile_bots.src.instructions.tty_instructions import TTYInstructions
        instructions_adapter = TTYInstructions(instructions_obj)
        return instructions_adapter.serialize()
