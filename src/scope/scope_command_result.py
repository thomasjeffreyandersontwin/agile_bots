
from typing import Optional

class ScopeCommandResult:
    
    def __init__(self, status: str, message: str, scope: 'Scope'):
        self.status = status
        self.message = message
        self.scope = scope
