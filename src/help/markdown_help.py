
from agile_bots.src.cli.adapters import MarkdownAdapter
from agile_bots.src.help.help import Help

class MarkdownHelp(MarkdownAdapter):
    
    def __init__(self, help_obj: Help):
        self.help_obj = help_obj
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.format_header(2, "Core Commands"))
        core = self.help_obj.commands.core
        lines.append(f"  {core.navigation_pattern}  - {core.description_full}")
        lines.append(f"  {core.short_navigation_pattern}           - {core.description_short}")
        lines.append("")
        
        lines.append("  Available Components:")
        lines.append(f"    behaviors   -> {self.help_obj.components.behaviors}")
        lines.append("")
        lines.append("    actions:")
        for action_name, description in self.help_obj.components.actions:
            lines.append(f"      {action_name:<12} - {description}")
        lines.append("")
        lines.append("    operations:")
        for operation, params in self.help_obj.components.operations.operations:
            if params:
                lines.append(f"      {operation:<12} {params}")
            else:
                lines.append(f"      {operation}")
        lines.append("")
        
        lines.append("  Examples:")
        for cmd, desc in self.help_obj.commands.examples.examples:
            lines.append(f"    echo '{cmd}' | python repl_main.py{' ' * (30 - len(cmd))} -> {desc}")
        lines.append("")
        
        lines.append("  Other Commands:")
        for cmd, desc in self.help_obj.commands.other.commands:
            lines.append(f"    echo '{cmd}' | python repl_main.py{' ' * (30 - len(cmd))} - {desc}")
        lines.append("")
        
        lines.append("  Scope Command Details:")
        for rule in self.help_obj.scope.important_rules:
            lines.append(f"    {rule}")
        lines.append("")
        lines.append("    Usage (pick ONE - each replaces the previous scope):")
        for pattern, desc in self.help_obj.scope.usage_patterns:
            lines.append(f"      echo '{pattern}' | python repl_main.py{' ' * (55 - len(pattern))} - {desc}")
        lines.append("")
        lines.append("    Examples (CORRECT - each sets a SINGLE scope type):")
        for example, desc in self.help_obj.scope.correct_examples:
            display_example = example if len(example) < 75 else example[:72] + "..."
            padding = max(1, 80 - len(display_example))
            lines.append(f"      {display_example}{' ' * padding} - {desc}")
        lines.append("")
        lines.append("    Examples (INCORRECT - DO NOT USE):")
        for example, reason in self.help_obj.scope.incorrect_examples:
            lines.append(f"      {example:<20} [X] {reason}")
        
        return '\n'.join(lines)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
