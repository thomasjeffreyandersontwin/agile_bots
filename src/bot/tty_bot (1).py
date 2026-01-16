
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.cli.base_hierarchical_adapter import BaseBotAdapter
from agile_bots.src.bot.bot import Bot

class TTYBot(BaseBotAdapter, TTYAdapter):
    
    def __init__(self, bot: Bot):
        BaseBotAdapter.__init__(self, bot, 'tty')
        self.bot = bot
    
    @property
    def name(self):
        return f"{self.add_bold('🤖 Bot:')} {self.bot.name}"
    
    @property
    def bot_name(self):
        return self.bot.bot_name
    
    @property
    def bot_directory(self):
        return f"{self.add_bold('Bot Path:')}\n{str(self.bot.bot_paths.bot_directory)}"
    
    @property
    def workspace_directory(self):
        return f"{self.add_bold('Workspace Path:')}\n{str(self.bot.bot_paths.workspace_directory)}"
    
    @property
    def bot_paths(self):
        from agile_bots.src.cli.adapter_factory import AdapterFactory
        tty_bot_paths = AdapterFactory.create(self.bot.bot_paths, 'tty')
        return tty_bot_paths.serialize()
    
    @property
    def progress(self):
        lines = []
        lines.append(self.add_bold('🗺️ Progress'))
        lines.append(f"{self.add_bold('Current Position:')} {self.bot.progress_path}")
        lines.append("")
        
        from agile_bots.src.cli.adapter_factory import AdapterFactory
        tty_behaviors = AdapterFactory.create(self.bot.behaviors, 'tty')
        lines.append(tty_behaviors.serialize())
        
        return '\n'.join(lines)
    
    @property
    def behaviors(self):
        from agile_bots.src.cli.adapter_factory import AdapterFactory
        tty_behaviors = AdapterFactory.create(self.bot.behaviors, 'tty')
        return tty_behaviors.serialize()
    
    @property
    def header(self):
        lines = []
        lines.append("")
        lines.append(self.section_separator())
        text = "CLI STATUS section"
        separator_width = 100
        padding = (separator_width - len(text)) // 2
        centered_text = " " * padding + self.add_bold(text) + " " * padding
        lines.append(centered_text)
        lines.append("This section contains current scope filter (if set), current progress in workflow, and available commands")
        lines.append("Review the CLI STATUS section below to understand both current state and available commands.")
        lines.append("☢️  You MUST DISPLAY this entire section in your response to the user exactly as you see it. ☢️")
        lines.append(self.section_separator())
        return '\n'.join(lines)
    
    @property
    def run_instructions(self):
        lines = []
        lines.append("Run:")
        lines.append("echo 'behavior.action' | python repl_main.py           # Defaults to 'instructions' operation")
        lines.append("echo 'behavior.action.operation' | python repl_main.py  # Runs operation")
        lines.append("")
        lines.append(self.add_bold("Args:"))
        lines.append('--scope "Epic, Sub Epic, Story"      # Filter by story names')
        lines.append('--scope "file:path/one,path/two"     # Filter by file paths')
        lines.append('--headless                             # Execute autonomously without user input')
        lines.append(self.subsection_separator())
        return '\n'.join(lines)
    
    @property
    def commands(self):
        lines = []
        lines.append(self.add_bold('💻 Commands:'))
        lines.append(self.add_bold("status | back | current | next | path [dir] | scope [filter] | headless \"msg\" | help | exit"))
        lines.append("")
        lines.append("// Run")
        lines.append("echo '[command]' | python repl_main.py")
        lines.append("// to invoke commands")
        lines.append("")
        lines.append(self.section_separator())
        return '\n'.join(lines)
    
    @property
    def behavior_action_summary(self):
        from agile_bots.src.cli.adapter_factory import AdapterFactory
        tty_behaviors = AdapterFactory.create(self.bot.behaviors, 'tty')
        
        lines = []
        lines.append(f"{self.add_bold('Behaviors:')} {tty_behaviors.names}")
        
        behavior = self.bot.behaviors.current or next(iter(self.bot.behaviors), None)
        if behavior:
            tty_actions = AdapterFactory.create(behavior.actions, 'tty')
            lines.append(f"{self.add_bold('Actions:')} {tty_actions.names}")
        
        return '\n'.join(lines)
    
    def format_header(self) -> str:
        return self.header
    
    def format_bot_info(self) -> str:
        lines = []
        lines.append(self.name)
        lines.append(self.bot_paths)
        
        if hasattr(self.bot, '_scope'):
            from agile_bots.src.cli.adapter_factory import AdapterFactory
            tty_scope = AdapterFactory.create(self.bot._scope, 'tty')
            lines.append(tty_scope.serialize())
        
        if self.bot.behaviors:
            lines.append(self.progress)
            lines.append(self.run_instructions)
        
        lines.append(self.commands)
        
        return '\n'.join(lines)
    
    def format_footer(self) -> str:
        return self.behavior_action_summary
    
    def serialize(self) -> str:
        return super().serialize()
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
