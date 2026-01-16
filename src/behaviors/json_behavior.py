
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.cli.base_hierarchical_adapter import BaseBehaviorsAdapter, BaseBehaviorAdapter
from agile_bots.src.behaviors.behavior import Behavior
from agile_bots.src.behaviors.behaviors import Behaviors

class JSONBehaviors(BaseBehaviorsAdapter, JSONAdapter):
    
    def __init__(self, behaviors: Behaviors):
        BaseBehaviorsAdapter.__init__(self, behaviors, 'json')
        self.behaviors = behaviors
    
    def serialize(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_dict(self) -> dict:
        behaviors_list = []
        for behavior_adapter in self._behavior_adapters:
            if hasattr(behavior_adapter, 'to_dict'):
                behaviors_list.append(behavior_adapter.to_dict())
        return {
            'current': self.behaviors.current.name if self.behaviors.current else None,
            'names': self.behaviors.names,
            'all_behaviors': behaviors_list
        }
    

class JSONBehavior(BaseBehaviorAdapter, JSONAdapter):
    
    def __init__(self, behavior: Behavior, is_current: bool = False):
        self.behavior = behavior
        self.is_current = is_current
        BaseBehaviorAdapter.__init__(self, behavior, 'json', is_current)
    
    def format_behavior_name(self) -> str:
        return ""
    
    def serialize(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_dict(self) -> dict:
        result = {
            'name': self.behavior.name,
            'bot_name': self.behavior.bot_name,
            'description': self.behavior.description,
            'goal': self.behavior.goal,
            'action_names': self.behavior.action_names,
            'is_completed': self.behavior.is_completed,
            'order': self.behavior.order,
            'is_current': self.is_current
        }
        
        if self.is_current and self._actions_adapter and hasattr(self._actions_adapter, 'to_dict'):
            result['actions'] = self._actions_adapter.to_dict()
        elif self.behavior.actions:
            result['actions'] = {
                'all_actions': [
                    {
                        'action_name': action.action_name,
                        'description': action.description,
                        'order': action.order,
                        'is_current': False,
                        'is_completed': self.behavior.actions.is_action_completed(action.action_name)
                    }
                    for action in self.behavior.actions
                ]
            }
        
        return result
    
    def deserialize(self, data: str) -> Behavior:
        behavior_data = json.loads(data)
        # This is a limitation of the domain model
        raise NotImplementedError("Behavior deserialization requires bot_paths and config files")
