
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast

from test_scanner import TestScanner
from scanners.violation import Violation

class ObjectOrientedHelpersScanner(TestScanner):

    PARAM_THRESHOLD = 3
    PARAMETRIZE_THRESHOLD = 3
    HELPER_CALL_THRESHOLD = 2

    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations

        content, lines, tree = parsed

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
                helper_used = self._uses_helper(node)
                param_count = self._count_params(node)
                parametrize_cols = self._parametrize_column_count(node)
                gwt_calls = self._given_when_then_calls(node)

                if (param_count >= self.PARAM_THRESHOLD or parametrize_cols >= self.PARAMETRIZE_THRESHOLD) and not helper_used:
                    message = (
                        f'Test "{node.name}" has many parameters ({max(param_count, parametrize_cols)}) '
                        f"but no helper/factory usage - consolidate with BotTestHelper or shared helper object."
                    )
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=message,
                            line_number=node.lineno,
                            location=str(file_path),
                            severity="warning",
                        ).to_dict()
                    )

                if gwt_calls >= self.HELPER_CALL_THRESHOLD and not helper_used:
                    message = (
                        f'Test "{node.name}" uses {gwt_calls} given/when/then helpers but no shared helper object; '
                        f"consolidate into BotTestHelper-style fixtures with standard data."
                    )
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=message,
                            line_number=node.lineno,
                            location=str(file_path),
                            severity="warning",
                        ).to_dict()
                    )

        return violations

    def _count_params(self, func_node: ast.FunctionDef) -> int:
        return sum(
            1
            for arg in func_node.args.args
            if arg.arg not in ("self", "cls")
        )

    def _parametrize_column_count(self, func_node: ast.FunctionDef) -> int:
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "parametrize":
                    if decorator.args:
                        first_arg = decorator.args[0]
                        if isinstance(first_arg, (ast.Constant, ast.Str)) and isinstance(first_arg.value, str):
                            columns = [c.strip() for c in first_arg.value.split(",") if c.strip()]
                            return len(columns)
        return 0

    def _given_when_then_calls(self, func_node: ast.FunctionDef) -> int:
        count = 0
        for inner in ast.walk(func_node):
            if isinstance(inner, ast.Call):
                func = inner.func
                name = ""
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name.startswith(("given_", "when_", "then_")):
                    count += 1
        return count

    def _uses_helper(self, func_node: ast.FunctionDef) -> bool:
        for inner in ast.walk(func_node):
            if isinstance(inner, ast.Call):
                if isinstance(inner.func, ast.Name) and "helper" in inner.func.id.lower():
                    return True
                if isinstance(inner.func, ast.Attribute) and "helper" in inner.func.attr.lower():
                    return True
            if isinstance(inner, ast.Assign):
                for target in inner.targets:
                    if isinstance(target, ast.Name) and "helper" in target.id.lower():
                        return True
        return False
