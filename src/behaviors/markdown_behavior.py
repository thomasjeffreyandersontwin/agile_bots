
from cli.adapters import MarkdownAdapter
from cli.base_hierarchical_adapter import BaseBehaviorsAdapter, BaseBehaviorAdapter
from behaviors.behavior import Behavior
from behaviors.behaviors import Behaviors

class MarkdownBehaviors(BaseBehaviorsAdapter, MarkdownAdapter):
    
    def __init__(self, behaviors: Behaviors):
        BaseBehaviorsAdapter.__init__(self, behaviors, 'markdown')
        self.behaviors = behaviors

class MarkdownBehavior(BaseBehaviorAdapter, MarkdownAdapter):
    
    def __init__(self, behavior: Behavior, is_current: bool = False):
        self.behavior = behavior
        self.is_current = is_current
        BaseBehaviorAdapter.__init__(self, behavior, 'markdown', is_current)
    
    def format_behavior_name(self) -> str:
        marker = "→ " if self.is_current else "  "
        return self.format_list_item(f"{marker}{self.behavior.name}")
