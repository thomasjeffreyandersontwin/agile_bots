
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.navigation.navigation import NavigationResult

class TTYNavigation(TTYAdapter):
    
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
    
    def serialize(self) -> str:
        lines = []
        
        if self.nav_result.success:
            lines.append(self.add_color("✓ Navigation successful", 'green'))
        else:
            lines.append(self.add_color("✗ Navigation failed", 'red'))
        
        if self.nav_result.message:
            lines.append(self.nav_result.message)
        
        if self.nav_result.new_position:
            lines.append(f"Position: {self.nav_result.new_position}")
        
        return '\n'.join(lines)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
