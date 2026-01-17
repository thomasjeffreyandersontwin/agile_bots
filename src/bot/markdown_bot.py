
from cli.adapters import MarkdownAdapter
from cli.base_hierarchical_adapter import BaseBotAdapter
from bot.bot import Bot
import logging
logger = logging.getLogger(__name__)

class MarkdownBot(BaseBotAdapter, MarkdownAdapter):
    
    def __init__(self, bot: Bot):
        BaseBotAdapter.__init__(self, bot, 'markdown')
        self.bot = bot
    
    
    @property
    def name(self):
        lines = []
        lines.append(MarkdownAdapter.format_header(self, 2, f"🤖 Bot: {self.bot.name}").strip())
        registered_bots = self.bot.bots
        if registered_bots and len(registered_bots) > 1:
            bot_list = ' | '.join(registered_bots)
            lines.append("")
            lines.append(f"**Registered:** {bot_list}")
            lines.append("**To change bots:** `bot <name>`")
        return '\n'.join(lines)
    
    @property
    def bot_paths(self):
        from cli.adapter_factory import AdapterFactory
        markdown_bot_paths = AdapterFactory.create(self.bot.bot_paths, 'markdown')
        return markdown_bot_paths.serialize()
    
    @property
    def progress(self):
        lines = []
        lines.append(MarkdownAdapter.format_header(self, 2, "🗺️¸Progress"))
        lines.append("")
        lines.append(f"**Current Position:** {self.bot.progress_path}")
        lines.append("")
        
        from cli.adapter_factory import AdapterFactory
        markdown_behaviors = AdapterFactory.create(self.bot.behaviors, 'markdown')
        lines.append(markdown_behaviors.serialize())
        
        return '\n'.join(lines)
    
    @property
    def commands(self):
        lines = []
        lines.append(MarkdownAdapter.format_header(self, 2, "💻 Commands"))
        lines.append("")
        lines.append("**status | back | current | next | path [dir] | scope [filter] | bot [name] | help | exit**")
        lines.append("")
        lines.append("```powershell")
        lines.append("echo '[command]' | python -m cli.cli_main")
        lines.append("```")
        lines.append("")
        lines.append("---")
        return '\n'.join(lines)
    
    @property
    def behavior_action_summary(self):
        lines = []
        
        behavior_names = []
        for behavior in self.bot.behaviors:
            name = behavior.name
            if name == (self.bot.behaviors.current.name if self.bot.behaviors.current else None):
                behavior_names.append(f"**{name}**")
            else:
                behavior_names.append(name)
        
        lines.append(f"**Behaviors:** {' | '.join(behavior_names)}")
        
        behavior = self.bot.behaviors.current or next(iter(self.bot.behaviors), None)
        if behavior:
            action_names = []
            all_actions = list(behavior.actions) + list(behavior.actions._non_workflow_actions)
            current_action_name = behavior.actions.current.action_name if behavior.actions.current else None
            for action in all_actions:
                name = action.action_name
                if name == current_action_name:
                    action_names.append(f"**{name}**")
                else:
                    action_names.append(name)
            lines.append(f"**Actions:** {' | '.join(action_names)}")
        
        return '\n'.join(lines)
    
    def format_header(self) -> str:
        lines = []
        lines.append("")
        lines.append("---")
        header_text = MarkdownAdapter.format_header(self, 2, "CLI STATUS section")
        lines.append(header_text)
        lines.append("")
        lines.append("This section contains current scope filter (if set), current progress in workflow, and available commands")
        lines.append("")
        lines.append("Review the CLI STATUS section below to understand both current state and available commands.")
        lines.append("")
        lines.append("**☢️  You MUST DISPLAY this entire section in your response to the user exactly as you see it. ☢️**")
        lines.append("")
        lines.append("---")
        return '\n'.join(lines)
    
    def format_bot_info(self) -> str:
        lines = []
        lines.append(self.name)
        lines.append("")
        lines.append(self.bot_paths)
        
        if hasattr(self.bot, '_scope') and self.bot._scope and hasattr(self.bot._scope, 'type'):
            from cli.adapter_factory import AdapterFactory
            try:
                markdown_scope = AdapterFactory.create(self.bot._scope, 'markdown')
                lines.append(markdown_scope.serialize())
                lines.append("")
            except (AttributeError, TypeError) as e:
                logger.warning(f'Failed to serialize scope to markdown: {str(e)}')
        
        if self.bot.behaviors:
            lines.append(self.progress)
            lines.append("")
        
        lines.append(self.commands)
        lines.append("")
        
        return '\n'.join(lines)
    
    def format_footer(self) -> str:
        return self.behavior_action_summary
    
    def serialize(self) -> str:
        result = super().serialize()
        return result + "\n" if result else result
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from utils import parse_command_text
        return parse_command_text(text)
