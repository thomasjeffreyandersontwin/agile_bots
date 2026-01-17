
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from block import Block
    from scan import Scan
    from actions.rules.rule import Rule

class Violation:
    
    def __init__(
        self,
        rule: 'Rule',
        block: 'Block',
        scan: 'Scan',
        violation_message: str,
        line_number: int = None,
        severity: str = 'error'
    ):
        if not hasattr(rule, 'name') or not hasattr(rule, 'rule_file'):
            raise TypeError(f"rule must be a Rule object, got {type(rule)}")
        
        self._rule = rule
        self._block = block
        self._scan = scan
        self._violation_message = violation_message
        self._line_number = line_number
        self._severity = severity
        
        block.add_violation(self)
        scan.add_violation(self)
    
    @property
    def rule(self) -> 'Rule':
        return self._rule
    
    @property
    def block(self) -> 'Block':
        return self._block
    
    @property
    def scan(self) -> 'Scan':
        return self._scan
    
    @property
    def violation_message(self) -> str:
        return self._violation_message
    
    @property
    def line_number(self) -> int:
        return self._line_number or self._block.start_line
    
    @property
    def severity(self) -> str:
        return self._severity
    
    @classmethod
    def create_from_rule_and_context(
        cls,
        rule: 'Rule',
        block: 'Block',
        scan: 'Scan',
        message: str,
        line_number: int = None,
        severity: str = 'error'
    ) -> 'Violation':
        return cls(rule, block, scan, message, line_number, severity)
    
    def to_dict(self) -> dict:
        result = {
            'rule': self._rule.name,
            'rule_file': self._rule.rule_file,
            'violation_message': self._violation_message,
            'severity': self._severity,
            'line_number': self.line_number,
            'location': str(self._block.file.path)
        }
        return result

