
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.exit_result.exit_result import ExitResult

class JSONExitResult(JSONAdapter):
    
    def __init__(self, exit_result: ExitResult):
        self.exit_result = exit_result
    
    @property
    def should_exit(self):
        return self.exit_result.should_exit
    
    @property
    def message(self):
        return self.exit_result.message
    
    def to_dict(self) -> dict:
        return {
            'should_exit': self.exit_result.should_exit,
            'message': self.exit_result.message
        }
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
