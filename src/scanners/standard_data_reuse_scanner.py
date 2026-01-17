
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import ast

from test_scanner import TestScanner
from scanners.violation import Violation

class StandardDataReuseScanner(TestScanner):

    CANONICAL_KEYS: Set[str] = {
        "current",
        "completed_actions",
        "stories",
        "events",
        "action",
        "state",
        "log",
        "results",
        "output",
    }

    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations

        content, lines, tree = parsed

        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test")]:
            dict_keysets = []
            for node in ast.walk(func):
                dict_node = None
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
                    dict_node = node.value
                elif isinstance(node, ast.Call):
                    for arg in list(node.args) + [kw.value for kw in node.keywords]:
                        if isinstance(arg, ast.Dict):
                            dict_node = arg
                            break

                if dict_node and self._dict_has_canonical_keys(dict_node):
                    keyset = self._dict_keyset(dict_node)
                    dict_keysets.append((keyset, node.lineno))
                    if not self._is_uppercase_constant(getattr(node, "targets", [])):
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message="Inline dict with standard test data fields - reuse a shared standard data set (e.g., STANDARD_STATE) instead of recreating ad-hoc.",
                                line_number=node.lineno,
                                location=str(file_path),
                                severity="warning",
                            ).to_dict()
                        )

            unique_keysets = {}
            for keyset, lineno in dict_keysets:
                unique_keysets.setdefault(keyset, []).append(lineno)
            if len(unique_keysets) > 1:
                lines = sorted({ln for lst in unique_keysets.values() for ln in lst})
                first_line = lines[0] if lines else func.lineno
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message="Test defines multiple ad-hoc data shapes for standard data fields; consolidate to a shared standard data set.",
                        line_number=first_line,
                        location=str(file_path),
                        severity="warning",
                    ).to_dict()
                )

        return violations

    def _is_uppercase_constant(self, targets: List[ast.expr]) -> bool:
        for target in targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                return True
        return False

    def _dict_has_canonical_keys(self, dict_node: ast.Dict) -> bool:
        for key in dict_node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if key.value in self.CANONICAL_KEYS:
                    return True
        return False

    def _dict_keyset(self, dict_node: ast.Dict) -> str:
        keys = []
        for key in dict_node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.append(key.value)
        return ",".join(sorted(keys))
