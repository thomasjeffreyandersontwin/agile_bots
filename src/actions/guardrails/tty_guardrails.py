
from agile_bots.src.cli.adapters import TTYAdapter

class TTYGuardrails(TTYAdapter):
    
    def __init__(self, guardrails):
        self.guardrails = guardrails
    
    def serialize(self) -> str:
        from agile_bots.src.cli.adapter_factory import AdapterFactory
        
        lines = []
        
        if self.guardrails.required_context:
            required_context_adapter = AdapterFactory.create(self.guardrails.required_context, 'tty')
            lines.append(required_context_adapter.serialize())
        
        
        return '\n'.join(lines)
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        parts = text.split(maxsplit=1)
        verb = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return verb, args
