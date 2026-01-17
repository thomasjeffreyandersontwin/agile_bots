
from typing import List, Set, Optional
import nltk
from nltk.corpus import wordnet as wn
from nltk import pos_tag, word_tokenize

import socket
_original_timeout = socket.getdefaulttimeout()
socket.setdefaulttimeout(2)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    try:
        nltk.download('wordnet', quiet=True)
    except:
        pass

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    try:
        nltk.download('averaged_perceptron_tagger_eng', quiet=True)
    except:
        pass

socket.setdefaulttimeout(_original_timeout)

class VocabularyHelper:
    
    AGENT_SUFFIXES = ['er', 'or', 'ar', 'ant', 'ent']
    
    GERUND_SUFFIX = 'ing'
    
    @staticmethod
    def is_verb(word: str) -> bool:
        try:
            word_lower = word.lower()
            synsets = wn.synsets(word_lower, pos=wn.VERB)
            return len(synsets) > 0
        except Exception:
            return False
    
    @staticmethod
    def is_noun(word: str) -> bool:
        try:
            word_lower = word.lower()
            synsets = wn.synsets(word_lower, pos=wn.NOUN)
            return len(synsets) > 0
        except Exception:
            return False
    
    @staticmethod
    def is_agent_noun(word: str) -> tuple[bool, Optional[str], Optional[str]]:
        word_lower = word.lower()
        
        for suffix in VocabularyHelper.AGENT_SUFFIXES:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
                base = word_lower[:-len(suffix)]
                
                if VocabularyHelper.is_verb(base):
                    return (True, base, suffix)
                
                if suffix == 'er' or suffix == 'or':
                    base_with_e = base + 'e'
                    if VocabularyHelper.is_verb(base_with_e):
                        return (True, base_with_e, suffix)
        
        return (False, None, None)
    
    @staticmethod
    def is_gerund(word: str) -> tuple[bool, Optional[str]]:
        word_lower = word.lower()
        
        if not word_lower.endswith(VocabularyHelper.GERUND_SUFFIX):
            return (False, None)
        
        if len(word_lower) <= len(VocabularyHelper.GERUND_SUFFIX) + 2:
            return (False, None)
        
        base = word_lower[:-len(VocabularyHelper.GERUND_SUFFIX)]
        
        if VocabularyHelper.is_verb(base):
            return (True, base)
        
        base_with_e = base + 'e'
        if VocabularyHelper.is_verb(base_with_e):
            return (True, base_with_e)
        
        if len(base) > 1 and base[-1] == base[-2]:
            base_single = base[:-1]
            if VocabularyHelper.is_verb(base_single):
                return (True, base_single)
        
        return (False, None)
    
    @staticmethod
    def get_pos_tags(text: str) -> List[tuple[str, str]]:
        try:
            tokens = word_tokenize(text)
            tokens = [t for t in tokens if t.isalnum() or any(c.isalnum() for c in t)]
            return pos_tag(tokens)
        except Exception:
            return []
    
    @staticmethod
    def is_verb_tag(tag: str) -> bool:
        verb_tags = ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']
        return tag in verb_tags
    
    @staticmethod
    def is_noun_tag(tag: str) -> bool:
        noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
        return tag in noun_tags
    
    @staticmethod
    def is_proper_noun_tag(tag: str) -> bool:
        proper_noun_tags = ['NNP', 'NNPS']
        return tag in proper_noun_tags
    
    @staticmethod
    def is_actor_or_role(word: str) -> bool:
        try:
            word_lower = word.lower()
            
            synsets = wn.synsets(word_lower)
            
            if not synsets:
                return False
            
            for synset in synsets:
                hypernyms = set()
                for path in synset.hypernym_paths():
                    hypernyms.update(path)
                
                for hypernym in hypernyms:
                    name = hypernym.name().split('.')[0]
                    if name in ['person', 'user', 'system', 'agent', 'entity', 'causal_agent']:
                        return True
            
            return False
        except Exception:
            return False
        

