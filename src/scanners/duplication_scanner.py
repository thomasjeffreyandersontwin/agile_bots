
from typing import List, Dict, Any, Optional, Tuple, Set, TYPE_CHECKING
from pathlib import Path
import ast
from datetime import datetime
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
import hashlib
from difflib import SequenceMatcher
import json

logger = logging.getLogger(__name__)

# Configuration constants
FILE_SCAN_TIMEOUT = 60  # seconds
MAX_FILE_SIZE = 500_000  # bytes (500KB)
PREVIEW_LENGTH = 200  # characters

def _safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_str = arg.encode('ascii', errors='replace').decode('ascii')
                safe_args.append(safe_str)
            else:
                safe_args.append(str(arg))
        print(*safe_args, **kwargs)

class DuplicationScanner(CodeScanner):
    
    SCANNER_VERSION = "1.0"
    
    def _get_cache_dir(self, file_path: Optional[Path] = None) -> Path:
        if file_path:
            current = file_path.parent
            while current and current.parent != current:
                if (current / '.git').exists() or (current / 'pyproject.toml').exists() or (current / 'setup.py').exists():
                    cache_dir = current / '.cache' / 'duplication_blocks'
                    break
                current = current.parent
            else:
                import tempfile
                cache_dir = Path(tempfile.gettempdir()) / 'agile_bot_cache' / 'duplication_blocks'
        else:
            import tempfile
            cache_dir = Path(tempfile.gettempdir()) / 'agile_bot_cache' / 'duplication_blocks'
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def _get_file_cache_key(self, file_path: Path) -> Optional[str]:
        try:
            mtime = file_path.stat().st_mtime
            file_size = file_path.stat().st_size
            key_data = f"{file_path}:{mtime}:{file_size}:{self.SCANNER_VERSION}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception:
            return None
    
    def _load_blocks_from_cache(self, file_path: Path) -> Optional[List[Dict]]:
        cache_key = self._get_file_cache_key(file_path)
        if not cache_key:
            return None
        
        cache_file = self._get_cache_dir(file_path) / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                return cached_data.get('blocks', [])
        except Exception as e:
            logger.debug(f"Cache read failed for {file_path}: {e}")
            return None
    
    def _save_blocks_to_cache(self, file_path: Path, blocks: List[Dict]):
        cache_key = self._get_file_cache_key(file_path)
        if not cache_key:
            return
        
        cache_file = self._get_cache_dir(file_path) / f"{cache_key}.json"
        
        try:
            serializable_blocks = []
            for block in blocks:
                serializable_block = {k: v for k, v in block.items() if k not in ('ast_nodes', 'file_path', 'lines')}
                serializable_blocks.append(serializable_block)
            
            cache_data = {
                'file_path': str(file_path),
                'cached_at': datetime.now().isoformat(),
                'blocks': serializable_blocks
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.debug(f"Cache write failed for {file_path}: {e}")
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        _safe_print(f"[DuplicationScanner.scan_code_file] Called for: {file_path}")
        
        if not file_path.exists():
            _safe_print(f"[DuplicationScanner.scan_code_file] File does not exist: {file_path}")
            return violations
        
        file_start_time = datetime.now()
        
        try:
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                _safe_print(f"Skipping large file ({file_size/1024:.1f}KB): {file_path}")
                return violations
        except Exception as e:
            _safe_print(f"Could not check file size for {file_path}: {e}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            lines = content.split('\n')
            
            functions = []
            
            def extract_functions_from_node(node: ast.AST, parent_class: str = None):
                if isinstance(node, ast.ClassDef):
                    for child in node.body:
                        extract_functions_from_node(child, node.name)
                elif isinstance(node, ast.FunctionDef):
                    func_body = ast.unparse(node.body) if hasattr(ast, 'unparse') else str(node.body)
                    functions.append((node.name, func_body, node.lineno, node, parent_class))
            
            for node in tree.body:
                extract_functions_from_node(node, None)
            
            func_violations = self._check_duplicate_functions(functions, file_path, lines)
            violations.extend(func_violations)
            
            elapsed = (datetime.now() - file_start_time).total_seconds()
            if elapsed > FILE_SCAN_TIMEOUT:
                _safe_print(f"TIMEOUT: File scan exceeded {FILE_SCAN_TIMEOUT}s: {file_path} (stopping early)")
                return violations
            
            block_violations = self._check_duplicate_code_blocks(functions, lines, file_path)
            violations.extend(block_violations)
            
            file_elapsed = (datetime.now() - file_start_time).total_seconds()
            if file_elapsed > FILE_SCAN_TIMEOUT:
                _safe_print(f"VERY SLOW scan: {file_path} took {file_elapsed:.1f}s (exceeded {FILE_SCAN_TIMEOUT}s threshold)")
            elif file_elapsed > 10:
                _safe_print(f"Slow scan: {file_path} took {file_elapsed:.1f}s")
            
            if violations:
                _safe_print(f"[DUPLICATION SCANNER] Found {len(violations)} violations in {file_path}")
                _safe_print(f"[DUPLICATION SCANNER] Violations: {[v.get('violation_message', '')[:100] for v in violations]}")
                self._log_violation_details(file_path, violations, lines)
            else:
                _safe_print(f"[DUPLICATION SCANNER] No violations found in {file_path}")
            
            return violations
        
        except (SyntaxError, UnicodeDecodeError) as e:
            _safe_print(f"Skipping file with syntax/encoding error: {file_path}: {e}")
            return violations
        except Exception as e:
            file_elapsed = (datetime.now() - file_start_time).total_seconds()
            import traceback
            _safe_print(f"Unexpected error scanning {file_path} after {file_elapsed:.1f}s: {e}")
            traceback.print_exc()
            raise
    
    def _check_duplicate_functions(self, functions: List[tuple], file_path: Path, lines: List[str] = None) -> List[Dict[str, Any]]:
        violations = []
        
        body_hashes = {}
        for func_tuple in functions:
            func_name, func_body, line_num, node, class_name = func_tuple
            body_hash = hashlib.md5(func_body.encode()).hexdigest()
            if body_hash not in body_hashes:
                body_hashes[body_hash] = []
            body_hashes[body_hash].append((func_name, line_num, node, class_name))
        
        for body_hash, func_list in body_hashes.items():
            if len(func_list) > 1:
                func_names = [f[0] for f in func_list]
                func_nodes = [f[2] for f in func_list]
                class_names = [f[3] for f in func_list]
                line_numbers = [f[1] for f in func_list]
                
                if self._are_interface_methods(func_names, class_names, func_nodes):
                    continue
                
                if all(self._is_simple_property(node) for node in func_nodes):
                    continue
                
                if all(self._is_simple_delegation(node) for node in func_nodes):
                    continue
                
                if all(self._is_trivial_stub(node) for node in func_nodes):
                    continue
                
                violation = Violation(
                    rule=self.rule,
                    violation_message=f'Duplicate code detected: functions {", ".join(func_names)} have identical bodies - extract to shared function',
                    location=str(file_path),
                    line_number=line_numbers[0],
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _are_interface_methods(self, func_names: List[str], class_names: List[Any], func_nodes: List[ast.FunctionDef]) -> bool:
        if all(name.startswith('__') and name.endswith('__') for name in func_names):
            unique_classes = set(c for c in class_names if c is not None)
            if len(unique_classes) > 1:
                return True
            if len(func_names) == 1 and func_names[0] == '__str__':
                return True
        
        if all(self._is_simple_property_getter(node) for node in func_nodes):
            unique_classes = set(c for c in class_names if c is not None)
            if len(unique_classes) > 1:
                return True
        
        if len(set(func_names)) == 1:
            unique_classes = set(c for c in class_names if c is not None)
            if len(unique_classes) > 1:
                if all(self._is_simple_delegation(node) for node in func_nodes):
                    return True
        
        return False
    
    def _is_simple_delegation(self, func_node: ast.FunctionDef) -> bool:
        if self._is_simple_property_getter(func_node):
            return True
        
        executable_body = [stmt for stmt in func_node.body if not self._is_docstring_or_comment(stmt, func_node)]
        if len(executable_body) != 1:
            return False
        
        stmt = executable_body[0]
        if not isinstance(stmt, ast.Return) or not stmt.value:
            return False
        
        return self._is_delegation_return_value(stmt.value)
    
    def _is_trivial_stub(self, func_node: ast.FunctionDef) -> bool:
        """Check if function is a trivial stub that just returns a simple constant."""
        executable_body = [stmt for stmt in func_node.body if not self._is_docstring_or_comment(stmt, func_node)]
        if len(executable_body) != 1:
            return False
        
        stmt = executable_body[0]
        if not isinstance(stmt, ast.Return):
            return False
        
        # Check if returns a simple constant (string, number, None, empty list/dict/set/tuple)
        if isinstance(stmt.value, ast.Constant):
            # Empty strings, empty collections, None, 0, False are trivial
            value = stmt.value.value
            if value in ("", None, 0, False):
                return True
        
        # Empty collection literals
        if isinstance(stmt.value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
            if hasattr(stmt.value, 'elts') and len(stmt.value.elts) == 0:
                return True
            if hasattr(stmt.value, 'keys') and len(stmt.value.keys) == 0:
                return True
        
        return False
    
    def _is_delegation_return_value(self, value: ast.expr) -> bool:
        if isinstance(value, ast.Call):
            return self._is_self_method_call(value)
        if isinstance(value, ast.Subscript):
            return self._is_self_attribute_subscript(value)
        if isinstance(value, ast.Attribute):
            return self._is_self_name(value.value)
        return False
    
    def _is_self_method_call(self, call: ast.Call) -> bool:
        if not isinstance(call.func, ast.Attribute):
            return False
        func_value = call.func.value
        if self._is_self_name(func_value):
            return True
        if isinstance(func_value, ast.Attribute) and self._is_self_name(func_value.value):
            return True
        if isinstance(func_value, ast.Name):
            return True
        return False
    
    def _is_self_attribute_subscript(self, subscript: ast.Subscript) -> bool:
        if not isinstance(subscript.value, ast.Attribute):
            return False
        return self._is_self_name(subscript.value.value)
    
    def _is_self_name(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Name) and node.id == 'self'
    
    def _is_simple_property_getter(self, func_node: ast.FunctionDef) -> bool:
        if not self._has_property_decorator(func_node):
            return self._is_simple_self_return(func_node)
        
        executable_body = [stmt for stmt in func_node.body if not self._is_docstring_or_comment(stmt, func_node)]
        if len(executable_body) != 1:
            return False
        
        stmt = executable_body[0]
        if not isinstance(stmt, ast.Return):
            return False
        
        if isinstance(stmt.value, ast.Attribute) and self._is_self_name(stmt.value.value):
            return True
        if isinstance(stmt.value, ast.Name):
            return True
        return False
    
    def _has_property_decorator(self, func_node: ast.FunctionDef) -> bool:
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'property':
                return True
            if self._is_property_attribute_decorator(decorator):
                return True
        return False
    
    def _is_property_attribute_decorator(self, decorator: ast.AST) -> bool:
        """Check if decorator is a property attribute decorator."""
        if not isinstance(decorator, ast.Attribute):
            return False
        if decorator.attr in ('setter', 'deleter'):
            return False
        if not hasattr(decorator, 'value'):
            return False
        if not isinstance(decorator.value, ast.Name):
            return False
        return decorator.value.id == 'property'
    
    def _is_simple_self_return(self, func_node: ast.FunctionDef) -> bool:
        if len(func_node.body) > 2:
            return False
        for stmt in func_node.body:
            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Attribute):
                if self._is_self_name(stmt.value.value):
                    return True
        return False
    
    def _check_duplicate_code_blocks(self, functions: List[tuple], lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        all_blocks = []
        for func_tuple in functions:
            func_name, func_body, func_line, func_node, _ = func_tuple
            blocks = self._extract_code_blocks(func_node, func_line, func_name)
            all_blocks.extend(blocks)
        
        SIMILARITY_THRESHOLD = 0.90
        
        comparison_count = 0
        similarity_scores = []
        
        duplicate_pairs = []
        reported_block_indices = set()
        
        _safe_print(f"[DuplicationScanner] Extracted {len(all_blocks)} blocks from {len(functions)} functions")
        
        compared_pairs = set()
        for i, block1 in enumerate(all_blocks):
            for j, block2 in enumerate(all_blocks[i+1:], start=i+1):
                if i == j:
                    continue
                
                pair_key = tuple(sorted([i, j]))
                if pair_key in compared_pairs:
                    continue
                compared_pairs.add(pair_key)
                
                if (block1['func_name'] == block2['func_name'] and 
                    not (block1['end_line'] < block2['start_line'] or block2['end_line'] < block1['start_line'])):
                    continue
                
                ast_similarity, normalized_similarity, content_similarity = self._calculate_block_similarities(block1, block2)
                
                max_similarity = self._determine_max_similarity(ast_similarity, content_similarity, normalized_similarity, SIMILARITY_THRESHOLD)
                
                if max_similarity == 0.0:
                    similarity_scores.append((ast_similarity, content_similarity, max(ast_similarity, content_similarity)))
                    continue
                
                similarity_scores.append((ast_similarity, content_similarity, max_similarity))
                
                if max_similarity >= SIMILARITY_THRESHOLD:
                    if self._should_skip_duplicate_pair(block1, block2):
                        continue
                    
                    if self._should_report_duplicate(block1, block2):
                        duplicate_pairs.append((i, j, max_similarity))
                        _safe_print(f"[DuplicationScanner] Found duplicate pair: block {i} (line {block1['start_line']}) vs block {j} (line {block2['start_line']}), similarity={max_similarity:.2f}")
        
        _safe_print(f"[DuplicationScanner] Compared {comparison_count} block pairs")
        _safe_print(f"[DuplicationScanner] Found {len(duplicate_pairs)} duplicate pairs (threshold: {SIMILARITY_THRESHOLD})")
        if similarity_scores:
            top_scores = sorted(similarity_scores, key=lambda x: x[2], reverse=True)[:10]
            _safe_print(f"[DuplicationScanner] Top similarity scores: {[(f'{a:.2f}', f'{c:.2f}', f'{m:.2f}') for a, c, m in top_scores]}")
        
        group_repr = list(range(len(all_blocks)))
        
        def find(x):
            if group_repr[x] != x:
                group_repr[x] = find(group_repr[x])
            return group_repr[x]
        
        def union(x, y):
            root_x = find(x)
            root_y = find(y)
            if root_x != root_y:
                group_repr[root_y] = root_x
        
        for i, j, _ in duplicate_pairs:
            union(i, j)
        
        groups = {}
        for idx in range(len(all_blocks)):
            root = find(idx)
            if root not in groups:
                groups[root] = []
            groups[root].append(idx)
        
        merged_groups = {}
        group_keys = list(groups.keys())
        
        for i, root_idx in enumerate(group_keys):
            if root_idx in merged_groups:
                continue
            
            group_blocks = [all_blocks[idx] for idx in groups[root_idx]]
            func_pairs = set()
            for block in group_blocks:
                func_pairs.add(block['func_name'])
            
            merged_with = root_idx
            for j, other_root_idx in enumerate(group_keys[i+1:], start=i+1):
                if other_root_idx in merged_groups:
                    continue
                
                other_blocks = [all_blocks[idx] for idx in groups[other_root_idx]]
                other_func_pairs = set()
                for block in other_blocks:
                    other_func_pairs.add(block['func_name'])
                
                if func_pairs == other_func_pairs:
                    overlaps = False
                    for block1 in group_blocks:
                        for block2 in other_blocks:
                            if (block1['func_name'] == block2['func_name'] and
                                not (block1['end_line'] < block2['start_line'] or 
                                     block2['end_line'] < block1['start_line'])):
                                overlaps = True
                                break
                        if overlaps:
                            break
                    
                    if overlaps:
                        groups[merged_with].extend(groups[other_root_idx])
                        merged_groups[other_root_idx] = merged_with
            
            merged_groups[root_idx] = merged_with
        
        final_groups = {}
        for root_idx, block_indices in groups.items():
            merged_root = merged_groups.get(root_idx, root_idx)
            if merged_root not in final_groups:
                final_groups[merged_root] = []
            final_groups[merged_root].extend(block_indices)
        
        for root_idx in final_groups:
            final_groups[root_idx] = list(set(final_groups[root_idx]))
        
        _safe_print(f"[DuplicationScanner] Built {len(final_groups)} duplicate groups")
        
        for root_idx, block_indices in final_groups.items():
            if len(block_indices) < 2:
                _safe_print(f"[DuplicationScanner] Skipping group {root_idx}: only {len(block_indices)} block(s)")
                continue
            
            if all(idx in reported_block_indices for idx in block_indices):
                continue
            
            group_blocks = [all_blocks[idx] for idx in sorted(block_indices)]
            
            filtered_blocks = []
            blocks_by_func = {}
            
            for block in group_blocks:
                func_name = block['func_name']
                if func_name not in blocks_by_func:
                    blocks_by_func[func_name] = []
                blocks_by_func[func_name].append(block)
            
            for func_name, func_blocks in blocks_by_func.items():
                func_blocks.sort(key=lambda b: (b['end_line'] - b['start_line'], -b['start_line']), reverse=True)
                
                non_overlapping = []
                for block in func_blocks:
                    overlaps = False
                    for selected in non_overlapping:
                        if not (block['end_line'] < selected['start_line'] or selected['end_line'] < block['start_line']):
                            overlaps = True
                            break
                    if not overlaps:
                        non_overlapping.append(block)
                
                filtered_blocks.extend(non_overlapping)
            
            if len(filtered_blocks) < 2:
                _safe_print(f"[DuplicationScanner] Skipping group {root_idx}: filtering reduced to {len(filtered_blocks)} block(s)")
                continue
            
            _safe_print(f"[DuplicationScanner] Reporting duplicate group: {len(filtered_blocks)} blocks")
            
            primary_block = filtered_blocks[0]
            
            previews = []
            for block in filtered_blocks:
                location = f"{block['func_name']}:{block['start_line']}-{block['end_line']}"
                preview = block['preview'][:PREVIEW_LENGTH] + '...' if len(block['preview']) > PREVIEW_LENGTH else block['preview']
                previews.append(f"Location ({location}):\n```python\n{preview}\n```")
            
            violation_message = (
                f'Duplicate code blocks detected ({len(filtered_blocks)} locations) - extract to helper function.\n\n' +
                '\n\n'.join(previews)
            )
            
            violation = Violation(
                rule=self.rule,
                violation_message=violation_message,
                location=str(file_path),
                line_number=primary_block['start_line'],
                severity='error'
            ).to_dict()
            violations.append(violation)
            
            reported_block_indices.update(block_indices)
        
        _safe_print(f"[DuplicationScanner._check_duplicate_code_blocks] Returning {len(violations)} violations")
        return violations
    
    def _calculate_block_similarities(self, block1: Dict, block2: Dict) -> Tuple[float, float, float]:
        """Calculate AST, normalized, and content similarities between two blocks."""
        try:
            ast_similarity = self._compare_ast_blocks(block1['ast_nodes'], block2['ast_nodes'])
        except Exception as e:
            _safe_print(f"Error comparing AST blocks: {e}")
            ast_similarity = 0.0
        
        try:
            normalized_similarity = SequenceMatcher(None, block1['normalized'], block2['normalized']).ratio()
        except Exception as e:
            _safe_print(f"Error comparing normalized blocks: {e}")
            normalized_similarity = 0.0
        
        try:
            preview1_normalized = ' '.join(block1['preview'].split())
            preview2_normalized = ' '.join(block2['preview'].split())
            content_similarity = SequenceMatcher(None, preview1_normalized, preview2_normalized).ratio()
        except Exception as e:
            _safe_print(f"Error comparing content blocks: {e}")
            content_similarity = 0.0
        
        return ast_similarity, normalized_similarity, content_similarity
    
    def _determine_max_similarity(self, ast_sim: float, content_sim: float, normalized_sim: float, threshold: float) -> float:
        """Determine the maximum similarity score based on multiple metrics."""
        if ast_sim >= 0.85 and content_sim >= 0.50:
            return max(ast_sim, content_sim)
        if ast_sim >= 0.80 and content_sim >= 0.70:
            return max(ast_sim, content_sim)
        if max(ast_sim, content_sim) >= 0.90 and min(ast_sim, content_sim) >= 0.60:
            return max(ast_sim, content_sim)
        if ast_sim >= threshold:
            return ast_sim
        return 0.0
    
    def _should_skip_duplicate_pair(self, block1: Dict, block2: Dict) -> bool:
        """Check if a duplicate pair should be skipped based on various filters."""
        if self._is_interface_method(block1['func_name']) or self._is_interface_method(block2['func_name']):
            return True
        
        if self._is_mostly_helper_calls(block1['ast_nodes']) or self._is_mostly_helper_calls(block2['ast_nodes']):
            return True
        
        if self._is_helper_function(block1['func_name']) and self._is_helper_function(block2['func_name']):
            return True
        
        if self._operates_on_different_domains(block1, block2):
            return True
        
        if self._calls_different_methods(block1['ast_nodes'], block2['ast_nodes']):
            return True
        
        if self._is_sequential_appends_with_different_content(block1['ast_nodes'], block2['ast_nodes']):
            return True
        
        return False
    
    def _should_report_duplicate(self, block1: Dict, block2: Dict) -> bool:
        """Determine if a duplicate should be reported."""
        if block1['func_name'] != block2['func_name']:
            return True
        if abs(block1['start_line'] - block2['start_line']) > 10:
            return True
        return False
    
    def _extract_code_blocks(self, func_node: ast.FunctionDef, func_start_line: int, func_name: str) -> List[Dict[str, Any]]:
        blocks = []
        MIN_NODES = 5
        MAX_NODES = 80
        MIN_LINES = 5
        MAX_LINES = 20
        
        if func_name.startswith('test_'):
            return blocks
        
        if self._is_interface_method(func_name):
            return blocks
        
        if self._is_simple_property(func_node):
            return blocks
        
        if self._is_simple_constructor(func_node):
            return blocks
        
        subtrees = self._extract_subtrees_from_function(func_node, MIN_NODES, MAX_NODES)
        
        for subtree in subtrees:
            start_line = subtree.lineno if hasattr(subtree, 'lineno') else func_start_line
            end_line = subtree.end_lineno if hasattr(subtree, 'end_lineno') and subtree.end_lineno else start_line
            
            total_lines = end_line - start_line + 1
            if total_lines < MIN_LINES or total_lines > MAX_LINES:
                continue
            
            if not hasattr(subtree, 'body') or not isinstance(subtree.body, list):
                continue
            
            block_statements = [stmt for stmt in subtree.body if not self._is_docstring_or_comment(stmt, func_node)]
            
            if not block_statements:
                continue
            
            if all(self._is_docstring_or_comment(s, func_node) for s in block_statements):
                continue
            
            if self._is_only_helper_calls(block_statements):
                continue
            
            if self._is_mostly_helper_calls(block_statements):
                continue
            
            if self._is_mostly_assertions(block_statements):
                continue
            
            if self._is_test_pattern(block_statements):
                continue
            
            if self._is_list_building_pattern(block_statements):
                continue
            
            if self._is_sequential_output_building(block_statements):
                continue
            
            if self._is_logging_or_output_pattern(block_statements):
                continue
            
            if self._is_string_formatting_pattern(block_statements):
                continue
            
            actual_code_count = self._count_actual_code_statements(block_statements)
            if actual_code_count < 3:
                continue
            
            normalized = self._normalize_block(block_statements)
            if not normalized:
                continue
            
            preview = self._get_block_preview(block_statements)
            
            blocks.append({
                'hash': hashlib.md5(normalized.encode()).hexdigest(),
                'start_line': start_line,
                'end_line': end_line,
                'func_name': func_name,
                'preview': preview,
                'normalized': normalized,
                'ast_nodes': block_statements
            })
        
        executable_body = [stmt for stmt in func_node.body if not self._is_docstring_or_comment(stmt, func_node)]
        
        for block_size in range(5, min(11, len(executable_body) + 1)):
            for i in range(len(executable_body) - block_size + 1):
                block_statements = executable_body[i:i+block_size]
                
                if self._is_contained_in_subtree(block_statements, subtrees):
                    continue
                
                if all(self._is_docstring_or_comment(s, func_node) for s in block_statements):
                    continue
                if self._is_only_helper_calls(block_statements):
                    continue
                if self._is_mostly_helper_calls(block_statements):
                    continue
                if self._is_mostly_assertions(block_statements):
                    continue
                if self._is_test_pattern(block_statements):
                    continue
                
                if self._is_sequential_output_building(block_statements):
                    continue
                
                if self._is_logging_or_output_pattern(block_statements):
                    continue
                
                if self._is_string_formatting_pattern(block_statements):
                    continue
                
                actual_code_count = self._count_actual_code_statements(block_statements)
                if actual_code_count < 3:
                    continue
                
                start_line = block_statements[0].lineno if hasattr(block_statements[0], 'lineno') else func_start_line
                end_line = block_statements[-1].end_lineno if hasattr(block_statements[-1], 'end_lineno') else (
                    block_statements[-1].lineno if hasattr(block_statements[-1], 'lineno') else start_line
                )
                
                total_lines = end_line - start_line + 1
                if total_lines < MIN_LINES or total_lines > MAX_LINES:
                    continue
                
                normalized = self._normalize_block(block_statements)
                if not normalized:
                    continue
                
                preview = self._get_block_preview(block_statements)
                
                blocks.append({
                    'hash': hashlib.md5(normalized.encode()).hexdigest(),
                    'start_line': start_line,
                    'end_line': end_line,
                    'func_name': func_name,
                    'preview': preview,
                    'normalized': normalized,
                    'ast_nodes': block_statements
                })
        
        return blocks
    
    def _extract_subtrees_from_function(self, func_node: ast.FunctionDef, min_nodes: int, max_nodes: int) -> List[ast.AST]:
        subtrees = []
        control_structures = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncFor, ast.AsyncWith)
        
        def extract_from_node(node):
            if isinstance(node, control_structures):
                num_nodes = len(list(ast.walk(node)))
                if min_nodes <= num_nodes <= max_nodes:
                    subtrees.append(node)
            
            self._extract_from_node_children(node, extract_from_node)
        
        for stmt in func_node.body:
            extract_from_node(stmt)
        
        return subtrees
    
    def _extract_from_node_children(self, node: ast.AST, extract_fn):
        """Recursively extract from child nodes."""
        if hasattr(node, 'body') and isinstance(node.body, list):
            for child in node.body:
                extract_fn(child)
        
        if hasattr(node, 'orelse') and isinstance(node.orelse, list):
            for child in node.orelse:
                extract_fn(child)
        
        if hasattr(node, 'handlers') and isinstance(node.handlers, list):
            for handler in node.handlers:
                if hasattr(handler, 'body') and isinstance(handler.body, list):
                    for child in handler.body:
                        extract_fn(child)
        
        if hasattr(node, 'finalbody') and isinstance(node.finalbody, list):
            for child in node.finalbody:
                extract_fn(child)
    
    def _is_contained_in_subtree(self, block_statements: List[ast.stmt], subtrees: List[ast.AST]) -> bool:
        if not block_statements or not subtrees:
            return False
        
        block_start = block_statements[0].lineno if hasattr(block_statements[0], 'lineno') else 0
        block_end = block_statements[-1].end_lineno if hasattr(block_statements[-1], 'end_lineno') else block_start
        
        for subtree in subtrees:
            subtree_start = subtree.lineno if hasattr(subtree, 'lineno') else 0
            subtree_end = subtree.end_lineno if hasattr(subtree, 'end_lineno') else subtree_start
            
            if subtree_start <= block_start and block_end <= subtree_end:
                return True
        
        return False
    
    def _get_statement_end_line(self, stmt: ast.stmt) -> int:
        if hasattr(stmt, 'end_lineno') and stmt.end_lineno:
            return stmt.end_lineno
        
        if isinstance(stmt, ast.If):
            return self._get_if_end_line(stmt)
        if isinstance(stmt, (ast.For, ast.While, ast.AsyncFor)):
            return self._get_loop_end_line(stmt)
        if isinstance(stmt, ast.Try):
            return self._get_try_end_line(stmt)
        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            return self._get_with_end_line(stmt)
        
        return stmt.lineno if hasattr(stmt, 'lineno') else 0
    
    def _get_if_end_line(self, stmt: ast.If) -> int:
        """Get end line for If statement."""
        end_line = stmt.lineno
        if stmt.body:
            end_line = max(end_line, self._get_body_end_line(stmt.body))
        if stmt.orelse:
            end_line = max(end_line, self._get_body_end_line(stmt.orelse))
        return end_line
    
    def _get_loop_end_line(self, stmt) -> int:
        """Get end line for loop statement."""
        end_line = stmt.lineno
        if stmt.body:
            end_line = max(end_line, self._get_body_end_line(stmt.body))
        if stmt.orelse:
            end_line = max(end_line, self._get_body_end_line(stmt.orelse))
        return end_line
    
    def _get_try_end_line(self, stmt: ast.Try) -> int:
        """Get end line for Try statement."""
        end_line = stmt.lineno
        if stmt.body:
            end_line = max(end_line, self._get_body_end_line(stmt.body))
        if stmt.orelse:
            end_line = max(end_line, self._get_body_end_line(stmt.orelse))
        if stmt.finalbody:
            end_line = max(end_line, self._get_body_end_line(stmt.finalbody))
        for handler in stmt.handlers:
            if handler.body:
                end_line = max(end_line, self._get_body_end_line(handler.body))
        return end_line
    
    def _get_with_end_line(self, stmt) -> int:
        """Get end line for With statement."""
        end_line = stmt.lineno
        if stmt.body:
            end_line = max(end_line, self._get_body_end_line(stmt.body))
        return end_line
    
    def _get_body_end_line(self, body: List[ast.stmt]) -> int:
        if not body:
            return 0
        end_line = 0
        for stmt in body:
            stmt_end = self._get_statement_end_line(stmt)
            end_line = max(end_line, stmt_end)
        return end_line
    
    def _is_docstring_or_comment(self, stmt: ast.stmt, func_node: ast.FunctionDef = None) -> bool:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if isinstance(stmt.value.value, str):
                if func_node and func_node.body and func_node.body[0] is stmt:
                    return True
                value_str = stmt.value.value.strip()
                if any(pattern in value_str for pattern in ['Args:', 'Returns:', 'Raises:', 'Yields:', 'Note:', 'Example:']):
                    return True
                if '\n' in value_str:
                    return True
        if isinstance(stmt, ast.Pass):
            return True
        return False
    
    def _is_mostly_helper_calls(self, statements: List[ast.stmt]) -> bool:
        if not statements:
            return False
        
        helper_count, total_count = self._count_helper_statements(statements)
        
        if total_count == 0:
            return True
        
        return (helper_count / total_count) >= 0.6
    
    def _count_helper_statements(self, statements: List[ast.stmt]) -> Tuple[int, int]:
        """Count helper calls vs total statements."""
        helper_count = 0
        total_count = 0
        helper_patterns = [
            'given_', 'when_', 'then_',
            'create_', 'build_', 'make_', 'generate_',
            'verify_', 'assert_', 'check_', 'ensure_',
            'setup_', 'bootstrap_', 'initialize_',
            'get_', 'load_', 'fetch_'
        ]
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            total_count += 1
            
            if self._is_helper_statement(stmt, helper_patterns):
                helper_count += 1
        
        return helper_count, total_count
    
    def _is_helper_statement(self, stmt: ast.stmt, helper_patterns: List[str]) -> bool:
        """Check if statement is a helper call."""
        if isinstance(stmt, ast.Assert):
            return True
        
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            func_name = self._get_function_name(stmt.value.func)
            if func_name and any(func_name.startswith(pattern) for pattern in helper_patterns):
                return True
        
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func_name = self._get_function_name(stmt.value.func)
            if func_name and any(func_name.startswith(pattern) for pattern in helper_patterns):
                return True
        
        return False
    
    def _is_only_helper_calls(self, statements: List[ast.stmt]) -> bool:
        helper_patterns = [
            'given_', 'when_', 'then_',
            'create_', 'build_', 'make_', 'generate_',
            'verify_', 'assert_', 'check_', 'ensure_',
            'setup_', 'bootstrap_', 'initialize_',
            'get_', 'load_', 'fetch_'
        ]
        
        for stmt in statements:
            if not self._is_valid_helper_only_statement(stmt, helper_patterns):
                return False
        
        return True
    
    def _is_valid_helper_only_statement(self, stmt: ast.stmt, helper_patterns: List[str]) -> bool:
        """Check if statement is valid for helper-only context."""
        if isinstance(stmt, ast.Assert):
            return True
        
        if isinstance(stmt, ast.Assign):
            if not isinstance(stmt.value, ast.Call):
                return False
            func_name = self._get_function_name(stmt.value.func)
            return func_name and self._check_helper_pattern_match(func_name, helper_patterns)
        
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func_name = self._get_function_name(stmt.value.func)
            return func_name and self._check_helper_pattern_match(func_name, helper_patterns)
        
        return False
    
    def _check_helper_pattern_match(self, func_name: str, helper_patterns: List[str]) -> bool:
        return any(func_name.startswith(pattern) for pattern in helper_patterns)
    
    def _get_function_name(self, func_node: ast.expr) -> Optional[str]:
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None
    
    def _is_helper_function(self, func_name: str) -> bool:
        helper_patterns = [
            'given_', 'when_', 'then_',
            'create_', 'build_', 'make_', 'generate_',
            'verify_', 'assert_', 'check_', 'ensure_',
            'setup_', 'bootstrap_', 'initialize_',
            'get_', 'load_', 'fetch_'
        ]
        return any(func_name.startswith(pattern) for pattern in helper_patterns)
    
    def _is_interface_method(self, func_name: str) -> bool:
        if func_name.startswith('__') and func_name.endswith('__'):
            return True
        
        interface_methods = {
            'items', 'keys', 'values',
            'children', 'steps',
            'default_test_method',
            'get', 'set', 'has',
        }
        if func_name in interface_methods:
            return True
        
        if func_name in ['items', 'keys', 'values', 'children', 'steps']:
            return True
        
        return False
    
    def _count_actual_code_statements(self, statements: List[ast.stmt]) -> int:
        count = 0
        for stmt in statements:
            if self._is_docstring_or_comment(stmt) or isinstance(stmt, ast.Pass):
                continue
            
            count += self._count_statement_and_children(stmt)
        
        return count
    
    def _count_statement_and_children(self, stmt: ast.stmt) -> int:
        """Count a statement and recursively count its children."""
        if isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Expr, ast.Return, 
                            ast.Raise, ast.Assert, ast.Delete, ast.Import, ast.ImportFrom,
                            ast.Global, ast.Nonlocal)):
            return 1
        
        if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            return self._count_control_flow_statement(stmt)
        
        if isinstance(stmt, (ast.AsyncFor, ast.AsyncWith)):
            return self._count_async_statement(stmt)
        
        return 0
    
    def _count_control_flow_statement(self, stmt) -> int:
        """Count code in control flow statement."""
        count = 0
        if hasattr(stmt, 'body'):
            count += self._count_actual_code_statements(stmt.body)
        if hasattr(stmt, 'orelse') and stmt.orelse:
            count += self._count_actual_code_statements(stmt.orelse)
        if hasattr(stmt, 'handlers'):
            for handler in stmt.handlers:
                count += self._count_actual_code_statements(handler.body)
        if hasattr(stmt, 'finalbody') and stmt.finalbody:
            count += self._count_actual_code_statements(stmt.finalbody)
        return count
    
    def _count_async_statement(self, stmt) -> int:
        """Count code in async statement."""
        if hasattr(stmt, 'body'):
            return self._count_actual_code_statements(stmt.body)
        return 0
    
    def _is_string_formatting_pattern(self, statements: List[ast.stmt]) -> bool:
        if not statements:
            return False
        
        string_ops, total_count = self._count_string_operations(statements)
        
        if total_count == 0:
            return False
        
        return (string_ops / total_count) >= 0.6
    
    def _count_string_operations(self, statements: List[ast.stmt]) -> Tuple[int, int]:
        """Count string operations vs total statements."""
        string_ops = 0
        total_count = 0
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            total_count += 1
            
            if self._is_string_operation_statement(stmt):
                string_ops += 1
        
        return string_ops, total_count
    
    def _is_string_operation_statement(self, stmt: ast.stmt) -> bool:
        if isinstance(stmt, ast.Assign):
            if isinstance(stmt.value, ast.JoinedStr):
                return True
            if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Attribute):
                if stmt.value.func.attr in ('format', 'join'):
                    return True
            if isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, (ast.Add, ast.Mod)):
                return True
        
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            if isinstance(stmt.value.func, ast.Attribute):
                if stmt.value.func.attr in ('format', 'join', 'replace', 'strip', 'split'):
                    return True
        
        return False
    
    def _is_mostly_assertions(self, statements: List[ast.stmt]) -> bool:
        if not statements:
            return False
        
        assertion_count = 0
        total_count = 0
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            total_count += 1
            if isinstance(stmt, ast.Assert):
                assertion_count += 1
        
        if total_count == 0:
            return False
        
        return (assertion_count / total_count) >= 0.6
    
    def _is_test_pattern(self, statements: List[ast.stmt]) -> bool:
        if not statements:
            return False
        
        helper_count, assertion_count, other_count = self._classify_test_statements(statements)
        
        total = helper_count + assertion_count + other_count
        if total == 0:
            return False
        
        test_pattern_ratio = (helper_count + assertion_count) / total
        return test_pattern_ratio >= 0.75 and other_count <= 1
    
    def _classify_test_statements(self, statements: List[ast.stmt]) -> Tuple[int, int, int]:
        helper_count = 0
        assertion_count = 0
        other_count = 0
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            if isinstance(stmt, ast.Assert):
                assertion_count += 1
            elif self._is_call_statement(stmt):
                if self._is_helper_call_statement(stmt):
                    helper_count += 1
                else:
                    other_count += 1
            else:
                other_count += 1
        
        return helper_count, assertion_count, other_count
    
    def _is_call_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement is a call (assign or expr)."""
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            return True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            return True
        return False
    
    def _is_helper_call_statement(self, stmt: ast.stmt) -> bool:
        """Check if call statement is a helper function."""
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            func_name = self._get_function_name(stmt.value.func)
            return func_name and self._is_helper_function(func_name)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func_name = self._get_function_name(stmt.value.func)
            return func_name and self._is_helper_function(func_name)
        return False
    
    def _is_sequential_output_building(self, statements: List[ast.stmt]) -> bool:
        if not statements or len(statements) < 3:
            return False
        
        append_count, total_count, has_loop_with_appends = self._analyze_output_building(statements)
        
        if total_count == 0:
            return False
        
        # Pattern 1: 70%+ direct appends
        if (append_count / total_count) >= 0.7:
            return True
        
        # Pattern 2: Has a loop with appends + some surrounding appends (help text pattern)
        return has_loop_with_appends and append_count >= 2
    
    def _analyze_output_building(self, statements: List[ast.stmt]) -> Tuple[int, int, bool]:
        """Analyze statements for output building patterns."""
        append_count = 0
        total_count = 0
        has_loop_with_appends = False
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            total_count += 1
            
            if self._is_append_statement(stmt):
                append_count += 1
            
            if isinstance(stmt, ast.For) and self._loop_contains_appends(stmt):
                has_loop_with_appends = True
                append_count += 1
        
        return append_count, total_count, has_loop_with_appends
    
    def _is_append_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement is an append/extend call."""
        if not isinstance(stmt, ast.Expr):
            return False
        if not isinstance(stmt.value, ast.Call):
            return False
        if not isinstance(stmt.value.func, ast.Attribute):
            return False
        return stmt.value.func.attr in ('append', 'extend')
    
    def _loop_contains_appends(self, stmt: ast.For) -> bool:
        """Check if loop contains append operations."""
        for node in ast.walk(stmt):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    if node.value.func.attr in ('append', 'extend'):
                        return True
        return False
    
    def _is_logging_or_output_pattern(self, statements: List[ast.stmt]) -> bool:
        if not statements:
            return False
        
        output_count, total_count = self._count_output_statements(statements)
        
        if total_count == 0:
            return False
        
        # If 60%+ is logging/output, exclude it
        return (output_count / total_count) >= 0.6
    
    def _count_output_statements(self, statements: List[ast.stmt]) -> Tuple[float, int]:
        """Count output/logging statements vs total."""
        output_count = 0.0
        total_count = 0
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            total_count += 1
            output_count += self._get_output_score(stmt)
        
        return output_count, total_count
    
    def _get_output_score(self, stmt: ast.stmt) -> float:
        """Get output score for statement (0, 0.5, or 1)."""
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            if self._is_logging_call(stmt.value):
                return 1.0
        
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.BinOp):
            if isinstance(stmt.value.op, ast.Add):
                return 0.5  # Half credit for string building
        
        return 0.0
    
    def _is_logging_call(self, call: ast.Call) -> bool:
        """Check if call is a logging/output operation."""
        if isinstance(call.func, ast.Attribute):
            method_name = call.func.attr
            obj_name = call.func.value.id if isinstance(call.func.value, ast.Name) else None
            
            if obj_name in ('logger', 'log', 'logging'):
                return True
            if method_name in ('debug', 'info', 'warning', 'error', 'critical', 'log', 'exception'):
                return True
            if method_name in ('write', 'writeline', 'writelines', 'flush'):
                return True
        
        if isinstance(call.func, ast.Name):
            if call.func.id in ('print', '_safe_print', 'safe_print'):
                return True
        
        return False
    
    def _is_list_building_pattern(self, statements: List[ast.stmt]) -> bool:
        if not statements:
            return False
        
        list_building_count, sequential_appends, has_append, total_count = self._analyze_list_building(statements)
        
        if total_count == 0:
            return False
        
        # If this is ALL or mostly sequential appends (common output building pattern), it's not duplication
        if sequential_appends >= 3 and (sequential_appends / total_count) >= 0.7:
            return True
        
        # If this is mostly list building with append calls inside conditionals, it's likely a formatting pattern
        if has_append and (list_building_count / total_count) >= 0.5:
            return True
        
        return (list_building_count / total_count) >= 0.7
    
    def _analyze_list_building(self, statements: List[ast.stmt]) -> Tuple[int, int, bool, int]:
        """Analyze statements for list building patterns."""
        list_building_count = 0
        sequential_appends = 0
        has_append = False
        total_count = 0
        
        for stmt in statements:
            if self._is_docstring_or_comment(stmt):
                continue
            
            total_count += 1
            
            if self._is_list_building_statement(stmt):
                list_building_count += 1
                if self._is_append_or_extend_call(stmt):
                    has_append = True
                    sequential_appends += 1
            
            if isinstance(stmt, ast.If) and self._if_contains_appends(stmt):
                list_building_count += 1
                has_append = True
        
        return list_building_count, sequential_appends, has_append, total_count
    
    def _is_list_building_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement is list building."""
        if self._is_append_or_extend_call(stmt):
            return True
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, (ast.List, ast.ListComp)):
            return True
        return False
    
    def _is_append_or_extend_call(self, stmt: ast.stmt) -> bool:
        """Check if statement is append/extend call."""
        if not isinstance(stmt, ast.Expr):
            return False
        if not isinstance(stmt.value, ast.Call):
            return False
        if not isinstance(stmt.value.func, ast.Attribute):
            return False
        return stmt.value.func.attr in ('extend', 'append')
    
    def _if_contains_appends(self, stmt: ast.If) -> bool:
        """Check if If statement contains appends."""
        for substmt in ast.walk(stmt):
            if isinstance(substmt, ast.Expr) and isinstance(substmt.value, ast.Call):
                if isinstance(substmt.value.func, ast.Attribute):
                    if substmt.value.func.attr in ('extend', 'append'):
                        return True
        return False
    
    def _is_simple_property(self, func_node: ast.FunctionDef) -> bool:
        if not func_node.decorator_list:
            return False
        
        if not self._has_any_property_decorator(func_node):
            return False
        
        executable_body = [stmt for stmt in func_node.body if not self._is_docstring_or_comment(stmt, func_node)]
        return len(executable_body) <= 2
    
    def _has_any_property_decorator(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has any property-related decorator."""
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'property':
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr in ('setter', 'deleter'):
                return True
        return False
    
    def _is_simple_constructor(self, func_node: ast.FunctionDef) -> bool:
        if func_node.name != '__init__':
            return False
        
        executable_body = [stmt for stmt in func_node.body if not self._is_docstring_or_comment(stmt, func_node)]
        
        self_assignments, other_statements = self._count_constructor_statements(executable_body)
        
        total = self_assignments + other_statements
        return total > 0 and (self_assignments / total) >= 0.8
    
    def _count_constructor_statements(self, executable_body: List[ast.stmt]) -> Tuple[int, int]:
        """Count self assignments vs other statements in constructor."""
        self_assignments = 0
        other_statements = 0
        
        for stmt in executable_body:
            if self._is_self_assignment_statement(stmt):
                self_assignments += 1
            else:
                other_statements += 1
        
        return self_assignments, other_statements
    
    def _is_self_assignment_statement(self, stmt: ast.stmt) -> bool:
        if not isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            return False
        
        targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
        
        for target in targets:
            if not self._is_self_attribute_target(target):
                return False
        
        return True
    
    def _is_self_attribute_target(self, target: ast.expr) -> bool:
        if not isinstance(target, ast.Attribute):
            return False
        if not isinstance(target.value, ast.Name):
            return False
        return target.value.id == 'self'
    
    def _extract_domain_entities(self, block: Dict[str, Any]) -> Set[str]:
        func_name = block['func_name'].lower()
        entities = set()
        
        common_entities = ['user', 'product', 'order', 'item', 'account', 'payment', 
                          'customer', 'invoice', 'report', 'task', 'project', 'story',
                          'feature', 'epic', 'sprint', 'team', 'workflow', 'action',
                          'rule', 'validation', 'scanner', 'violation', 'document',
                          'file', 'path', 'config', 'context', 'state', 'node']
        
        for entity in common_entities:
            if entity in func_name:
                entities.add(entity)
        
        return entities
    
    def _operates_on_different_domains(self, block1: Dict[str, Any], block2: Dict[str, Any]) -> bool:
        domain_patterns1 = self._extract_domain_entities(block1)
        domain_patterns2 = self._extract_domain_entities(block2)
        
        if self._has_different_domain_crud_operations(domain_patterns1, domain_patterns2, block1, block2):
            return True
        
        if self._has_different_iteration_targets(block1, block2):
            return True
        
        if self._has_different_list_targets(block1, block2):
            return True
        
        return False
    
    def _has_different_domain_crud_operations(self, domain1: Set[str], domain2: Set[str], 
                                             block1: Dict, block2: Dict) -> bool:
        """Check if blocks have different domain CRUD operations."""
        if not (domain1 and domain2 and domain1 != domain2):
            return False
        
        func1, func2 = block1['func_name'], block2['func_name']
        if abs(len(func1) - len(func2)) > 3:
            return False
        
        crud_ops = ['create', 'read', 'get', 'update', 'delete', 'remove', 
                   'save', 'load', 'fetch', 'set', 'find', 'search']
        func1_lower, func2_lower = func1.lower(), func2.lower()
        
        for op in crud_ops:
            if func1_lower.startswith(op) and func2_lower.startswith(op):
                return True
        return False
    
    def _has_different_iteration_targets(self, block1: Dict, block2: Dict) -> bool:
        """Check if blocks iterate over different collections."""
        collections1 = self._extract_iteration_targets(block1.get('ast_nodes', []))
        collections2 = self._extract_iteration_targets(block2.get('ast_nodes', []))
        
        if collections1 and collections2:
            return not collections1.intersection(collections2)
        return False
    
    def _has_different_list_targets(self, block1: Dict, block2: Dict) -> bool:
        """Check if blocks build different lists."""
        list_targets1 = self._extract_list_building_targets(block1.get('ast_nodes', []))
        list_targets2 = self._extract_list_building_targets(block2.get('ast_nodes', []))
        
        if list_targets1 and list_targets2:
            return not list_targets1.intersection(list_targets2)
        return False
    
    def _calls_different_methods(self, block1_nodes: List[ast.stmt], block2_nodes: List[ast.stmt]) -> bool:
        calls1 = self._extract_method_calls(block1_nodes)
        calls2 = self._extract_method_calls(block2_nodes)
        
        if not calls1 or not calls2:
            return False
        
        if len(calls1) == len(calls2) and len(calls1) >= 2:
            method_names1 = {call for call in calls1}
            method_names2 = {call for call in calls2}
            
            if method_names1 != method_names2:
                same_calls = len(method_names1 & method_names2)
                total_unique = len(method_names1 | method_names2)
                if total_unique > 0:
                    similarity_ratio = same_calls / total_unique
                    if similarity_ratio < 0.5:
                        return True
        
        return False
    
    def _extract_method_calls(self, nodes: List[ast.stmt]) -> List[str]:
        method_calls = []
        
        for node in nodes:
            call_name = self._get_call_name_from_node(node)
            if call_name:
                method_calls.append(call_name)
        
        return method_calls
    
    def _get_call_name_from_node(self, node: ast.stmt) -> Optional[str]:
        """Extract call name from statement node."""
        call = None
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value
        
        if not call:
            return None
        
        if isinstance(call.func, ast.Attribute):
            return call.func.attr
        if isinstance(call.func, ast.Name):
            return call.func.id
        return None
    
    def _extract_iteration_targets(self, nodes: List[ast.stmt]) -> Set[str]:
        targets = set()
        
        for node in nodes:
            for child in ast.walk(node):
                if isinstance(child, ast.For):
                    # Extract what we're iterating over
                    if isinstance(child.iter, ast.Attribute):
                        # e.g., self.bot.behaviors -> 'behaviors'
                        targets.add(child.iter.attr)
                    elif isinstance(child.iter, ast.Name):
                        # e.g., items -> 'items'
                        targets.add(child.iter.id)
        
        return targets
    
    def _extract_list_building_targets(self, nodes: List[ast.stmt]) -> Set[str]:
        targets = set()
        
        for node in nodes:
            # Look for assignments creating empty lists
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.List) and len(node.value.elts) == 0:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            targets.add(target.id)
            
            # Look for append calls
            for child in ast.walk(node):
                if isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                    if isinstance(child.value.func, ast.Attribute):
                        if child.value.func.attr == 'append':
                            # Get the list being appended to
                            if isinstance(child.value.func.value, ast.Name):
                                targets.add(child.value.func.value.id)
        
        return targets
    
    def _is_sequential_appends_with_different_content(self, block1_nodes: List[ast.stmt], block2_nodes: List[ast.stmt]) -> bool:
        
        # Extract append content from block 1
        appends1 = []
        for node in block1_nodes:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'append':
                    if node.value.args:
                        arg = node.value.args[0]
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            appends1.append(arg.value)
        
        # Extract append content from block 2
        appends2 = []
        for node in block2_nodes:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'append':
                    if node.value.args:
                        arg = node.value.args[0]
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            appends2.append(arg.value)
        
        # If both blocks are mostly appends (80%+) with string literals
        block1_append_ratio = len(appends1) / len(block1_nodes) if block1_nodes else 0
        block2_append_ratio = len(appends2) / len(block2_nodes) if block2_nodes else 0
        
        if block1_append_ratio >= 0.8 and block2_append_ratio >= 0.8:
            # Check if the content is actually different
            if appends1 and appends2:
                # Calculate how many string literals are different
                common_strings = set(appends1) & set(appends2)
                total_unique_strings = len(set(appends1) | set(appends2))
                
                if total_unique_strings > 0:
                    similarity = len(common_strings) / total_unique_strings
                    # If less than 30% of the strings are common, they're different content
                    if similarity < 0.3:
                        return True
        
        return False
    
    def _normalize_block(self, statements: List[ast.stmt]) -> Optional[str]:
        try:
            normalized_parts = []
            for stmt in statements:
                normalized = self._normalize_statement(stmt)
                if normalized:
                    normalized_parts.append(normalized)
            return "|".join(normalized_parts) if normalized_parts else None
        except Exception as e:
            _safe_print(f"Error normalizing block: {e}")
            return None
    
    def _normalize_statement(self, stmt: ast.stmt) -> Optional[str]:
        if self._is_docstring_stmt(stmt):
            return None
        if isinstance(stmt, ast.Assign):
            return f"ASSIGN({len(stmt.targets)}_targets)"
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            return "CALL"
        if isinstance(stmt, ast.Assert):
            return "ASSERT"
        if isinstance(stmt, ast.For):
            return "FOR_LOOP"
        if isinstance(stmt, ast.With):
            return "WITH"
        return type(stmt).__name__
    
    def _is_docstring_stmt(self, stmt: ast.stmt) -> bool:
        if not isinstance(stmt, ast.Expr):
            return False
        if not isinstance(stmt.value, ast.Constant):
            return False
        if not isinstance(stmt.value.value, str):
            return False
        return stmt.value.value.strip().startswith('"""')
    
    def _get_block_preview(self, statements: List[ast.stmt]) -> str:
        try:
            if hasattr(ast, 'unparse'):
                preview_lines = []
                for stmt in statements:
                    if self._is_docstring_or_comment(stmt):
                        continue
                    preview_lines.append(ast.unparse(stmt))
                return "\n".join(preview_lines)
            else:
                return str(statements)
        except Exception as e:
            _safe_print(f"Error generating block preview: {e}")
            return str(statements)
    
    def _compare_ast_blocks(self, block1: List[ast.stmt], block2: List[ast.stmt]) -> float:
        if len(block1) == 0 and len(block2) == 0:
            return 1.0
        if len(block1) == 0 or len(block2) == 0:
            return 0.0
        
        if len(block1) != len(block2):
            return self._compare_ast_structures(block1, block2)
        
        similarities = []
        for node1, node2 in zip(block1, block2):
            similarity = self._compare_ast_nodes_deep(node1, node2)
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _compare_ast_structures(self, block1: List[ast.stmt], block2: List[ast.stmt]) -> float:
        if not block1 or not block2:
            return 0.0
        
        similarities = []
        for node1 in block1:
            best_match = 0.0
            for node2 in block2:
                similarity = self._compare_ast_nodes_deep(node1, node2)
                best_match = max(best_match, similarity)
            similarities.append(best_match)
        
        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            length_ratio = min(len(block1), len(block2)) / max(len(block1), len(block2))
            return avg_similarity * length_ratio
        
        return 0.0
    
    def _compare_ast_nodes_deep(self, node1: ast.AST, node2: ast.AST) -> float:
        if type(node1) != type(node2):
            return 0.0
        
        comparators = {
            ast.Assign: self._compare_assign_nodes,
            ast.AugAssign: self._compare_augassign_nodes,
            ast.Assert: self._compare_assert_nodes,
            ast.Return: self._compare_return_nodes,
            ast.If: self._compare_if_nodes,
            ast.For: self._compare_for_nodes,
            ast.While: self._compare_while_nodes,
            ast.With: self._compare_with_nodes,
            ast.Try: self._compare_try_nodes,
            ast.Raise: self._compare_raise_nodes,
        }
        
        node_type = type(node1)
        if node_type in comparators:
            return comparators[node_type](node1, node2)
        
        if isinstance(node1, ast.Expr) and isinstance(node1.value, ast.Call):
            if isinstance(node2, ast.Expr) and isinstance(node2.value, ast.Call):
                return self._compare_call_nodes(node1.value, node2.value)
            return 0.0
        
        return 0.8
    
    def _compare_assign_nodes(self, node1: ast.Assign, node2: ast.Assign) -> float:
        if len(node1.targets) != len(node2.targets):
            return 0.5
        
        value_sim = self._compare_expr_structure(node1.value, node2.value)
        return 0.7 + 0.3 * value_sim
    
    def _compare_augassign_nodes(self, node1: ast.AugAssign, node2: ast.AugAssign) -> float:
        if type(node1.op) != type(node2.op):
            return 0.5
        return 0.9
    
    def _compare_call_nodes(self, node1: ast.Call, node2: ast.Call) -> float:
        arg_count1 = len(node1.args) + len(node1.keywords)
        arg_count2 = len(node2.args) + len(node2.keywords)
        
        if arg_count1 != arg_count2:
            return 0.6
        
        func_sim = self._compare_expr_structure(node1.func, node2.func)
        
        arg_sims = []
        for a1, a2 in zip(node1.args, node2.args):
            arg_sims.append(self._compare_expr_structure(a1, a2))
        
        avg_arg_sim = sum(arg_sims) / len(arg_sims) if arg_sims else 1.0
        
        return 0.5 + 0.3 * func_sim + 0.2 * avg_arg_sim
    
    def _compare_assert_nodes(self, node1: ast.Assert, node2: ast.Assert) -> float:
        test_sim = self._compare_expr_structure(node1.test, node2.test)
        return 0.8 + 0.2 * test_sim
    
    def _compare_return_nodes(self, node1: ast.Return, node2: ast.Return) -> float:
        if node1.value is None and node2.value is None:
            return 1.0
        if node1.value is None or node2.value is None:
            return 0.5
        return 0.7 + 0.3 * self._compare_expr_structure(node1.value, node2.value)
    
    def _compare_if_nodes(self, node1: ast.If, node2: ast.If) -> float:
        test_sim = self._compare_expr_structure(node1.test, node2.test)
        body_sim = self._compare_ast_structures(node1.body, node2.body)
        orelse_sim = self._compare_ast_structures(node1.orelse, node2.orelse)
        return 0.3 * test_sim + 0.5 * body_sim + 0.2 * orelse_sim
    
    def _compare_for_nodes(self, node1: ast.For, node2: ast.For) -> float:
        body_sim = self._compare_ast_structures(node1.body, node2.body)
        orelse_sim = self._compare_ast_structures(node1.orelse, node2.orelse)
        return 0.8 * body_sim + 0.2 * orelse_sim
    
    def _compare_while_nodes(self, node1: ast.While, node2: ast.While) -> float:
        test_sim = self._compare_expr_structure(node1.test, node2.test)
        body_sim = self._compare_ast_structures(node1.body, node2.body)
        return 0.3 * test_sim + 0.7 * body_sim
    
    def _compare_with_nodes(self, node1: ast.With, node2: ast.With) -> float:
        if len(node1.items) != len(node2.items):
            return 0.5
        body_sim = self._compare_ast_structures(node1.body, node2.body)
        return 0.7 + 0.3 * body_sim
    
    def _compare_try_nodes(self, node1: ast.Try, node2: ast.Try) -> float:
        body_sim = self._compare_ast_structures(node1.body, node2.body)
        handlers_sim = 1.0 if len(node1.handlers) == len(node2.handlers) else 0.5
        orelse_sim = self._compare_ast_structures(node1.orelse, node2.orelse)
        finalbody_sim = self._compare_ast_structures(node1.finalbody, node2.finalbody)
        return 0.4 * body_sim + 0.2 * handlers_sim + 0.2 * orelse_sim + 0.2 * finalbody_sim
    
    def _compare_raise_nodes(self, node1: ast.Raise, node2: ast.Raise) -> float:
        if node1.exc is None and node2.exc is None:
            return 1.0
        if node1.exc is None or node2.exc is None:
            return 0.5
        return 0.7 + 0.3 * self._compare_expr_structure(node1.exc, node2.exc)
    
    def _compare_expr_structure(self, expr1: ast.expr, expr2: ast.expr) -> float:
        if type(expr1) != type(expr2):
            return 0.0
        
        if isinstance(expr1, ast.Call):
            return self._compare_call_nodes(expr1, expr2)
        if isinstance(expr1, ast.Attribute):
            return 0.8 + 0.2 * self._compare_expr_structure(expr1.value, expr2.value)
        if isinstance(expr1, ast.Name):
            return 0.9
        if isinstance(expr1, ast.Constant):
            return 0.8 if type(expr1.value) == type(expr2.value) else 0.5
        if isinstance(expr1, ast.BinOp):
            return self._compare_binop_expr(expr1, expr2)
        if isinstance(expr1, ast.UnaryOp):
            return self._compare_unaryop_expr(expr1, expr2)
        if isinstance(expr1, ast.Compare):
            return self._compare_compare_expr(expr1, expr2)
        return 0.7
    
    def _compare_binop_expr(self, expr1: ast.BinOp, expr2: ast.BinOp) -> float:
        if type(expr1.op) != type(expr2.op):
            return 0.3
        left_sim = self._compare_expr_structure(expr1.left, expr2.left)
        right_sim = self._compare_expr_structure(expr1.right, expr2.right)
        return 0.5 + 0.25 * left_sim + 0.25 * right_sim
    
    def _compare_unaryop_expr(self, expr1: ast.UnaryOp, expr2: ast.UnaryOp) -> float:
        if type(expr1.op) != type(expr2.op):
            return 0.3
        return 0.7 + 0.3 * self._compare_expr_structure(expr1.operand, expr2.operand)
    
    def _compare_compare_expr(self, expr1: ast.Compare, expr2: ast.Compare) -> float:
        if len(expr1.ops) != len(expr2.ops) or len(expr1.comparators) != len(expr2.comparators):
            return 0.4
        left_sim = self._compare_expr_structure(expr1.left, expr2.left)
        return 0.6 + 0.4 * left_sim
    
    def _log_violation_details(self, file_path: Path, violations: List[Dict[str, Any]], lines: List[str]) -> None:
        if not violations:
            return
        
        
        _safe_print(f"\n[{file_path}] Found {len(violations)} duplication violation(s):")
        
        for idx, violation in enumerate(violations, 1):
            line_num = violation.get('line_number', '?')
            msg = violation.get('violation_message', '')
            
            _safe_print(f"\n  Violation {idx} (line {line_num}):")
            
            if 'Location (' in msg:
                parts = msg.split('Location (')
                locations_found = []
                
                for part in parts[1:]:
                    if '):' in part:
                        location_part = part.split('):')[0]
                        
                        try:
                            func_name, line_range = location_part.split(':')
                            start_line, end_line = line_range.split('-')
                            locations_found.append((func_name, int(start_line), int(end_line)))
                        except ValueError:
                            logger.debug(f'Could not parse location: {location_part}')
                
                for loc_idx, (func_name, start_line, end_line) in enumerate(locations_found, 1):
                    _safe_print(f"\n    Location {loc_idx}: {func_name}() at lines {start_line}-{end_line}")
                    
                    if start_line is not None and end_line is not None and lines:
                        start_idx = max(0, start_line - 1)
                        end_idx = min(len(lines), end_line)
                        
                        if start_idx < len(lines) and end_idx > start_idx:
                            code_block = lines[start_idx:end_idx]
                            _safe_print(f"    {'-' * 70}")
                            for line_num, code_line in enumerate(code_block, start=start_line):
                                _safe_print(f"    {line_num:4d} | {code_line}")
                            _safe_print(f"    {'-' * 70}")
                        else:
                            _safe_print(f"    (Could not extract code: invalid line range)")
                    else:
                        _safe_print(f"    (Could not extract code: invalid location)")
            else:
                _safe_print(f"    {msg[:300]}...")
        
        _safe_print("")
    
    def _filter_files_by_package_proximity(
        self,
        changed_files: List[Path],
        all_files: List[Path],
        max_parent_levels: int = 3,
        max_files: int = 20
    ) -> List[Path]:
        """Filter all_files to only include files in nearby packages.
        
        Priority:
        1. Same package (immediate siblings)
        2. Parent package
        3. Parent's parent package (up to max_parent_levels)
        
        Stops adding files once max_files limit is reached.
        
        Args:
            changed_files: Files that were changed (to determine package context)
            all_files: All files available for comparison
            max_parent_levels: Maximum number of parent levels to traverse (default: 3)
            max_files: Maximum number of files to include in comparison (default: 20)
        
        Returns:
            Filtered list of files in nearby packages (up to max_files)
        """
        if not changed_files:
            return all_files[:max_files] if len(all_files) > max_files else all_files
        
        nearby_files = []
        seen_files = set()
        
        for changed_file in changed_files:
            if len(nearby_files) >= max_files:
                break
            
            changed_dir = changed_file.parent
            
            for file in all_files:
                if len(nearby_files) >= max_files:
                    break
                if file not in seen_files and file.parent == changed_dir:
                    nearby_files.append(file)
                    seen_files.add(file)
            
            current_dir = changed_dir
            for level in range(1, max_parent_levels + 1):
                if len(nearby_files) >= max_files:
                    break
                
                current_dir = current_dir.parent
                if not current_dir or current_dir == current_dir.parent:
                    break
                
                for file in all_files:
                    if len(nearby_files) >= max_files:
                        break
                    
                    if file in seen_files:
                        continue
                    
                    if file.parent == current_dir:
                        nearby_files.append(file)
                        seen_files.add(file)
                    elif file.parent.parent == current_dir:
                        nearby_files.append(file)
                        seen_files.add(file)
        
        if len(nearby_files) < len(all_files):
            _safe_print(f"[CROSS-FILE] Filtered to {len(nearby_files)} nearby files (from {len(all_files)} total, max: {max_files}) based on package proximity")
        
        return nearby_files
    
    def scan_cross_file(
        self = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None,
        all_test_files: Optional[List[Path]] = None,
        all_code_files: Optional[List[Path]] = None,
        status_writer: Optional[Any] = None,
        max_cross_file_comparisons: int = 20
    ) -> List[Dict[str, Any]]:
        violations = []
        
        if all_test_files is None:
            all_test_files = test_files
        if all_code_files is None:
            all_code_files = code_files
        
        changed_files = []
        if code_files:
            changed_files.extend(code_files)
        if test_files:
            changed_files.extend(test_files)
        
        all_files = []
        if all_code_files:
            all_files.extend(all_code_files)
        if all_test_files:
            all_files.extend(all_test_files)
        
        if not changed_files or not all_files:
            return violations
        
        all_files = self._filter_files_by_package_proximity(changed_files, all_files, max_files=max_cross_file_comparisons)
        
        if len(changed_files) < len(all_files):
            _safe_print(f"\n[CROSS-FILE] Incremental scan: Checking {len(changed_files)} changed file(s) against {len(all_files)} total files...")
        else:
            _safe_print(f"\n[CROSS-FILE] Full scan: Scanning {len(all_files)} files for cross-file duplication...")
        import sys
        
        def write_status(msg: str):
            if status_writer and hasattr(status_writer, 'write_cross_file_progress'):
                try:
                    status_writer.write_cross_file_progress(msg)
                except Exception as e:
                    logger.debug(f'Could not write to status file: {type(e).__name__}: {e}')
        
        write_status(f"\n## Cross-File Duplication Analysis")
        write_status(f"Scanning {len(changed_files)} changed file(s) against {len(all_files)} total files...")
        
        changed_blocks = []
        all_blocks = []
        
        _safe_print(f"[CROSS-FILE] Extracting blocks from {len(changed_files)} changed file(s)...")
        for file_idx, file_path in enumerate(changed_files):
            if file_idx % 10 == 0:
                _safe_print(f"[CROSS-FILE] Changed files: {file_idx}/{len(changed_files)} - {file_path.name}")
                sys.stdout.flush()
            if not file_path.exists():
                continue
            
            try:
                file_size = file_path.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    _safe_print(f"Skipping large file ({file_size/1024:.1f}KB): {file_path}")
                    continue
            except Exception as e:
                logger.debug(f'Error checking file size for {file_path}: {type(e).__name__}: {e}')
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                lines = content.split('\n')
                
                functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_body = ast.unparse(node.body) if hasattr(ast, 'unparse') else str(node.body)
                        functions.append((node.name, func_body, node.lineno, node))
                
                for func_tuple in functions:
                    if len(func_tuple) == 5:
                        func_name, func_body, func_line, func_node, _ = func_tuple
                    else:
                        func_name, func_body, func_line, func_node = func_tuple
                    blocks = self._extract_code_blocks(func_node, func_line, func_name)
                    for block in blocks:
                        block['file_path'] = file_path
                        block['lines'] = lines
                        changed_blocks.append(block)
                        
            except (SyntaxError, UnicodeDecodeError) as e:
                logger.debug(f'Skipping file {file_path} due to {type(e).__name__}: {e}')
                continue
            except Exception as e:
                _safe_print(f"Error processing {file_path} for cross-file scan: {e}")
                continue
        
        _safe_print(f"\n[CROSS-FILE] Extracting blocks from {len(all_files)} reference file(s)...")
        cache_hits = 0
        cache_misses = 0
        
        for file_idx, file_path in enumerate(all_files):
            if file_idx % 10 == 0:
                _safe_print(f"[CROSS-FILE] Reference files: {file_idx}/{len(all_files)} - {file_path.name} (cache: {cache_hits} hits, {cache_misses} misses)")
                sys.stdout.flush()
            
            if not file_path.exists():
                continue
            
            cached_blocks = self._load_blocks_from_cache(file_path)
            if cached_blocks is not None:
                cache_hits += 1
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    for block in cached_blocks:
                        block['file_path'] = file_path
                        block['lines'] = lines
                        all_blocks.append(block)
                except Exception as e:
                    logger.debug(f'Error rehydrating cached blocks for {file_path}: {e}')
                continue
            
            cache_misses += 1
            
            try:
                file_size = file_path.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    _safe_print(f"Skipping large file ({file_size/1024:.1f}KB): {file_path}")
                    continue
            except Exception as e:
                logger.debug(f'Error checking file size for {file_path}: {type(e).__name__}: {e}')
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))
                lines = content.split('\n')
                
                functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_body = ast.unparse(node.body) if hasattr(ast, 'unparse') else str(node.body)
                        functions.append((node.name, func_body, node.lineno, node))
                
                file_blocks = []
                for func_tuple in functions:
                    if len(func_tuple) == 5:
                        func_name, func_body, func_line, func_node, _ = func_tuple
                    else:
                        func_name, func_body, func_line, func_node = func_tuple
                    blocks = self._extract_code_blocks(func_node, func_line, func_name)
                    for block in blocks:
                        block['file_path'] = file_path
                        block['lines'] = lines
                        all_blocks.append(block)
                        file_blocks.append(block)
                
                self._save_blocks_to_cache(file_path, file_blocks)
                        
            except (SyntaxError, UnicodeDecodeError) as e:
                logger.debug(f'Skipping file {file_path} due to {type(e).__name__}: {e}')
                continue
            except Exception as e:
                _safe_print(f"Error processing {file_path} for cross-file scan: {e}")
                continue
        
        _safe_print(f"[CROSS-FILE] Cache statistics: {cache_hits} hits, {cache_misses} misses ({cache_hits/(cache_hits+cache_misses)*100:.1f}% hit rate)" if (cache_hits + cache_misses) > 0 else "[CROSS-FILE] No files processed")
        
        _safe_print(f"\n[CROSS-FILE] Extracted {len(changed_blocks)} blocks from changed files, {len(all_blocks)} blocks from all files")
        write_status(f"Extracted {len(changed_blocks)} changed blocks, {len(all_blocks)} reference blocks")
        
        SIMILARITY_THRESHOLD = 0.90
        compared_pairs = set()
        total_comparisons = len(changed_blocks) * len(all_blocks)
        comparison_count = 0
        last_progress = 0
        
        _safe_print(f"[CROSS-FILE] Starting {total_comparisons:,} pairwise comparisons (changed vs all)...")
        write_status(f"Starting {total_comparisons:,} pairwise comparisons...")
        
        start_time = datetime.now()
        last_report_time = start_time
        REPORT_INTERVAL_SECONDS = 10
        REPORT_INTERVAL_COMPARISONS = 50000
        last_comparison_report = 0
        
        for i, block1 in enumerate(changed_blocks):
            for j, block2 in enumerate(all_blocks):
                if block1['file_path'] == block2['file_path']:
                    continue
                
                if (block1['file_path'] == block2['file_path'] and 
                    block1['start_line'] == block2['start_line'] and
                    block1['func_name'] == block2['func_name']):
                    continue
                
                comparison_count += 1
                
                now = datetime.now()
                elapsed_since_report = (now - last_report_time).total_seconds()
                progress_pct = (comparison_count * 100) // total_comparisons if total_comparisons > 0 else 0
                
                should_report = (
                    progress_pct >= last_progress + 5 or
                    comparison_count >= last_comparison_report + REPORT_INTERVAL_COMPARISONS or
                    elapsed_since_report >= REPORT_INTERVAL_SECONDS
                )
                
                if should_report:
                    elapsed_total = (now - start_time).total_seconds()
                    rate = comparison_count / max(1, elapsed_total)
                    remaining = total_comparisons - comparison_count
                    eta_seconds = int(remaining / max(1, rate))
                    progress_msg = f"Comparing: {progress_pct}% ({comparison_count:,}/{total_comparisons:,}) - {len(violations)} violations - ETA: {eta_seconds}s"
                    _safe_print(f"[CROSS-FILE] {progress_msg}")
                    write_status(progress_msg + "  ")
                    last_progress = progress_pct
                    last_report_time = now
                    last_comparison_report = comparison_count
                
                if 'ast_nodes' in block1 and 'ast_nodes' in block2:
                    ast_similarity = self._compare_ast_blocks(block1['ast_nodes'], block2['ast_nodes'])
                else:
                    ast_similarity = 0.0
                
                normalized_similarity = SequenceMatcher(None, block1['normalized'], block2['normalized']).ratio()
                
                preview1_normalized = ' '.join(block1['preview'].split())
                preview2_normalized = ' '.join(block2['preview'].split())
                content_similarity = SequenceMatcher(None, preview1_normalized, preview2_normalized).ratio()
                
                if ast_similarity >= SIMILARITY_THRESHOLD or (normalized_similarity >= SIMILARITY_THRESHOLD and content_similarity >= 0.85):
                    file1 = block1['file_path']
                    file2 = block2['file_path']
                    func1 = block1['func_name']
                    func2 = block2['func_name']
                    start1 = block1['start_line']
                    end1 = block1['end_line']
                    start2 = block2['start_line']
                    end2 = block2['end_line']
                    
                    preview1 = block1['preview']
                    preview2 = block2['preview']
                    
                    if len(preview1) > 300:
                        preview1 = preview1[:300] + '...'
                    if len(preview2) > 300:
                        preview2 = preview2[:300] + '...'
                    
                    location1 = f"{file1.name}:{func1} (lines {start1}-{end1})"
                    location2 = f"{file2.name}:{func2} (lines {start2}-{end2})"
                    
                    violation_message = (
                        f'Duplicate code detected across files - extract to shared function.\n\n'
                        f'Location 1 ({location1}):\n```python\n{preview1}\n```\n\n'
                        f'Location 2 ({location2}):\n```python\n{preview2}\n```'
                    )
                    
                    violation = Violation(
                        rule=self.rule,
                        violation_message=violation_message,
                        location=str(file1),
                        line_number=start1,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    
                    if len(violations) % 10 == 0:
                        write_status(f"Found {len(violations)} violations so far...")
                        sys.stdout.flush()
        
        complete_msg = f"Complete: {comparison_count} comparisons, {len(violations)} violations"
        _safe_print(f"\n[CROSS-FILE] {complete_msg}")
        write_status(complete_msg)
        write_status("")
        return violations

