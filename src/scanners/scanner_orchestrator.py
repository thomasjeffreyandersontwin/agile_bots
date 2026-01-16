
from typing import List, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from .scan import Scan
    from .scope import Scope
    from agile_bots.src.actions.rules.rule import Rule
    from .scanner import Scanner
    from .scanner_registry import ScannerRegistry

from .resources.scope import Scope
from .resources.scan import Scan
from .scanner_registry import ScannerRegistry

class ScannerOrchestrator:
    
    def __init__(self, scanner_registry: ScannerRegistry = None, bot_name: str = None):
        self._scanner_registry = scanner_registry or ScannerRegistry(bot_name=bot_name)
    
    @property
    def scanner_registry(self) -> ScannerRegistry:
        return self._scanner_registry
    
    def selects_scanner_helpers_by_rule(
        self,
        rule: 'Rule'
    ) -> 'Scanner':
        scanner_class = self.scanner_registry.finds_scanner_by_rule(rule)
        
        if not scanner_class:
            raise ValueError(f"No scanner found for rule: {rule.name}")
        
        return scanner_class()
    
    def performs_scan_on_scope(
        self,
        scan: 'Scan',
        scope: 'Scope',
        rule: 'Rule',
        scanner: 'Scanner' = None
    ) -> 'Scan':
        selected_scanner = scanner or self.selects_scanner_helpers_by_rule(rule)
        
        scan.undergoes_scan(selected_scanner)
        
        return scan
    
    def returns_scan(
        self,
        scope: 'Scope',
        rule: 'Rule'
    ) -> 'Scan':
        scan = Scan(scope, rule)
        self.performs_scan_on_scope(scan, scope, rule)
        return scan

