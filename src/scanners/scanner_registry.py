
from typing import Optional, Dict, Type
import importlib
import re
from scanners.scanner import Scanner

class ScannerRegistry:
    
    def __init__(self, bot_name: str = None):
        self._bot_name = bot_name
        self._scanner_cache: Dict[str, Type[Scanner]] = {}
    
    def finds_scanner_by_rule(self, rule) -> Optional[Type[Scanner]]:
        if not hasattr(rule, 'scanner_path') or not rule.scanner_path:
            return None
        
        if rule.scanner_path in self._scanner_cache:
            return self._scanner_cache[rule.scanner_path]
        
        scanner_class = self.loads_scanner_class(rule.scanner_path)
        if scanner_class:
            self._scanner_cache[rule.scanner_path] = scanner_class
        
        return scanner_class
    
    def loads_scanner_class(self, scanner_module_path: str) -> Optional[Type[Scanner]]:
        scanner_class, _ = self.loads_scanner_class_with_error(scanner_module_path)
        return scanner_class
    
    def loads_scanner_class_with_error(self, scanner_module_path: str) -> tuple[Optional[Type[Scanner]], Optional[str]]:
        if not scanner_module_path:
            return None, None
        
        try:
            module_path, class_name = scanner_module_path.rsplit('.', 1)
            
            scanner_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower().replace('_scanner', '').replace('scanner', '')
            
            paths_to_try = [
                module_path,
                f'scanners.{scanner_name}_scanner',
                f'agile_bots.src.scanners.{scanner_name}_scanner'
            ]
            
            if self._bot_name:
                paths_to_try.append(f'agile_bots.bots.{self._bot_name}.src.scanners.{scanner_name}_scanner')
            
            for path in paths_to_try:
                try:
                    module = importlib.import_module(path)
                    if hasattr(module, class_name):
                        scanner_class = getattr(module, class_name)
                        
                        if isinstance(scanner_class, type) and hasattr(scanner_class, 'scan'):
                            if issubclass(scanner_class, Scanner):
                                return scanner_class, None
                except (ImportError, AttributeError):
                    continue
            
            return None, f"Scanner class not found: {scanner_module_path}"
        except Exception as e:
            return None, f"Error loading scanner {scanner_module_path}: {e}"

