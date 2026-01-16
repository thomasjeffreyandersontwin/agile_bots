
from agile_bots.src.cli.adapters import MarkdownAdapter
from agile_bots.src.navigation.navigation import NavigationResult

class MarkdownNavigation(MarkdownAdapter):
    
    def __init__(self, nav_result: NavigationResult):
        self.nav_result = nav_result
    
    def serialize(self) -> str:
        lines = []
        
        status = "✓ Success" if self.nav_result.success else "✗ Failed"
        lines.append(self.format_header(2, f"Navigation: {status}"))
        lines.append("")
        
        if self.nav_result.message:
            lines.append(self.nav_result.message)
            lines.append("")
        
        if self.nav_result.new_position:
            lines.append(f"**Position:** `{self.nav_result.new_position}`")
            lines.append("")
        
        return ''.join(lines)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
