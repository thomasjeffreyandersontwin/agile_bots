
from agile_bots.src.cli.adapters import MarkdownAdapter
from agile_bots.src.bot_path.bot_path import BotPath

class MarkdownBotPath(MarkdownAdapter):
    
    def __init__(self, bot_path: BotPath):
        self.bot_path = bot_path
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.format_header(2, "Bot Paths"))
        lines.append("")
        lines.append(f"**Workspace:** `{self.bot_path.workspace_directory}`")
        lines.append("")
        lines.append(f"**Bot Directory:** `{self.bot_path.bot_directory}`")
        lines.append("")
        lines.append(f"**Base Actions:** `{self.bot_path.base_actions_directory}`")
        lines.append("")
        lines.append(f"**Documentation:** `{self.bot_path.documentation_path}`")
        lines.append("")
        lines.append(f"**Python Root:** `{self.bot_path.python_workspace_root}`")
        lines.append("")
        
        return ''.join(lines)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
