
from agile_bots.src.cli.adapters import MarkdownAdapter
from agile_bots.src.cli.base_hierarchical_adapter import BaseBehaviorsAdapter, BaseBehaviorAdapter
from agile_bots.src.behaviors.behavior import Behavior
from agile_bots.src.behaviors.behaviors import Behaviors

class MarkdownBehaviors(BaseBehaviorsAdapter, MarkdownAdapter):
    
    def __init__(self, behaviors: Behaviors):
        BaseBehaviorsAdapter.__init__(self, behaviors, 'markdown')
        self.behaviors = behaviors
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)

class MarkdownBehavior(BaseBehaviorAdapter, MarkdownAdapter):
    
    def __init__(self, behavior: Behavior, is_current: bool = False):
        self.behavior = behavior
        self.is_current = is_current
        BaseBehaviorAdapter.__init__(self, behavior, 'markdown', is_current)
    
    def format_behavior_name(self) -> str:
        marker = "→ " if self.is_current else "  "
        return self.format_list_item(f"{marker}{self.behavior.name}")
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
