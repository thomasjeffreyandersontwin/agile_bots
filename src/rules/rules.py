from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Iterator, Dict, Any, TYPE_CHECKING, Callable
from pathlib import Path
from .rule import Rule
from .rule_loader import RuleLoader
from .rule_filter import RuleFilter
from ..actions.build.story_graph_data import StoryGraphData
from ..story_graph.story_graph import StoryGraph
from ..actions.validate.validation_scope import ValidationScope
if TYPE_CHECKING:
    from ..actions.action_context import ValidateActionContext

@dataclass
class ValidationCallbacks:
    on_scanner_start: Optional[Callable] = None
    on_scanner_complete: Optional[Callable] = None
    on_file_scanned: Optional[Callable] = None

@dataclass
class ValidationContext:
    story_graph: Dict[str, Any]
    files: Dict[str, List[Path]]
    callbacks: ValidationCallbacks
    skiprule: List[str]
    exclude: List[str]
    skip_cross_file: bool
    all_files: bool
    behavior: Any
    bot_paths: Any
    working_dir: Path
    status_writer: Optional[Any] = None
    max_cross_file_comparisons: int = 20

    @classmethod
    def from_action_context(cls, behavior, context: 'ValidateActionContext', callbacks: Optional[ValidationCallbacks] = None) -> 'ValidationContext':
        story_graph_data = StoryGraphData(behavior)
        story_graph = StoryGraph(behavior.bot_paths, behavior.bot_paths.workspace_directory, story_graph_spec=story_graph_data.story_graph_spec)
        validation_scope = ValidationScope.from_context(context, behavior.bot_paths, behavior_name=behavior.name)
        
        story_graph_content = story_graph.content
        if context.scope:
            story_graph_content = validation_scope.filter_story_graph(story_graph_content)
        
        files = cls._get_files_for_validation(behavior, context)
        
        skiprule = context.scope.skiprule if context.scope else []
        exclude = context.scope.exclude if context.scope else []
        
        return cls(
            story_graph=story_graph_content,
            files=files,
            callbacks=callbacks or ValidationCallbacks(),
            skiprule=skiprule,
            exclude=exclude,
            skip_cross_file=context.skip_cross_file,
            all_files=context.all_files,
            behavior=behavior,
            bot_paths=behavior.bot_paths,
            working_dir=behavior.bot_paths.workspace_directory,
            max_cross_file_comparisons=context.max_cross_file_comparisons
        )
    
    @classmethod
    def _get_files_for_validation(cls, behavior, context: 'ValidateActionContext') -> Dict[str, List[Path]]:
        from agile_bots.src.actions.validate.file_discovery import FileDiscovery
        from agile_bots.src.scope import ScopeType
        from agile_bots.src.actions.validate.validation_type import ValidationType
        
        validation_type = behavior.validation_type
        if validation_type == ValidationType.STORY_GRAPH:
            return {}

        if context.scope and context.scope.type == ScopeType.FILES:
            files_dict = {}
            for file_path_str in context.scope.value:
                file_path = Path(file_path_str)
                if 'test' in str(file_path).lower() or behavior.name in ('tests', 'test'):
                    if 'test' not in files_dict:
                        files_dict['test'] = []
                    files_dict['test'].append(file_path)
                else:
                    if 'src' not in files_dict:
                        files_dict['src'] = []
                    files_dict['src'].append(file_path)
            
            if context.scope.file_filter:
                filtered_files = {}
                for key, file_list in files_dict.items():
                    filtered = context.scope.filters_files(file_list)
                    if filtered:
                        filtered_files[key] = filtered
                return filtered_files
            
            return files_dict
        
        file_discovery = FileDiscovery(behavior.bot_paths, behavior.name, [])
        
        if behavior.name in ('tests', 'test'):
            all_files = {'test': file_discovery.discover_files_from_directory('test')}
        elif behavior.name == 'code':
            all_files = {'src': file_discovery.discover_files_from_directory('src')}
        else:
            all_files = {
                'test': file_discovery.discover_files_from_directory('test'),
                'src': file_discovery.discover_files_from_directory('src')
            }
        
        if context.scope and context.scope.file_filter:
            filtered_files = {}
            for key, file_list in all_files.items():
                filtered = context.scope.filters_files(file_list)
                if filtered:
                    filtered_files[key] = filtered
            return filtered_files
        
        return all_files
    
    @classmethod
    def from_parameters(cls, parameters: Dict[str, Any], behavior, bot_paths, callbacks: Optional[ValidationCallbacks] = None) -> 'ValidationContext':
        from agile_bots.src.actions.action_context import ValidateActionContext, Scope, ScopeType, FileFilter
        from agile_bots.src.bot.behavior import Behavior
        
        if isinstance(behavior, str):
            behavior = Behavior(name=behavior, bot_paths=bot_paths)
        
        scope = None
        if 'scope' in parameters and parameters['scope']:
            scope_dict = parameters['scope']
            if isinstance(scope_dict, dict):
                scope_type_str = scope_dict.get('type', 'all')
                scope_type = ScopeType(scope_type_str)
                scope = Scope(
                    type=scope_type,
                    value=scope_dict.get('value', []),
                    exclude=scope_dict.get('exclude', []),
                    skiprule=scope_dict.get('skiprule', [])
                )
        elif 'test' in parameters or 'src' in parameters:
            file_paths = []
            if 'test' in parameters:
                test_files = parameters['test']
                if isinstance(test_files, str):
                    file_paths.append(test_files)
                elif isinstance(test_files, list):
                    file_paths.extend(test_files)
            if 'src' in parameters:
                src_files = parameters['src']
                if isinstance(src_files, str):
                    file_paths.append(src_files)
                elif isinstance(src_files, list):
                    file_paths.extend(src_files)
            
            if file_paths:
                scope = Scope(
                    type=ScopeType.FILES,
                    value=file_paths,
                    exclude=[],
                    skiprule=[]
                )
        
        all_files = parameters.get('all_files', False) or parameters.get('force_full', False)
        
        context = ValidateActionContext(
            scope=scope,
            background=parameters.get('background'),
            skip_cross_file=parameters.get('skip_cross_file', False),
            all_files=all_files
        )
        
        return cls.from_action_context(behavior, context, callbacks)

    def should_skip_rule(self, rule_name: str) -> bool:
        return rule_name in self.skiprule

    def get_filtered_files(self, rules_instance: 'Rules') -> Dict[str, List[Path]]:
        if not self.exclude:
            return self.files
        return rules_instance._rule_filter.filter_files(self.files, self.exclude)

    def get_last_report_timestamp(self) -> float:
        logger = logging.getLogger(__name__)
        docs_path = self.bot_paths.documentation_path
        reports_dir = self.bot_paths.workspace_directory / docs_path / 'reports'
        logger.info(f'Looking for previous reports in: {reports_dir}')
        if not reports_dir.exists():
            logger.info('Reports directory does not exist - returning 0.0')
            return 0.0
        
        report_files = list(reports_dir.glob(f'{self.behavior.name}-validation-status-*.md'))
        logger.info(f'Found {len(report_files)} report files')
        if not report_files:
            logger.info('No report files found - returning 0.0')
            return 0.0
        
        current_time = time.time()
        previous_run_files = [f for f in report_files if (current_time - f.stat().st_mtime) > 10]
        logger.info(f'Found {len(previous_run_files)} previous run files (excluding files < 10 seconds old)')
        
        if not previous_run_files:
            logger.info('No previous run files found - returning 0.0')
            return 0.0
        
        most_recent = max(previous_run_files, key=lambda p: p.stat().st_mtime)
        logger.info(f'Most recent previous report: {most_recent.name} (timestamp: {most_recent.stat().st_mtime})')
        return most_recent.stat().st_mtime

    def filter_changed_files(self, files: Dict[str, List[Path]]) -> tuple:
        if self.all_files:
            return files, files
        
        last_report_time = self.get_last_report_timestamp()
        
        if last_report_time == 0.0:
            return files, files
        
        changed_files = {}
        for file_type, file_list in files.items():
            changed = [f for f in file_list if f.stat().st_mtime > last_report_time]
            changed_files[file_type] = changed
        
        return changed_files, files

class Rules:

    def __init__(self, behavior=None, bot_config=None, bot_paths=None):
        self.behavior = behavior
        self.bot_config = bot_config
        if behavior:
            if not bot_paths:
                raise ValueError('bot_paths is required when behavior is provided')
            self.bot_name = behavior.bot_name
            self.behavior_name = behavior.name
            self.bot_paths = bot_paths
        elif bot_config:
            self.bot_name = bot_config.name
            self.behavior_name = 'common'
            self.bot_paths = bot_paths
        else:
            raise ValueError('Either behavior or bot_config must be provided')
        self._rules: Optional[List[Rule]] = None
        self._all_violations: List[Dict[str, Any]] = []
        self._rule_loader = RuleLoader(self.bot_name, self.behavior_name, self.bot_paths, self.behavior)
        self._rule_filter = RuleFilter(self.bot_paths)

    def _load_rules(self) -> List[Rule]:
        if self._rules is not None:
            return self._rules
        all_rules = []
        
        bot_rules = self._rule_loader.load_bot_rules()
        all_rules.extend(bot_rules)
        
        if self.behavior:
            behavior_rules = self._rule_loader.load_behavior_rules()
            all_rules.extend(behavior_rules)
        
        self._rules = all_rules
        return self._rules

    def find_by_name(self, rule_name: str) -> Optional[Rule]:
        rules = self._load_rules()
        for rule in rules:
            if rule.name == rule_name:
                return rule
        return None

    def __iter__(self) -> Iterator[Rule]:
        rules = self._load_rules()
        for rule in rules:
            yield rule

    def __len__(self) -> int:
        return len(self._load_rules())

    def add_violations(self, violations: List[Dict[str, Any]]) -> None:
        self._all_violations.extend(violations)

    @property
    def violations(self) -> List[Dict[str, Any]]:
        return self._all_violations

    @property
    def violation_summary(self) -> List[str]:
        summary = []
        for rule in self._load_rules():
            if rule.has_scanner and rule.violations:
                file_by_file_count = len(rule.file_by_file_violations)
                cross_file_count = len(rule.cross_file_violations)
                if file_by_file_count > 0 or cross_file_count > 0:
                    summary.append(f'Rule {rule.rule_file}: {file_by_file_count} file-by-file, {cross_file_count} cross-file violations')
        return summary

    def formatted_rules(self) -> str:
        rules = self._load_rules()
        if not rules:
            return 'No validation rules found.'
        sorted_rules = sorted(rules, key=lambda r: r.priority)
        sections = []
        for rule in sorted_rules:
            sections.extend(rule.formatted_text())
        return '\n'.join(sections) if sections else 'No validation rules found.'

    def formatted_rules_digest(self) -> str:
        rules = self._load_rules()
        if not rules:
            return 'No validation rules found.'
        
        rules = sorted(rules, key=lambda r: r.priority)
        
        lines = ['Rules to follow:', '']
        for i, rule in enumerate(rules):
            description = rule.description or 'No description'
            lines.append(f"- **{rule.name}**: {description}")
            
            do_section = rule.rule_content.get('do', {})
            do_desc = do_section.get('description', '')
            if do_desc:
                lines.append(f"  DO: {do_desc}")
            
            dont_section = rule.rule_content.get('dont', {})
            dont_desc = dont_section.get('description', '')
            if dont_desc:
                lines.append(f"  DON'T: {dont_desc}")
            
            if i < len(rules) - 1:
                lines.append("")
        
        return '\n'.join(lines)

    def _has_scanner_error(self, execution_status: str, scanner_results: Any) -> bool:
        if execution_status.startswith('EXECUTION_FAILED') or execution_status.startswith('EXECUTION_SKIPPED'):
            return True
        if not isinstance(scanner_results, dict):
            return False
        if 'error' in scanner_results:
            return True
        file_by_file = scanner_results.get('file_by_file', {})
        return isinstance(file_by_file, dict) and 'error' in file_by_file

    def _extract_error_message(self, execution_status: str, scanner_results: Any) -> str:
        if execution_status.startswith('EXECUTION_FAILED'):
            return execution_status
        if not isinstance(scanner_results, dict):
            return f'Scanner execution failed: {execution_status}'
        if 'error' in scanner_results:
            return scanner_results['error']
        file_by_file = scanner_results.get('file_by_file', {})
        if isinstance(file_by_file, dict) and 'error' in file_by_file:
            return file_by_file['error']
        return f'Scanner execution failed: {execution_status}'

    def _flush_logger_handlers(self, logger) -> None:
        for handler in logger.handlers:
            handler.flush()
    
    def _convert_violations_to_dicts(self, data: Any) -> Any:
        if hasattr(data, 'to_dict'):
            return data.to_dict()
        elif isinstance(data, dict):
            return {k: self._convert_violations_to_dicts(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_violations_to_dicts(item) for item in data]
        else:
            return data

    def _process_scanner_result(self, rule, rule_result: dict, scanner_results: Any, scanner_path: str, scanner_name: str, logger) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        execution_status = rule.scanner_execution_status or 'SUCCESS'
        if self._has_scanner_error(execution_status, scanner_results):
            error_msg = self._extract_error_message(execution_status, scanner_results)
            logger.info(f'[{timestamp}] Completed scanner: {scanner_name} (rule: {rule.rule_file}) - FAILED: {error_msg}')
            self._flush_logger_handlers(logger)
            rule_result['scanner_status'] = {'status': 'EXECUTION_FAILED', 'scanner_path': scanner_path, 'error': error_msg}
            return f'  [ERROR] {rule.rule_file}: {error_msg}'
        violations_count = len(rule.violations)
        logger.info(f'[{timestamp}] Completed scanner: {scanner_name} (rule: {rule.rule_file}) - SUCCESS ({violations_count} violations)')
        self._flush_logger_handlers(logger)
        rule_result['scanner_status'] = {'status': 'EXECUTED', 'scanner_path': scanner_path, 'execution_status': execution_status, 'violations_found': violations_count}
        self.add_violations(rule.violations)
        return f'  [OK] {rule.rule_file}: Scanner executed successfully ({violations_count} violations)'

    def _execute_scanner(self, rule, rule_result: dict, context: ValidationContext, scanner_path: str, logger, files: Dict, changed_files: Dict, all_files: Dict) -> str:
        scanner_name = scanner_path.split('.')[-1] if '.' in scanner_path else scanner_path
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'[{timestamp}] Starting scanner: {scanner_name} (rule: {rule.rule_file})')
        self._flush_logger_handlers(logger)
        if context.callbacks.on_scanner_start:
            context.callbacks.on_scanner_start(rule.rule_file, scanner_path)
        try:
            max_cross_file = getattr(context, 'max_cross_file_comparisons', 20)
            from agile_bots.src.rules.scan_config import ScanConfig
            scan_config = ScanConfig(
                story_graph=context.story_graph,
                files=all_files or files,
                changed_files=changed_files,
                skip_cross_file=context.skip_cross_file,
                max_cross_file_comparisons=max_cross_file,
                on_file_scanned=context.callbacks.on_file_scanned,
                status_writer=context.status_writer
            )
            scanner_results = rule.scan(scan_config)
            rule_result['scanner_results'] = self._convert_violations_to_dicts(scanner_results)
            return self._process_scanner_result(rule, rule_result, scanner_results, scanner_path, scanner_name, logger)
        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_msg = f'Scanner execution failed: {str(e)}'
            logger.error(f'[{timestamp}] Completed scanner: {scanner_name} (rule: {rule.rule_file}) - EXCEPTION: {error_msg}')
            self._flush_logger_handlers(logger)
            logger.error(f'Scanner execution failed for rule {rule.rule_file}: {e}', exc_info=True)
            rule_result['scanner_status'] = {'status': 'EXECUTION_FAILED', 'scanner_path': scanner_path, 'error': error_msg}
            raise

    def _process_rule(self, rule, rule_result: dict, context: ValidationContext, logger, files: Dict, changed_files: Dict, all_files: Dict) -> str:
        scanner_path = rule.scanner_path
        if not scanner_path:
            rule_result['scanner_status'] = {'status': 'NO_SCANNER', 'scanner_path': None}
            return f'  [SKIP] {rule.rule_file}: No scanner defined'
        if not rule.has_scanner:
            load_error = rule.scanner_load_error or 'Unknown error - scanner class is None'
            rule_result['scanner_status'] = {'status': 'LOAD_FAILED', 'scanner_path': scanner_path, 'error': load_error}
            logger.error(f'Scanner failed to load for rule {rule.rule_file}: {load_error}')
            return f'  [FAILED] {rule.rule_file}: Scanner failed to load - {load_error}'
        return self._execute_scanner(rule, rule_result, context, scanner_path, logger, files, changed_files, all_files)

    def validate(self, context: ValidationContext, files: Optional[Dict[str, List[Path]]]=None, callbacks: Optional[ValidationCallbacks]=None, skiprule: Optional[List[str]]=None, exclude: Optional[List[str]]=None) -> List[Dict[str, Any]]:
        if isinstance(context, ValidationContext):
            return self._execute_validation(context)
        return self._execute_validation(self._create_legacy_context(context, files, callbacks, skiprule, exclude))

    def _create_legacy_context(self, story_graph: Dict, files: Optional[Dict], callbacks: Optional[ValidationCallbacks], skiprule: Optional[List[str]], exclude: Optional[List[str]]) -> ValidationContext:
        return ValidationContext(story_graph=story_graph, files=files or {}, callbacks=callbacks or ValidationCallbacks(), skiprule=skiprule or [], exclude=exclude or [], skip_cross_file=True, all_files=False, behavior=self.behavior, bot_paths=getattr(self, 'bot_paths', None), working_dir=Path.cwd())

    def _execute_validation(self, context: ValidationContext) -> List[Dict[str, Any]]:
        logger = logging.getLogger(__name__)
        self._log_validation_start(context, logger)
        processed_rules = self._process_all_rules(context, logger)
        return self._convert_violations_to_dicts(processed_rules)
    
    def _log_validation_start(self, context: ValidationContext, logger) -> None:
        logger.info('=== Starting rules validation ===')
        files = context.get_filtered_files(self)
        changed_files, all_files = context.filter_changed_files(files)
        files_to_scan_count = sum((len(f) for f in changed_files.values()))
        total_files_count = sum((len(f) for f in all_files.values()))
        if files_to_scan_count < total_files_count:
            logger.info(f'Incremental scan: {files_to_scan_count} changed file(s) out of {total_files_count} total files')
        else:
            logger.info(f'Full scan: {total_files_count} file(s)')
        rules_list = list(self)
        logger.info(f'Loaded {len(rules_list)} rules')
        if context.skiprule:
            logger.info(f'Skipping rules: {set(context.skiprule)}')
    
    def _process_all_rules(self, context: ValidationContext, logger) -> List[Dict[str, Any]]:
        processed_rules = []
        scanner_status_summary = []
        rules_list = list(self)
        files = context.get_filtered_files(self)
        changed_files, all_files = context.filter_changed_files(files)
        for idx, rule in enumerate(rules_list, 1):
            rule_name = Path(rule.rule_file).stem
            if context.should_skip_rule(rule_name):
                logger.info(f'Skipping rule {idx}/{len(rules_list)}: {rule.rule_file} (--skiprule)')
                scanner_status_summary.append(f'  [SKIP] {rule.rule_file}: Skipped by --skiprule')
                continue
            logger.info(f'Processing rule {idx}/{len(rules_list)}: {rule.rule_file}')
            rule_result = {'rule_file': rule.rule_file, 'rule_content': rule.rule_content, 'scanner_status': {}}
            try:
                status_line = self._process_rule(rule, rule_result, context, logger, files, changed_files, all_files)
                scanner_status_summary.append(status_line)
            except Exception:
                scanner_status_summary.append(f'  [ERROR] {rule.rule_file}: Scanner execution failed')
                raise
            processed_rules.append(rule_result)
            if context.callbacks.on_scanner_complete:
                context.callbacks.on_scanner_complete(rule_result)
        self._log_scanner_status_summary(scanner_status_summary, logger)
        return processed_rules
    
    def _log_scanner_status_summary(self, scanner_status_summary: List[str], logger) -> None:
        if scanner_status_summary:
            logger.info('=== SCANNER EXECUTION STATUS ===')
            for status_line in scanner_status_summary:
                logger.info(status_line)
            logger.info('=== END SCANNER STATUS ===')

