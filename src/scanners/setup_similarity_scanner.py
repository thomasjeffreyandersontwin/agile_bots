
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
import ast
from collections import defaultdict

from test_scanner import TestScanner
from scanners.violation import Violation

class SetupSimilarityScanner(TestScanner):

    MIN_KEYS = 2
    MIN_REUSE = 3
    MIN_INTRA_DUP = 2

    def scan(
        self,
        story_graph: Dict[str, Any],
        rule_obj: Any = None,
        test_files: Optional[List["Path"]] = None,
        code_files: Optional[List["Path"]] = None,
        on_file_scanned: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        fingerprint_occurrences: Dict[Tuple[str, Tuple[str, ...]], List[Tuple[Path, int, str]]] = defaultdict(list)
        intra_duplicates: List[Dict[str, Any]] = []

        files = test_files or []
        for file_path in files:
            parsed = self._read_and_parse_file(file_path)
            if not parsed:
                continue
            content, lines, tree = parsed

            for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test")]:
                payloads = self._collect_payloads(func)
                per_func_counts: Dict[Tuple[str, Tuple[str, ...]], List[int]] = defaultdict(list)
                for fp, lineno in payloads:
                    per_func_counts[fp].append(lineno)
                    fingerprint_occurrences[fp].append((file_path, lineno, func.name))
                for fp, ln_list in per_func_counts.items():
                    if len(ln_list) >= self.MIN_INTRA_DUP:
                        first_line = sorted(ln_list)[0]
                        intra_duplicates.append(
                            Violation(
                                rule=rule_obj,
                                violation_message=(
                                    f'Test "{func.name}" builds {len(ln_list)} similar setup payloads; '
                                    f"centralize into a shared standard fixture/helper."
                                ),
                                line_number=first_line,
                                location=str(file_path),
                                severity="warning",
                            ).to_dict()
                        )

        for fp, occs in fingerprint_occurrences.items():
            if len(occs) >= self.MIN_REUSE:
                keyset = fp[0]
                key_text = ", ".join(keyset.split(",")) if keyset else "keys"
                # Emit up to 5 locations for context
                for file_path, lineno, func_name in occs[:5]:
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=(
                                f'Setup payload with keys [{key_text}] reused across {len(occs)} tests; '
                                f"extract to shared standard data/helper instead of ad-hoc dicts."
                            ),
                            line_number=lineno,
                            location=str(file_path),
                            severity="warning",
                        ).to_dict()
                    )

        violations.extend(intra_duplicates)
        return violations

    def _collect_payloads(self, func_node: ast.FunctionDef) -> List[Tuple[Tuple[str, Tuple[str, ...]], int]]:
        payloads: List[Tuple[Tuple[str, Tuple[str, ...]], int]] = []
        for node in ast.walk(func_node):
            dict_node = None
            lineno = getattr(node, "lineno", None)

            if isinstance(node, ast.Dict):
                dict_node = node
            elif isinstance(node, ast.Call):
                for arg in list(node.args) + [kw.value for kw in node.keywords]:
                    if isinstance(arg, ast.Dict):
                        dict_node = arg
                        lineno = getattr(arg, "lineno", lineno)
                        break
                if not dict_node and isinstance(node.func, ast.Attribute) and node.func.attr in ("write_text", "write_bytes"):
                    if node.args:
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Call) and self._is_json_dumps(first_arg):
                            for arg in first_arg.args:
                                if isinstance(arg, ast.Dict):
                                    dict_node = arg
                                    lineno = getattr(arg, "lineno", lineno)
                                    break

            if dict_node:
                keyset, typemap = self._fingerprint_dict(dict_node)
                if keyset:
                    payloads.append(((keyset, typemap), lineno or func_node.lineno))

        return payloads

    def _is_json_dumps(self, call: ast.Call) -> bool:
        func = call.func
        if isinstance(func, ast.Attribute) and func.attr == "dumps":
            return True
        if isinstance(func, ast.Name) and func.id == "dumps":
            return True
        return False

    def _fingerprint_dict(self, dict_node: ast.Dict) -> Tuple[str, Tuple[str, ...]]:
        keys: List[str] = []
        types: List[str] = []
        for key, val in zip(dict_node.keys, dict_node.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.append(key.value)
                types.append(self._type_of(val))
        keys_sorted = sorted(keys)
        if len(keys_sorted) < self.MIN_KEYS:
            return "", ()
        return ",".join(keys_sorted), tuple(types)

    def _type_of(self, node: ast.AST) -> str:
        if isinstance(node, ast.Dict):
            return "dict"
        if isinstance(node, ast.List):
            return "list"
        if isinstance(node, ast.Tuple):
            return "tuple"
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        if isinstance(node, ast.Name):
            return "var"
        return type(node).__name__
