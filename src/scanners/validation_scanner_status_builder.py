import logging
from pathlib import Path
from typing import Dict, Any, List
from actions.validate.validation_stats import ValidationStats
logger = logging.getLogger(__name__)

MAX_VIOLATION_DENSITY_FOR_GOOD_STATUS = 200
MAX_RULES_WITH_ERRORS_FOR_GOOD_STATUS = 5

class ValidationScannerStatusBuilder:

    def __init__(self, check_violation_severities_fn, rule_name_to_anchor_fn):
        self._check_violation_severities = check_violation_severities_fn
        self._rule_name_to_anchor = rule_name_to_anchor_fn

    def build_scanner_status(self, validation_rules: List[Dict[str, Any]], build_status_summary_fn) -> List[str]:
        lines = ['## Scanner Execution Status', '']
        categorized = self._categorize_rules(validation_rules)
        stats = self._build_stats(validation_rules, categorized)
        lines.extend(build_status_summary_fn(stats))
        lines.append('')
        lines.extend(self._format_executed_rules(categorized['executed']))
        lines.extend(self._format_failed_rules(categorized['load_failed'], 'Scanner Load Failures', 'LOAD FAILED'))
        lines.extend(self._format_failed_rules(categorized['execution_failed'], 'Scanner Execution Failures', 'EXECUTION FAILED'))
        lines.extend(self._format_no_scanner_rules(categorized['no_scanner']))
        return lines

    def _categorize_rules(self, validation_rules: List[Dict[str, Any]]) -> Dict[str, List]:
        result = {'executed': [], 'load_failed': [], 'execution_failed': [], 'no_scanner': []}
        for rule_dict in validation_rules:
            rule_file = rule_dict.get('rule_file', 'unknown')
            scanner_status = rule_dict.get('scanner_status', {})
            status = scanner_status.get('status', 'UNKNOWN')
            self._categorize_rule_by_status(status, rule_dict, rule_file, scanner_status, result)
        return result

    def _categorize_rule_by_status(self, status: str, rule_dict: Dict, rule_file: str, scanner_status: Dict, result: Dict):
        if status == 'EXECUTED':
            result['executed'].append(self._build_executed_rule_info(rule_dict, rule_file, scanner_status))
            return
        if status == 'LOAD_FAILED':
            result['load_failed'].append(self._build_failed_rule_info(rule_file, scanner_status))
            return
        if status == 'EXECUTION_FAILED':
            result['execution_failed'].append(self._build_failed_rule_info(rule_file, scanner_status))
            return
        if status == 'NO_SCANNER':
            result['no_scanner'].append(rule_file)

    def _build_failed_rule_info(self, rule_file: str, scanner_status: Dict) -> Dict:
        return {'rule': rule_file, 'scanner_path': scanner_status.get('scanner_path', 'unknown'), 'error': scanner_status.get('error', 'Unknown error')}

    def _build_executed_rule_info(self, rule_dict: Dict, rule_file: str, scanner_status: Dict) -> Dict:
        violations = scanner_status.get('violations_found', 0)
        scanner_results = rule_dict.get('scanner_results', {})
        has_errors, has_warnings = self._check_violation_severities(scanner_results)
        return {'rule': rule_file, 'violations': violations, 'execution_status': scanner_status.get('execution_status', 'SUCCESS'), 'scanner_path': scanner_status.get('scanner_path', 'unknown'), 'has_errors': has_errors, 'has_warnings': has_warnings}

    def _build_stats(self, validation_rules: List[Dict], categorized: Dict) -> ValidationStats:
        executed = categorized['executed']
        return ValidationStats(total_rules=len(validation_rules), total_with_scanners=len(executed) + len(categorized['load_failed']) + len(categorized['execution_failed']), executed_count=len(executed), load_failed_count=len(categorized['load_failed']), execution_failed_count=len(categorized['execution_failed']), no_scanner_count=len(categorized['no_scanner']), total_violations=sum((r['violations'] for r in executed)), rules_clean=sum((1 for r in executed if r['violations'] == 0 and (not r['has_errors']) and (not r['has_warnings']))), rules_with_warnings=sum((1 for r in executed if r['has_warnings'] and (not r['has_errors']))), rules_with_errors=sum((1 for r in executed if r['has_errors'])), executed_rules=executed)

    def _format_executed_rules(self, executed_rules: List[Dict]) -> List[str]:
        if not executed_rules:
            return []
        lines = ['### 🟩 Successfully Executed Scanners', '']
        executed_rules.sort(key=lambda x: (-x['violations'], x['rule']))
        for rule_info in executed_rules:
            lines.extend(self._format_executed_rule_line(rule_info))
        lines.append('')
        return lines

    def _format_executed_rule_line(self, rule_info: Dict) -> List[str]:
        violations = rule_info['violations']
        rule_name = Path(rule_info['rule']).stem if rule_info['rule'] else 'unknown'
        status_indicator, status_text = self._get_status_indicator(rule_info)
        violations_text = f'{violations} violation(s)' if violations > 0 else '0 violations'
        anchor_link = self._rule_name_to_anchor(rule_name)
        rule_display_name = rule_name.replace('_', ' ').title()
        details_link = f" - [View Details](#{rule_name.replace('_', '-').lower()}-violations)" if violations > 0 else ''
        exec_status = rule_info.get('execution_status', 'SUCCESS')
        status_suffix = f'({exec_status})' if exec_status != 'SUCCESS' else f'({status_text})'
        return [f'- {status_indicator} **[{rule_display_name}]({anchor_link})** - {violations_text} {status_suffix}{details_link}', f"  - Scanner: `{rule_info['scanner_path']}`"]

    def _get_status_indicator(self, rule_info: Dict) -> tuple:
        if rule_info['has_errors']:
            return ('🟥', 'ERRORS')
        if rule_info['has_warnings']:
            return ('🟨', 'WARNINGS')
        if rule_info['violations'] == 0:
            return ('🟩', 'CLEAN')
        return ('🟨', 'VIOLATIONS')

    def _format_failed_rules(self, failed_rules: List[Dict], title: str, status: str) -> List[str]:
        if not failed_rules:
            return []
        lines = [f'### 🟥 {title}', '']
        for rule_info in failed_rules:
            rule_name = Path(rule_info['rule']).stem if rule_info['rule'] else 'unknown'
            anchor_link = self._rule_name_to_anchor(rule_name)
            rule_display_name = rule_name.replace('_', ' ').title()
            lines.append(f'- 🟥 **[{rule_display_name}]({anchor_link})** - {status}')
            lines.append(f"  - Scanner Path: `{rule_info['scanner_path']}`")
            lines.append(f"  - Error: `{rule_info['error']}`")
        lines.append('')
        return lines

    def _format_no_scanner_rules(self, no_scanner_rules: List[str]) -> List[str]:
        if not no_scanner_rules:
            return []
        lines = ['### [i] Rules Without Scanners', '']
        for rule_file in no_scanner_rules[:10]:
            rule_name = Path(rule_file).stem if rule_file else 'unknown'
            anchor_link = self._rule_name_to_anchor(rule_name)
            lines.append(f"- [i] **[{rule_name.replace('_', ' ').title()}]({anchor_link})** - No scanner configured")
        if len(no_scanner_rules) > 10:
            lines.append(f'- *... and {len(no_scanner_rules) - 10} more rules without scanners*')
        lines.append('')
        return lines

    def build_status_summary(self, stats: ValidationStats) -> List[str]:
        lines = []
        overall_status, overall_text = self._get_overall_status(stats)
        lines.append(f'### {overall_status} Overall Status: {overall_text}')
        lines.append('')
        lines.extend(self._build_summary_table(stats))
        lines.extend(self._build_totals_summary(stats))
        return lines

    def _get_overall_status(self, stats: ValidationStats) -> tuple:
        if stats.execution_failed_count > 0:
            return ('🟥', 'CRITICAL ISSUES')
        if stats.load_failed_count > 2:
            return ('🟥', 'CRITICAL ISSUES')
        
        if not stats.has_violations:
            return ('🟩', 'ALL CLEAN')
        
        violation_density = stats.total_violations
        
        if violation_density < 150 and stats.rules_with_errors == 0:
            return ('🟩', 'HEALTHY')
        if violation_density < MAX_VIOLATION_DENSITY_FOR_GOOD_STATUS and stats.rules_with_errors <= MAX_RULES_WITH_ERRORS_FOR_GOOD_STATUS:
            return ('🟨', 'GOOD - Minor Issues')
        
        if stats.rules_with_errors > 0:
            return ('🟨', 'NEEDS ATTENTION')
        
        return ('🟨', 'WARNINGS FOUND')

    def _build_summary_table(self, stats: ValidationStats) -> List[str]:
        lines = ['| Status | Count | Description |', '|--------|-------|-------------|']
        if stats.executed_count > 0:
            desc = 'Scanners ran without errors' if stats.rules_clean > 0 else 'Scanners executed'
            lines.append(f'| 🟩 Executed Successfully | {stats.executed_count} | {desc} |')
        if stats.rules_clean > 0:
            lines.append(f'| 🟩 Clean Rules | {stats.rules_clean} | No violations found |')
        if stats.rules_with_warnings > 0:
            warning_count = sum((r['violations'] for r in stats.executed_rules if r.get('has_warnings') and (not r.get('has_errors'))))
            lines.append(f'| 🟨 Rules with Warnings | {stats.rules_with_warnings} | Found {warning_count} warning violation(s) |')
        if stats.rules_with_errors > 0:
            error_count = sum((r['violations'] for r in stats.executed_rules if r.get('has_errors')))
            lines.append(f'| 🟥 Rules with Errors | {stats.rules_with_errors} | Found {error_count} error violation(s) |')
        if stats.load_failed_count > 0:
            lines.append(f'| 🟥 Load Failed | {stats.load_failed_count} | Scanner could not be loaded |')
        if stats.execution_failed_count > 0:
            lines.append(f'| 🟥 Execution Failed | {stats.execution_failed_count} | Scanner crashed during execution |')
        if stats.no_scanner_count > 0:
            lines.append(f'| [i] No Scanner | {stats.no_scanner_count} | Rule has no scanner configured |')
        lines.append('')
        return lines

    def _build_totals_summary(self, stats: ValidationStats) -> List[str]:
        lines = [f'**Total Rules:** {stats.total_rules}', f'- **Rules with Scanners:** {stats.total_with_scanners}', f'  - 🟩 **Executed Successfully:** {stats.executed_count}']
        if stats.load_failed_count > 0:
            lines.append(f'  - 🟥 **Load Failed:** {stats.load_failed_count}')
        if stats.execution_failed_count > 0:
            lines.append(f'  - 🟥 **Execution Failed:** {stats.execution_failed_count}')
        if stats.no_scanner_count > 0:
            lines.append(f'- [i] **Rules without Scanners:** {stats.no_scanner_count}')
        return lines

    def build_validation_rules(self, validation_rules: List[Dict[str, Any]]) -> List[str]:
        lines = ['## Validation Rules Checked', '']
        rule_status_lookup = self._build_rule_status_lookup(validation_rules, self._check_violation_severities)
        sorted_rules = sorted(validation_rules, key=lambda r: self._rule_sort_key(r, rule_status_lookup))
        for rule_dict in sorted_rules[:20]:
            lines.extend(self._format_rule_entry(rule_dict, rule_status_lookup))
        if len(validation_rules) > 20:
            lines.append(f'*... and {len(validation_rules) - 20} more rules*')
            lines.append('')
        return lines

    def _build_rule_status_lookup(self, validation_rules: List[Dict], check_severities_fn) -> Dict:
        lookup = {}
        for rule_dict in validation_rules:
            rule_file = rule_dict.get('rule_file', 'unknown')
            scanner_status = rule_dict.get('scanner_status', {})
            status = scanner_status.get('status', 'UNKNOWN')
            has_errors, has_warnings = (False, False)
            if status == 'EXECUTED':
                has_errors, has_warnings = check_severities_fn(rule_dict.get('scanner_results', {}))
            lookup[rule_file] = {'status': status, 'violations': scanner_status.get('violations_found', 0), 'has_errors': has_errors, 'has_warnings': has_warnings, 'scanner_path': scanner_status.get('scanner_path', 'unknown'), 'execution_status': scanner_status.get('execution_status', 'SUCCESS'), 'error': scanner_status.get('error', None)}
        return lookup

    def _rule_sort_key(self, rule_dict: Dict, lookup: Dict) -> tuple:
        info = lookup.get(rule_dict.get('rule_file', 'unknown'), {})
        status, violations = (info.get('status', 'UNKNOWN'), info.get('violations', 0))
        if status in ('EXECUTION_FAILED', 'LOAD_FAILED'):
            return (0, 0, '')
        if info.get('has_errors'):
            return (1, -violations, rule_dict.get('rule_file', ''))
        if info.get('has_warnings'):
            return (2, -violations, rule_dict.get('rule_file', ''))
        if violations == 0 and status == 'EXECUTED':
            return (3, 0, rule_dict.get('rule_file', ''))
        return (4, 0, rule_dict.get('rule_file', ''))

    def _format_rule_entry(self, rule_dict: Dict, lookup: Dict) -> List[str]:
        rule_file = rule_dict.get('rule_file', 'unknown')
        rule_name = Path(rule_file).stem if rule_file else 'unknown'
        description = rule_dict.get('rule_content', rule_dict).get('description', 'No description')
        info = lookup.get(rule_file, {})
        status_indicator, status_text = self._get_rule_status_display(info)
        anchor_id = rule_name.replace('_', '-').lower()
        rule_title = rule_name.replace('_', ' ').title()
        violations_link = f' - [View Details](#{anchor_id}-violations)' if info.get('violations', 0) > 0 else ''
        lines = [f'### {status_indicator} Rule: <span id="{anchor_id}">{rule_title}</span> - {status_text}{violations_link}', f'**Description:** {description}']
        lines.extend(self._format_rule_scanner_info(info))
        lines.append('')
        return lines

    def _get_rule_status_display(self, info: Dict) -> tuple:
        status, violations = (info.get('status', 'UNKNOWN'), info.get('violations', 0))
        if status in ('EXECUTION_FAILED', 'LOAD_FAILED'):
            return ('🟥', 'FAILED')
        if status == 'NO_SCANNER':
            return ('[i]', 'NO SCANNER')
        if info.get('has_errors'):
            return ('🟥', f'{violations} ERROR(S)')
        if info.get('has_warnings'):
            return ('🟨', f'{violations} WARNING(S)')
        if violations == 0:
            return ('🟩', 'CLEAN (0 violations)')
        return ('🟨', f'{violations} VIOLATION(S)')

    def _format_rule_scanner_info(self, info: Dict) -> List[str]:
        lines = []
        status = info.get('status', 'UNKNOWN')
        scanner_path = info.get('scanner_path', 'unknown')
        if status == 'EXECUTED':
            if scanner_path != 'unknown':
                lines.append(f'**Scanner:** `{scanner_path}`')
            if info.get('execution_status', 'SUCCESS') != 'SUCCESS':
                lines.append(f"**Execution Status:** {info['execution_status']}")
        elif status in ('LOAD_FAILED', 'EXECUTION_FAILED'):
            if scanner_path != 'unknown':
                lines.append(f'**Scanner:** `{scanner_path}`')
            if info.get('error'):
                lines.append(f"**Error:** `{info['error']}`")
        elif status == 'NO_SCANNER':
            lines.append('**Scanner:** Not configured')
        return lines
