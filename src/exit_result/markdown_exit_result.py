
from agile_bots.src.cli.adapters import MarkdownAdapter
from agile_bots.src.exit_result.exit_result import ExitResult

class MarkdownExitResult(MarkdownAdapter):
    
    def __init__(self, exit_result: ExitResult):
        self.exit_result = exit_result
    
    def serialize(self) -> str:
        lines = []
        
        if self.exit_result.should_exit:
            lines.append(self.format_header(2, "Exit"))
            lines.append("")
        
        if self.exit_result.message:
            lines.append(self.exit_result.message)
            lines.append("")
        
        return ''.join(lines) if lines else ""
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
