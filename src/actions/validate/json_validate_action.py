
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.actions.validate.validate_action import ValidateRulesAction

class JSONValidateAction(JSONAdapter):
    
    def __init__(self, action: ValidateRulesAction, is_current: bool = False, is_completed: bool = False):
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
    def rules(self):
        return self.action.rules
    
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
        
        if self.action.rules:
            rules_list = getattr(self.action.rules, 'rules', None) or getattr(self.action.rules, '_rules', None) or []
            if not rules_list and hasattr(self.action.rules, '__iter__'):
                rules_list = list(self.action.rules)
            result['rules'] = {
                'count': len(rules_list),
                'rules': [
                    {
                        'rule_name': getattr(rule, 'rule_name', None) or getattr(rule, 'name', None) or 'unknown',
                        'rule_file': getattr(rule, 'rule_file', None) or '',
                        'enabled': getattr(rule, 'enabled', True)
                    }
                    for rule in rules_list
                ]
            }
        
        return result
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
