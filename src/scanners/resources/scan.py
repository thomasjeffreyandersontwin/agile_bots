
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from scope import Scope
    from violation import Violation
    from actions.rules.rule import Rule

class Scan:
    
    def __init__(self, scope: 'Scope', rule: 'Rule'):
        self._scope = scope
        self._rule = rule
        self._violations: List['Violation'] = []
    
    @property
    def scope(self) -> 'Scope':
        return self._scope
    
    @property
    def rule(self) -> 'Rule':
        return self._rule
    
    @property
    def violations(self) -> List['Violation']:
        return self._violations
    
    def add_violation(self, violation: 'Violation'):
        self._violations.append(violation)
    
    def add_violations(self, violations: List['Violation']):
        self._violations.extend(violations)
    
    def undergoes_scan(self, scanner) -> List['Violation']:
        scanner.performs_scan_for_one_rule(self, self._scope, self._rule)
        return self._violations

