
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from file import File
    from violation import Violation

class Block:
    
    def __init__(self, file: 'File', content: str, start_line: int, end_line: int):
        self._file = file
        self._content = content
        self._start_line = start_line
        self._end_line = end_line
        self._subblocks: List['Block'] = []
        self._violations: List['Violation'] = []
        self._similarity_calculator = None
        self._violation_reporter = None
        self._code_structure_analyzer = None
        self._complexity_metrics = None
        self._class_naming_checker = None
        self._method_naming_checker = None
    
    @property
    def file(self) -> 'File':
        return self._file
    
    @property
    def content(self) -> str:
        return self._content
    
    @property
    def subblocks(self) -> List['Block']:
        return self._subblocks
    
    @property
    def violations(self) -> List['Violation']:
        return self._violations
    
    @property
    def start_line(self) -> int:
        return self._start_line
    
    @property
    def end_line(self) -> int:
        return self._end_line
    
    def add_subblock(self, block: 'Block'):
        self._subblocks.append(block)
    
    def add_violation(self, violation: 'Violation'):
        self._violations.append(violation)
    
    def normalize_content(self) -> str:
        normalized = self._content.strip()
        normalized = normalized.replace('\r\n', '\n')
        normalized = normalized.replace('\r', '\n')
        lines = [line.rstrip() for line in normalized.split('\n')]
        return '\n'.join(lines)
    
    def has_similarity(self, other: 'Block', similarity_calculator) -> bool:
        if self._similarity_calculator is None:
            self._similarity_calculator = similarity_calculator
        return self._similarity_calculator.calculates_block_similarity(self, other)
    
    def analyze_structure(self, code_structure_analyzer) -> List['Violation']:
        if self._code_structure_analyzer is None:
            self._code_structure_analyzer = code_structure_analyzer
        return self._code_structure_analyzer.analyzes_code_structure(self)
    
    def calculate_complexity(self, complexity_metrics) -> dict:
        if self._complexity_metrics is None:
            self._complexity_metrics = complexity_metrics
        return {}
    
    def check_class_naming(self, class_naming_checker) -> List['Violation']:
        if self._class_naming_checker is None:
            self._class_naming_checker = class_naming_checker
        return self._class_naming_checker.checks_class_name_matches_story(self) + \
               self._class_naming_checker.validates_class_naming_conventions(self)
    
    def check_method_naming(self, method_naming_checker) -> List['Violation']:
        if self._method_naming_checker is None:
            self._method_naming_checker = method_naming_checker
        return self._method_naming_checker.checks_method_name_matches_scenario(self) + \
               self._method_naming_checker.validates_method_naming_conventions(self)

