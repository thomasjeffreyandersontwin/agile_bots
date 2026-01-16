
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.cli.base_hierarchical_adapter import BaseBehaviorsAdapter, BaseBehaviorAdapter
from agile_bots.src.behaviors.behavior import Behavior
from agile_bots.src.behaviors.behaviors import Behaviors

class TTYBehaviors(BaseBehaviorsAdapter, TTYAdapter):
    
    def __init__(self, behaviors: Behaviors):
        BaseBehaviorsAdapter.__init__(self, behaviors, 'tty')
        self.behaviors = behaviors
    
    @property
    def current(self):
        if self.behaviors.current:
            behavior_adapter = TTYBehavior(self.behaviors.current, is_current=True)
            return behavior_adapter.serialize()
        return ""
    
    @property
    def names(self):
        current_behavior_name = self.behaviors.current.name if self.behaviors.current else None
        names_list = []
        for behavior in self.behaviors:
            name = behavior.name
            if name == current_behavior_name:
                names_list.append(self.add_bold(name))
            else:
                names_list.append(name)
        return " | ".join(names_list)
    
    @property
    def all_behaviors(self):
        return self.serialize()
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)

class TTYBehavior(BaseBehaviorAdapter, TTYAdapter):
    
    def __init__(self, behavior: Behavior, is_current: bool = False):
        self.behavior = behavior
        self.is_current = is_current
        BaseBehaviorAdapter.__init__(self, behavior, 'tty', is_current)
    
    def format_behavior_name(self) -> str:
        if self.is_current:
            icon = "➤ "
            name = self.add_bold(self.behavior.name)
        else:
            icon = "☐ "
            name = self.behavior.name
        return f"- {icon}{name}"
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
