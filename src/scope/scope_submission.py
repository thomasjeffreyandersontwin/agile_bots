from dataclasses import dataclass
from typing import Optional

@dataclass
class ScopeSubmission:
    status: str
    behavior: Optional[str] = None
    action: Optional[str] = None
    message: str = ''
    node: Optional[str] = None
    node_type: Optional[str] = None
    
    @classmethod
    def error(cls, message: str) -> 'ScopeSubmission':
        return cls(status='error', message=message)
    
    @classmethod
    def success(cls, behavior: str, action: str, node: str, node_type: str, message: str = '') -> 'ScopeSubmission':
        return cls(
            status='success',
            behavior=behavior,
            action=action,
            message=message,
            node=node,
            node_type=node_type
        )
    
    def to_dict(self):
        return {
            'status': self.status,
            'behavior': self.behavior,
            'action': self.action,
            'message': self.message,
            'node': self.node,
            'node_type': self.node_type
        }
