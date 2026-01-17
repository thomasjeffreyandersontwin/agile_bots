
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import ast

from test_scanner import TestScanner
from scanners.violation import Violation

class FullResultAssertionsScanner(TestScanner):

    TARGET_NAMES: Set[str] = {
        "state",
        "log",
        "activity_log",
        "result",
        "results",
        "response",
        "resp",
        "payload",
        "data",
        "output",
        "details",
        "info",
        "graph",
        "story_graph",
        "story_map",
        "instructions",
        "config",
        "cfg",
        "activity",
        "event",
    }

    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations

        content, lines, tree = parsed

        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test")]:
            alias_targets = self._collect_result_aliases(func)
            if self._has_full_object_assert(func, alias_targets):
                continue
            for node in ast.walk(func):
                if isinstance(node, ast.Assert):
                    if self._is_single_field_assert(node.test, alias_targets):
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message="Assertion checks a single field of a complex result - assert the full object (or dataclass equality) using standard data.",
                                line_number=node.lineno,
                                location=str(file_path),
                                severity="warning",
                            ).to_dict()
                        )

        return violations

    def _is_single_field_assert(self, test_expr: ast.AST, aliases: Set[str]) -> bool:
        targets = aliases or set()
        if isinstance(test_expr, ast.Compare):
            left = test_expr.left
            if self._is_subscript_or_attr_on_target(left, targets):
                return True
            for comp in test_expr.comparators:
                if self._is_subscript_or_attr_on_target(comp, targets):
                    return True
        if isinstance(test_expr, ast.Compare):
            sides = [test_expr.left] + list(test_expr.comparators)
            for side in sides:
                if isinstance(side, ast.Call) and isinstance(side.func, ast.Name) and side.func.id == "len":
                    if side.args and self._is_target_name(side.args[0], targets):
                        return True
        if isinstance(test_expr, ast.Compare):
            sides = [test_expr.left] + list(test_expr.comparators)
            for side in sides:
                if self._is_target_name(side, targets) or self._is_subscript_or_attr_on_target(side, targets):
                    return True
        if isinstance(test_expr, ast.BoolOp):
            return any(self._is_single_field_assert(value, targets) for value in test_expr.values)
        return False

    def _is_subscript_or_attr_on_target(self, node: ast.AST, aliases: Set[str]) -> bool:
        if isinstance(node, ast.Subscript):
            if self._is_target_name(node.value, aliases):
                return True
        if isinstance(node, ast.Attribute):
            base = node.value
            while isinstance(base, ast.Attribute):
                base = base.value
            if self._is_target_name(base, aliases):
                return True
        return False

    def _is_target_name(self, node: ast.AST, aliases: Set[str]) -> bool:
        return isinstance(node, ast.Name) and node.id in (self.TARGET_NAMES | aliases)

    def _has_full_object_assert(self, func_node: ast.FunctionDef, aliases: Set[str]) -> bool:
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert) and isinstance(node.test, ast.Compare):
                left = node.test.left
                comps = node.test.comparators
                if any(self._is_target_name(expr, aliases) for expr in [left, *comps]):
                    if not any(isinstance(expr, (ast.Subscript, ast.Attribute)) for expr in [left, *comps]):
                        return True
        return False

    def _collect_result_aliases(self, func_node: ast.FunctionDef) -> Set[str]:
        aliases: Set[str] = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                source = node.value
                source_name = None
                if isinstance(source, ast.Name) and source.id in (self.TARGET_NAMES | aliases):
                    source_name = source.id
                elif isinstance(source, ast.Call):
                    source_name = self._infer_call_name(source)
                    if source_name and source_name in self.TARGET_NAMES:
                        pass
                    else:
                        source_name = None
                if targets:
                    for t in targets:
                        if source_name or (isinstance(source, ast.Name) and source.id in (self.TARGET_NAMES | aliases)):
                            aliases.add(t)
        return aliases

    def _infer_call_name(self, call: ast.Call) -> Optional[str]:
        func = call.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None
