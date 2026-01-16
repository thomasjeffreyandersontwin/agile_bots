
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.navigation.navigation import NavigationResult

class JSONNavigation(JSONAdapter):
    
    def __init__(self, nav_result: NavigationResult):
        self.nav_result = nav_result
    
    @property
    def success(self):
        return self.nav_result.success
    
    @property
    def message(self):
        return self.nav_result.message
    
    @property
    def new_position(self):
        return self.nav_result.new_position
    
    def to_dict(self) -> dict:
        return {
            'success': self.nav_result.success,
            'message': self.nav_result.message,
            'new_position': self.nav_result.new_position
        }
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
