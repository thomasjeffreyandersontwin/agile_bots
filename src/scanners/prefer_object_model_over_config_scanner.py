import re
from pathlib import Path
from typing import List, Dict, Any
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

class PreferObjectModelOverConfigScanner(CodeScanner):
    
    def __init__(self, self.rule=None):
        super().__init__()
        self.rule_name = "prefer_object_model_over_config"
        self.self.rule = self.rule
        
        self.config_access_patterns = [
            (r'(?<!self)\._config\[', 'Direct access to _config dictionary'),
            (r'(?<!self)\._config\.get\(', 'Using .get() on _config attribute'),
            (r"hasattr\([^,]+,\s*['\"]_config['\"]", 'Checking for _config attribute existence'),
        ]
        
        self.config_file_pattern = r'read_json_file\([^)]*(?:action_config|behavior_config|bot_config)\.json[^)]*\)'
        
        self.exception_patterns = [
            r'def __init__\(',
            r'class.*\(.*Config.*\)',
            r'def.*load.*config',
            r'def.*_load_.*_config',
            r'# scanner ignore',
        ]
    
    def scan_file(self, file_path: Path = None, story_graph: Dict[str, Any] = None) -> List[Violation]:
        violations = []
        
        # Use injected self.rule if provided, otherwise fall back to self.self.rule
        effective_rule = self.rule if self.rule is not None else self.self.rule
        if not effective_rule:
            return violations
        
        self.current_file_path = file_path
        
        if not file_path.exists():
            return violations
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return violations
        
        lines = content.split('\n')
        
        if self._is_exception_file(file_path):
            return violations
        
        for line_num, line in enumerate(lines, start=1):
            if '# scanner ignore' in line or '# noqa' in line:
                continue
            
            if self._is_in_exception_context(lines, line_num):
                continue
            
            for pattern, description in self.config_access_patterns:
                if re.search(pattern, line):
                    violations.append(self._create_violation(
                        line_num,
                        f"{description}. Use object properties instead of accessing _config directly.",
                        effective_rule
                    ))
            
            if re.search(self.config_file_pattern, line):
                if self._looks_like_object_exists_context(lines, line_num):
                    violations.append(self._create_violation(
                        line_num,
                        "Reading config file directly when object model may exist. Use object properties instead.",
                        effective_rule
                    ))
        
        return violations
    
    def _is_exception_file(self, file_path: Path) -> bool:
        file_str = str(file_path).lower()
        exception_paths = [
            'config',
            'loader',
            'factory',
            'migration',
            'setup',
            'generator',
            '__init__.py',
        ]
        return any(exc in file_str for exc in exception_paths)
    
    def _is_in_exception_context(self, lines: List[str], current_line: int) -> bool:
        current_indent = len(lines[current_line - 1]) - len(lines[current_line - 1].lstrip())
        
        for i in range(current_line - 2, max(0, current_line - 50), -1):
            line = lines[i]
            line_indent = len(line) - len(line.lstrip())
            
            if line_indent <= current_indent and ('def ' in line):
                for pattern in self.exception_patterns:
                    if re.search(pattern, line):
                        return True
                return False
        
        return False
    
    def _looks_like_object_exists_context(self, lines: List[str], current_line: int) -> bool:
        start = max(0, current_line - 5)
        end = min(len(lines), current_line + 5)
        context = '\n'.join(lines[start:end])
        
        object_patterns = [
            r'\.find_by_name\(',
            r'\.behaviors\.',
            r'\.actions\.',
            r'for \w+ in \w+\.behaviors',
            r'for \w+ in \w+\.actions',
            r'behavior\s*=',
            r'action\s*=',
        ]
        
        return any(re.search(pattern, context) for pattern in object_patterns)
    
    def _create_violation(self, line_num: int, message: str, effective_rule: Any = None) -> Violation:
        rule_to_use = effective_rule if effective_rule is not None else self.self.rule
        return Violation(
            rule=rule_to_use,
            violation_message=message,
            location=str(self.current_file_path),
            line_number=line_num,
            severity='error'
        )

