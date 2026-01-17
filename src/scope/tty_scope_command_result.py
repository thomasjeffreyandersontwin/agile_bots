
from cli.adapters import TTYAdapter
from scope.scope_command_result import ScopeCommandResult

class TTYScopeCommandResult(TTYAdapter):
    
    def __init__(self, scope_result: ScopeCommandResult):
        self.scope_result = scope_result
    
    def serialize(self) -> str:
        from scope.tty_scope import TTYScope
        
        lines = []
        
        status_color = 'green' if self.scope_result.status == 'success' else 'red'
        lines.append(self.add_color(f"Status: {self.scope_result.status}", status_color))
        
        if self.scope_result.message:
            lines.append(self.scope_result.message)
        
        lines.append("")
        
        scope_adapter = TTYScope(self.scope_result.scope)
        scope_output = scope_adapter.serialize()
        lines.append(scope_output)
        
        return '\n'.join(lines)
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from utils import parse_command_text
        return parse_command_text(text)
