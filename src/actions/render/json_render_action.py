
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.actions.render.render_action import RenderOutputAction

class JSONRenderAction(JSONAdapter):
    
    def __init__(self, action: RenderOutputAction, is_current: bool = False, is_completed: bool = False):
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
    def render_specs(self):
        return self.action.render_specs
    
    @property
    def templates(self):
        return self.action.templates
    
    @property
    def synchronizers(self):
        return self.action.synchronizers
    
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
        
        if self.action.render_specs:
            result['render_specs'] = {
                'count': len(self.action.render_specs),
                'specs': [
                    {
                        'name': getattr(spec, 'name', 'unknown'),
                        'renderer_command': getattr(spec, 'renderer_command', None) or getattr(spec, 'renderer', None) or '',
                        'template_file': str(getattr(spec, 'template_file', None)) if getattr(spec, 'template_file', None) else None,
                        'output_file': str(getattr(spec, 'output_file', None)) if getattr(spec, 'output_file', None) else None
                    }
                    for spec in self.action.render_specs
                ]
            }
            
            result['templates'] = [str(t) for t in self.action.templates] if self.action.templates else []
            result['synchronizers'] = [str(s) for s in self.action.synchronizers] if self.action.synchronizers else []
        
        return result
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
