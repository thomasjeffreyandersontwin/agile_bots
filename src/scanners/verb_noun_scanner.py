from typing import List, Dict, Any, Optional, Tuple
import logging
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation
from vocabulary_helper import VocabularyHelper

import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet as wn

logger = logging.getLogger(__name__)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

class VerbNounScanner(StoryScanner):
    
    def scan_domain_concept(self, node: Any, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_verb_noun_order(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_gerund_ending(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_noun_verb_noun_pattern(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_noun_verb_pattern(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_actor_prefix(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_noun_only(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_third_person_singular(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _get_node_type(self, node: StoryNode) -> str:
        if isinstance(node, Epic):
            return 'epic'
        elif isinstance(node, SubEpic):
            return 'sub_epic'
        elif isinstance(node, Story):
            return 'story'
        return 'unknown'
    
    def _get_tokens_and_tags(self, text: str) -> Tuple[List[str], List[Tuple[str, str]]]:
        try:
            tokens = word_tokenize(text)
            tokens = [t for t in tokens if t.isalnum() or any(c.isalnum() for c in t)]
            tags = pos_tag(tokens)
            return tokens, tags
        except Exception:
            return [], []
    
    def _is_verb(self, tag: str) -> bool:
        verb_tags = ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']
        return tag in verb_tags
    
    def _is_noun(self, tag: str) -> bool:
        noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
        return tag in noun_tags
    
    def _is_proper_noun(self, tag: str) -> bool:
        proper_noun_tags = ['NNP', 'NNPS']
        return tag in proper_noun_tags
    
    def _can_be_verb(self, word: str) -> bool:
        try:
            word_lower = word.lower()
            synsets = wn.synsets(word_lower, pos=wn.VERB)
            if synsets:
                return True
            
            for synset in wn.synsets(word_lower):
                if 'v' in synset.pos():
                    return True
            
            return False
        except Exception:
            return False
    
    def _check_verb_noun_order(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if len(tags) < 2:
                return None
            
            first_tag = tags[0][1]
            second_tag = tags[1][1]
            
            if self._is_verb(first_tag) and (self._is_noun(second_tag) or self._is_proper_noun(second_tag)):
                return None
            
        except Exception as e:
            logger.debug(f"Error in scanner: {e}")
        
        return None
    
    def _check_gerund_ending(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if not tags:
                return None
            
            if tags[0][1] == "VBG":
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses gerund (-ing) form - use present tense verb (e.g., "Places Order" not "Placing Order")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception as e:
            logger.debug(f"Error in scanner: {e}")
        
        return None
    
    def _check_third_person_singular(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if not tags:
                return None
            
            if tags[0][1] == "VBZ":
                first_word = tags[0][0]
                base_form = self._convert_to_base_form(first_word)
                
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses third-person singular verb form ("{first_word}") - use base verb form instead (e.g., "{base_form} Multiple Tokens" not "{first_word} Multiple Tokens")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception as e:
            logger.debug(f"Error in scanner: {e}")
        
        return None
    
    def _convert_to_base_form(self, verb: str) -> str:
        verb_lower = verb.lower()
        
        irregular_map = {
            "goes": "go",
            "does": "do",
            "has": "have",
            "is": "be",
            "says": "say",
        }
        
        if verb_lower in irregular_map:
            base = irregular_map[verb_lower]
            if verb[0].isupper():
                return base.capitalize()
            return base
        
        if verb_lower.endswith("ies") and len(verb_lower) > 3:
            base = verb_lower[:-3] + "y"
        elif verb_lower.endswith("es") and len(verb_lower) > 2:
            base = verb_lower[:-2]
        elif verb_lower.endswith("s") and len(verb_lower) > 1:
            base = verb_lower[:-1]
        else:
            return verb
        
        if verb[0].isupper():
            return base.capitalize()
        return base
    
    def _check_noun_verb_noun_pattern(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if len(tags) < 3:
                return None
            
            words = [tag[0].lower() for tag in tags]
            first_tag = tags[0][1]
            second_tag = tags[1][1]
            third_tag = tags[2][1]
            
            if (self._is_noun(first_tag) or self._is_proper_noun(first_tag)) and \
               self._is_verb(second_tag) and \
               (self._is_noun(third_tag) or self._is_proper_noun(third_tag)):
                if VocabularyHelper.is_actor_or_role(words[0]):
                    location = node.map_location()
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'{node_type.capitalize()} name "{name}" uses noun-verb-noun pattern (actor prefix) - use verb-noun format without actor (e.g., "Places Order" not "Customer places order")',
                        location=location,
                        severity='error'
                    ).to_dict()
        
        except Exception as e:
            logger.debug(f"Error in scanner: {e}")
        
        return None
    
    def _check_noun_verb_pattern(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if len(tags) < 2:
                return None
            
            first_word = tags[0][0]
            first_word_clean = ''.join(c for c in first_word if c.isalnum())
            first_word_lower = first_word_clean.lower()
            first_tag = tags[0][1]
            second_tag = tags[1][1]
            
            if self._is_verb(first_tag):
                return None
            
            if self._can_be_verb(first_word_lower):
                return None
            
            common_verb_abbreviations = {
                'init': True,
                'load': True,
                'save': True,
                'run': True,
                'get': True,
                'set': True,
                'add': True,
                'del': True,
                'rm': True,
                'mv': True,
                'cp': True,
                'mk': True,
                'rmv': True,
                'upd': True,
                'gen': True,
                'inv': True,
                'exec': True,
                'proc': True,
            }
            if first_word_lower in common_verb_abbreviations:
                return None
            
            adverbs = {
                'proactively', 'automatically', 'manually', 'immediately', 'quickly', 
                'slowly', 'carefully', 'properly', 'correctly', 'incorrectly',
                'efficiently', 'effectively', 'accurately', 'precisely', 'thoroughly',
                'completely', 'partially', 'fully', 'entirely', 'directly', 'indirectly',
                'explicitly', 'implicitly', 'actively', 'passively', 'dynamically',
                'statically', 'sequentially', 'concurrently', 'synchronously', 'asynchronously',
                'conditionally', 'unconditionally', 'selectively', 'globally', 'locally',
                'temporarily', 'permanently', 'securely', 'safely', 'reliably',
                'consistently', 'inconsistently', 'systematically', 'randomly', 'intelligently',
                'intuitively', 'transparently', 'opaque', 'verbosely', 'concisely',
                'gracefully', 'elegantly', 'robustly', 'resiliently', 'adaptively'
            }
            if first_word_lower in adverbs and self._is_verb(second_tag):
                return None
            
            if (self._is_noun(first_tag) or self._is_proper_noun(first_tag)) and self._is_verb(second_tag):
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses noun-verb pattern - use verb-noun format (e.g., "Places Order" not "Order places")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception:
            return None
        
        return None
    
    def _check_actor_prefix(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        name_lower = name.lower().strip()
        words = name_lower.split()
        
        if not words:
            return None
        
        first_word = words[0]
        
        tokens, tags = self._get_tokens_and_tags(name)
        if tags:
            first_tag = tags[0][1]
            if self._is_verb(first_tag):
                return None
        
        if self._can_be_verb(first_word):
            return None
        
        common_verb_abbreviations = {
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
            'exit', 'advance', 'show', 'auto-run', 'auto-confirm', 're-execute',
            'view', 'request', 'add', 'monitor', 'surface', 'report', 'gather',
            'access', 'update', 'filter', 'get'
        }
        if first_word in common_verb_abbreviations:
            return None
        
        if VocabularyHelper.is_actor_or_role(first_word):
            location = node.map_location()
            return Violation(
                rule=rule_obj,
                violation_message=f'{node_type.capitalize()} name "{name}" contains actor prefix (e.g., "Customer") - use verb-noun format without actor',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _check_noun_only(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        try:
            tokens, tags = self._get_tokens_and_tags(name)
            
            if not tags:
                return None
            
            has_verb = any(self._is_verb(tag[1]) for tag in tags)
            
            if not has_verb and tokens:
                first_token = tokens[0]
                if '-' in first_token:
                    parts = first_token.split('-')
                    for part in parts:
                        part_clean = ''.join(c for c in part if c.isalnum())
                        part_lower = part_clean.lower()
                        if self._can_be_verb(part_lower) or part_lower in ['run', 'confirm', 'execute', 'auto', 're']:
                            has_verb = True
                            break
                    if not has_verb:
                        full_word = ''.join(parts).lower()
                        if self._can_be_verb(full_word):
                            has_verb = True
            
            if not has_verb and len(tokens) > 1:
                adverbs = {
                    'proactively', 'automatically', 'manually', 'immediately', 'quickly', 
                    'slowly', 'carefully', 'properly', 'correctly', 'incorrectly',
                    'efficiently', 'effectively', 'accurately', 'precisely', 'thoroughly',
                    'completely', 'partially', 'fully', 'entirely', 'directly', 'indirectly',
                    'explicitly', 'implicitly', 'actively', 'passively', 'dynamically',
                    'statically', 'sequentially', 'concurrently', 'synchronously', 'asynchronously',
                    'conditionally', 'unconditionally', 'selectively', 'globally', 'locally',
                    'temporarily', 'permanently', 'securely', 'safely', 'reliably',
                    'consistently', 'inconsistently', 'systematically', 'randomly', 'intelligently',
                    'intuitively', 'transparently', 'opaque', 'verbosely', 'concisely',
                    'gracefully', 'elegantly', 'robustly', 'resiliently', 'adaptively'
                }
                first_word_lower = tokens[0].lower()
                if first_word_lower in adverbs:
                    second_word_clean = ''.join(c for c in tokens[1] if c.isalnum())
                    second_word_lower = second_word_clean.lower()
                    if self._can_be_verb(second_word_lower):
                        has_verb = True
                    elif second_word_lower in ['validate', 'check', 'verify', 'run', 'execute', 
                                                'process', 'generate', 'create', 'build', 'render',
                                                'load', 'save', 'store', 'update', 'delete',
                                                'track', 'monitor', 'report', 'display', 'show']:
                        has_verb = True
            
            if not has_verb and tokens:
                first_word_clean = ''.join(c for c in tokens[0] if c.isalnum())
                first_word_lower = first_word_clean.lower()
                if self._can_be_verb(first_word_lower):
                    has_verb = True
                
                if not has_verb:
                    common_verb_abbreviations = {
                        'init': True,
                        'load': True,
                        'save': True,
                        'run': True,
                        'get': True,
                        'set': True,
                        'add': True,
                        'del': True,
                        'rm': True,
                        'mv': True,
                        'cp': True,
                        'mk': True,
                        'rmv': True,
                        'upd': True,
                        'del': True,
                        'gen': True,
                        'inv': True,
                        'exec': True,
                        'proc': True,
                    }
                    if first_word_lower in common_verb_abbreviations:
                        has_verb = True
            
            if not has_verb and tokens:
                first_word_clean = ''.join(c for c in tokens[0] if c.isalnum())
                first_word_lower = first_word_clean.lower()
                
                common_action_verbs = {
                    'load', 'save', 'run', 'get', 'set', 'add', 'remove', 'delete',
                    'move', 'copy', 'make', 'create', 'update', 'generate', 'invoke',
                    'execute', 'process', 'init', 'initialize', 'build', 'render',
                    'validate', 'check', 'verify', 'test', 'deploy', 'install',
                    'configure', 'setup', 'start', 'stop', 'restart', 'close',
                    'open', 'read', 'write', 'edit', 'modify', 'change', 'replace',
                    'insert', 'append', 'prepend', 'merge', 'split', 'join', 'combine',
                    'separate', 'filter', 'sort', 'search', 'find', 'locate', 'discover',
                    'detect', 'identify', 'recognize', 'parse', 'analyze', 'evaluate',
                    'assess', 'measure', 'calculate', 'compute', 'transform', 'convert',
                    'translate', 'map', 'route', 'forward', 'redirect', 'send', 'receive',
                    'transmit', 'deliver', 'dispatch', 'submit', 'publish', 'broadcast',
                    'notify', 'alert', 'warn', 'inform', 'report', 'log', 'record',
                    'track', 'monitor', 'observe', 'watch', 'listen', 'collect', 'gather',
                    'accumulate', 'aggregate', 'summarize', 'extract', 'retrieve', 'fetch',
                    'pull', 'push', 'sync', 'synchronize', 'refresh', 'reload', 'reload',
                    'restore', 'recover', 'backup', 'restore', 'export', 'import',
                    'upload', 'download', 'transfer', 'migrate', 'upgrade', 'downgrade',
                    'install', 'uninstall', 'deploy', 'rollback', 'revert', 'undo', 'redo',
                    'cancel', 'abort', 'terminate', 'kill', 'destroy', 'remove', 'delete',
                    'clear', 'reset', 'initialize', 'init', 'setup', 'configure', 'prepare',
                    'arrange', 'organize', 'structure', 'format', 'style', 'design', 'plan',
                    'schedule', 'queue', 'prioritize', 'order', 'rank', 'sort', 'group',
                    'categorize', 'classify', 'tag', 'label', 'mark', 'flag', 'assign',
                    'allocate', 'distribute', 'share', 'grant', 'revoke', 'permit', 'deny',
                    'allow', 'block', 'restrict', 'limit', 'constrain', 'enforce', 'apply',
                    'implement', 'execute', 'perform', 'carry', 'out', 'complete', 'finish',
                    'end', 'conclude', 'finalize', 'close', 'terminate', 'abandon', 'drop',
                    'discard', 'ignore', 'skip', 'omit', 'exclude', 'include', 'add', 'append',
                    'insert', 'prepend', 'attach', 'link', 'connect', 'join', 'merge', 'combine',
                    'unite', 'unify', 'integrate', 'incorporate', 'embed', 'nest', 'wrap',
                    'unwrap', 'extract', 'isolate', 'separate', 'divide', 'split', 'partition',
                    'segment', 'slice', 'chunk', 'batch', 'group', 'cluster', 'aggregate',
                    'collect', 'gather', 'accumulate', 'assemble', 'compile', 'build', 'construct',
                    'create', 'generate', 'produce', 'manufacture', 'fabricate', 'make', 'form',
                    'shape', 'mold', 'sculpt', 'carve', 'cut', 'trim', 'prune', 'trim', 'shave',
                    'polish', 'refine', 'improve', 'enhance', 'optimize', 'tune', 'adjust',
                    'modify', 'alter', 'change', 'transform', 'convert', 'translate', 'transpose',
                    'rotate', 'flip', 'reverse', 'invert', 'mirror', 'reflect', 'project',
                    'cast', 'throw', 'send', 'emit', 'broadcast', 'transmit', 'deliver', 'dispatch',
                    'forward', 'route', 'redirect', 'reroute', 'reroute', 'reroute', 'reroute',
                }
                if first_word_lower in common_action_verbs:
                    has_verb = True
            
            if not has_verb:
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" appears to be noun-only - use verb-noun format (e.g., "Places Order" not "Order Management")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        except Exception:
            pass
        
        return None

