
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.scope.scope_command_result import ScopeCommandResult

class JSONScopeCommandResult(JSONAdapter):
    
    def __init__(self, scope_result: ScopeCommandResult):
        self.scope_result = scope_result
    
    def to_dict(self) -> dict:
        from agile_bots.src.scope.json_scope import JSONScope
        
        scope_adapter = JSONScope(self.scope_result.scope)
        scope_dict = scope_adapter.to_dict()
        
        return {
            'status': self.scope_result.status,
            'message': self.scope_result.message,
            'scope': scope_dict
        }
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
