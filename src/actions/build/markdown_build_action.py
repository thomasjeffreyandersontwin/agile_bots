
from agile_bots.src.actions.markdown_action import MarkdownAction
from agile_bots.src.actions.build.build_action import BuildStoryGraphAction

class MarkdownBuildAction(MarkdownAction):
    
    def __init__(self, action: BuildStoryGraphAction, is_current: bool = False, is_completed: bool = False):
        super().__init__(action, is_current, is_completed)
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
