
from agile_bots.src.cli.adapters import TTYAdapter

class TTYStrategy(TTYAdapter):
    
    def __init__(self, strategy):
        self.strategy = strategy
    
    def serialize(self) -> str:
        lines = []
        
        strategy_criterias = self.strategy.strategy_criterias.strategy_criterias
        if strategy_criterias:
            lines.append("")
            lines.append(self.add_bold("Decisions:"))
            for criteria_key, criteria in strategy_criterias.items():
                lines.append("")
                question = criteria.question
                if question:
                    lines.append(f"{self.add_bold(f'{criteria_key}:')} {question}")
                else:
                    lines.append(self.add_bold(f"{criteria_key}:"))
                
                options = criteria.options
                if options:
                    for option in options:
                        lines.extend(self._format_option(option))
        
        assumptions = self.strategy.assumptions.assumptions
        if assumptions:
            lines.append("")
            lines.append(self.add_bold("Assumptions:"))
            for assumption in assumptions:
                lines.append(f"- {assumption}")
        
        return '\n'.join(lines)
    
    def _format_option(self, option) -> list:
        lines = []
        if isinstance(option, dict):
            name = option.get('name', '')
            description = option.get('description', '')
            if name:
                lines.append(f"  - {self.add_bold(name)}")
                if description:
                    lines.append(f"    {description}")
            elif description:
                lines.append(f"  - {description}")
        elif isinstance(option, str):
            lines.append(f"  - {option}")
        return lines
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        parts = text.split(maxsplit=1)
        verb = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return verb, args
