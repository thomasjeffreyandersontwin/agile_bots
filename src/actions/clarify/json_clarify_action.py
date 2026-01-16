
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.actions.clarify.clarify_action import ClarifyContextAction

class JSONClarifyAction(JSONAdapter):
    
    def __init__(self, action: ClarifyContextAction, is_current: bool = False, is_completed: bool = False):
        self.action = action
        self.is_current = is_current
        self.is_completed = is_completed
    
    @property
    def action_name(self):
        return self.action.action_name
    
    @property
    def description(self):
        return self.action.description
    
    @property
    def order(self):
        return self.action.order
    
    @property
    def next_action(self):
        return self.action.next_action
    
    @property
    def workflow(self):
        return self.action.workflow
    
    @property
    def auto_confirm(self):
        return self.action.auto_confirm
    
    @property
    def skip_confirm(self):
        return self.action.skip_confirm
    
    @property
    def behavior(self):
        return self.action.behavior
    
    @property
    def required_context(self):
        return self.action.required_context
    
    @property
    def key_questions(self):
        return self.action.key_questions
    
    @property
    def evidence(self):
        return self.action.evidence
    
    def to_dict(self) -> dict:
        result = {
            'action_name': self.action.action_name,
            'description': self.action.description,
            'order': self.action.order,
            'next_action': self.action.next_action,
            'workflow': self.action.workflow,
            'auto_confirm': self.action.auto_confirm,
            'skip_confirm': self.action.skip_confirm,
            'behavior': self.action.behavior.name if self.action.behavior else None,
        }
        
        if self.action.required_context:
            key_questions_data = None
            if self.action.key_questions and hasattr(self.action.key_questions, 'questions'):
                key_questions_data = self.action.key_questions.questions
            
            evidence_data = None
            if self.action.evidence and hasattr(self.action.evidence, 'evidence_list'):
                evidence_data = self.action.evidence.evidence_list
            
            result['required_context'] = {
                'key_questions': key_questions_data,
                'evidence': evidence_data
            }
        
        return result
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
