
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.bot_path.bot_path import BotPath

class TTYBotPath(TTYAdapter):
    
    def __init__(self, bot_path: BotPath):
        self.bot_path = bot_path
    
    @property
    def workspace_directory(self):
        return self.bot_path.workspace_directory
    
    @property
    def bot_directory(self):
        return self.bot_path.bot_directory
    
    @property
    def base_actions_directory(self):
        return self.bot_path.base_actions_directory
    
    @property
    def python_workspace_root(self):
        return self.bot_path.python_workspace_root
    
    @property
    def documentation_path(self):
        return self.bot_path.documentation_path
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.add_bold("Bot Path:"))
        lines.append(str(self.bot_path.bot_directory))
        lines.append("")
        
        workspace_name = self.bot_path.workspace_directory.name
        lines.append(f"📂 {self.add_bold('Workspace:')} {workspace_name}")
        lines.append(str(self.bot_path.workspace_directory))
        lines.append("")
        lines.append("To change path:")
        lines.append("path demo/mob_minion              # Change to specific project")
        lines.append("path ../another_bot               # Change to relative path")
        lines.append(self.subsection_separator())
        
        return '\n'.join(lines)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
