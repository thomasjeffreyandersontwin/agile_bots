
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.exit_result.exit_result import ExitResult

class TTYExitResult(TTYAdapter):
    
    def __init__(self, exit_result: ExitResult):
        self.exit_result = exit_result
    
    @property
    def should_exit(self):
        return self.exit_result.should_exit
    
    @property
    def message(self):
        return self.exit_result.message
    
    def serialize(self) -> str:
        if self.exit_result.message:
            return self.exit_result.message
        return "Exiting..." if self.exit_result.should_exit else ""
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
