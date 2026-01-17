from typing import List, Dict, Any, Optional
import logging
import re
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation
from vocabulary_helper import VocabularyHelper

logger = logging.getLogger(__name__)

class ActiveLanguageScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_actor_in_name(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_passive_voice(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_capability_nouns(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _check_actor_in_name(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        words = name.split()
        if not words:
            return None
        
        first_word = words[0].lower()
        actor_index = 0
        
        if first_word == 'the' and len(words) > 1:
            first_word = words[1].lower()
            actor_index = 1
        
        tags = VocabularyHelper.get_pos_tags(name)
        if tags:
            first_tag = tags[actor_index][1] if len(tags) > actor_index else None
            if first_tag and VocabularyHelper.is_verb_tag(first_tag):
                return None
        
        if VocabularyHelper.is_verb(first_word):
            return None
        
        common_verbs = {
            'init', 'load', 'save', 'run', 'get', 'set', 'add', 'del', 'rm', 'mv',
            'cp', 'mk', 'rmv', 'upd', 'gen', 'inv', 'exec', 'proc', 'build', 'render',
            'validate', 'check', 'verify', 'test', 'deploy', 'install', 'configure',
            'setup', 'start', 'stop', 'restart', 'close', 'open', 'read', 'write',
            'edit', 'modify', 'change', 'replace', 'insert', 'append', 'prepend',
            'merge', 'split', 'join', 'combine', 'separate', 'filter', 'sort',
            'search', 'find', 'locate', 'discover', 'detect', 'identify', 'recognize',
            'parse', 'analyze', 'evaluate', 'assess', 'measure', 'calculate', 'compute',
            'transform', 'convert', 'translate', 'map', 'route', 'forward', 'redirect',
            'send', 'receive', 'transmit', 'deliver', 'dispatch', 'submit', 'publish',
            'broadcast', 'notify', 'alert', 'warn', 'inform', 'report', 'log', 'record',
            'track', 'monitor', 'observe', 'watch', 'listen', 'collect', 'gather',
            'accumulate', 'aggregate', 'summarize', 'extract', 'retrieve', 'fetch',
            'pull', 'push', 'sync', 'synchronize', 'refresh', 'reload', 'restore',
            'recover', 'backup', 'export', 'import', 'upload', 'download', 'transfer',
            'migrate', 'upgrade', 'downgrade', 'uninstall', 'rollback', 'revert',
            'undo', 'redo', 'cancel', 'abort', 'terminate', 'kill', 'destroy', 'remove',
            'delete', 'clear', 'reset', 'initialize', 'prepare', 'arrange', 'organize',
            'structure', 'format', 'style', 'design', 'plan', 'schedule', 'queue',
            'prioritize', 'order', 'rank', 'group', 'categorize', 'classify', 'tag',
            'label', 'mark', 'flag', 'assign', 'allocate', 'distribute', 'share',
            'grant', 'revoke', 'permit', 'deny', 'allow', 'block', 'restrict', 'limit',
            'constrain', 'enforce', 'apply', 'implement', 'execute', 'perform',
            'complete', 'finish', 'end', 'conclude', 'finalize', 'close', 'abandon',
            'drop', 'discard', 'ignore', 'skip', 'omit', 'exclude', 'include', 'attach',
            'link', 'connect', 'join', 'merge', 'combine', 'unite', 'unify', 'integrate',
            'incorporate', 'embed', 'nest', 'wrap', 'unwrap', 'isolate', 'divide',
            'partition', 'segment', 'slice', 'chunk', 'batch', 'cluster', 'assemble',
            'compile', 'construct', 'create', 'generate', 'produce', 'manufacture',
            'fabricate', 'make', 'form', 'shape', 'mold', 'sculpt', 'carve', 'cut',
            'trim', 'prune', 'shave', 'polish', 'refine', 'improve', 'enhance',
            'optimize', 'tune', 'adjust', 'alter', 'transpose', 'rotate', 'flip',
            'reverse', 'invert', 'mirror', 'reflect', 'project', 'cast', 'throw',
            'emit', 'store', 'bootstrap', 'handle', 'resume', 'launch', 'display',
            'exit', 'advance', 'show', 'view', 'request', 'add', 'monitor', 'surface',
            'gather', 'access', 'update', 'filter', 'get', 'input', 'guards', 'stores',
            'load', 'forward', 'track', 'find', 'close', 'process', 'return', 'set',
            'clear', 'pass', 'document', 'save'
        }
        if first_word in common_verbs:
            return None
        
        if VocabularyHelper.is_actor_or_role(first_word):
            actor = words[actor_index]
            location = node.map_location()
            suggested_name = ' '.join(words[actor_index + 1:])
            if suggested_name:
                suggested_name = suggested_name[0].upper() + suggested_name[1:] if len(suggested_name) > 1 else suggested_name.upper()
            else:
                suggested_name = "[Verb Noun]"
            
            return Violation(
                rule=rule_obj,
                violation_message=f'{node_type.capitalize()} name "{name}" has actor "{actor}" in the name - actor should be in "users" field, not in name. Use Verb-Noun format: "{suggested_name}"',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _get_node_type(self, node: StoryNode) -> str:
        if isinstance(node, Epic):
            return 'epic'
        elif isinstance(node, SubEpic):
            return 'sub_epic'
        elif isinstance(node, Story):
            return 'story'
        return 'unknown'
    
    def _check_passive_voice(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        passive_voice_patterns = [
            r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were|be|been|being)\s+\w+en\b',
        ]
        
        for pattern in passive_voice_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return self._create_passive_voice_violation(name, node, node_type, rule_obj)
        
        return None
    
    def _create_passive_voice_violation(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Dict[str, Any]:
        location = node.map_location()
        return Violation(
            rule=rule_obj,
            violation_message=f'{node_type.capitalize()} name "{name}" uses passive voice - use active voice (e.g., "Places Order" not "Order is placed")',
            location=location,
            severity='error'
        ).to_dict()
    
    def _check_capability_nouns(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        capability_noun_patterns = [
            r'\b[A-Z]\w+(ing|ment|ance|ence)\b$',
            r'.*\s+[A-Z]\w+(ing|ment|ance|ence)\b$',
        ]
        
        for pattern in capability_noun_patterns:
            if not re.search(pattern, name):
                continue
            
            if len(name.split()) >= 3:
                break
            
            if any(re.search(r'\b' + exclude + r'\b', name, re.IGNORECASE) for exclude in ["User Story", "Epic", "Feature"]):
                continue
            
            return self._create_capability_noun_violation(name, node, node_type, rule_obj, "capability noun")
        
        return None
    
    def _create_capability_noun_violation(self, name: str, node: StoryNode, node_type: str, rule_obj: Any, noun_type: str) -> Dict[str, Any]:
        location = node.map_location()
        message = f'{node_type.capitalize()} name "{name}" uses capability noun'
        if noun_type == "gerund":
            message += ' (gerund)'
        message += ' - use active behavioral language (e.g., "Processes Payments" not "Payment Processing")'
        
        return Violation(
            rule=rule_obj,
            violation_message=message,
            location=location,
            severity='error'
        ).to_dict()

