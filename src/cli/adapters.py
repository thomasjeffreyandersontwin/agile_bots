
from abc import ABC, abstractmethod
from typing import Dict, Any

class ChannelAdapter(ABC):
    
    @abstractmethod
    def serialize(self) -> str:
        pass

class TextAdapter(ChannelAdapter):
    
    @abstractmethod
    def parse_command_text(self, text: str) -> tuple[str, str]:
        pass

class TTYAdapter(TextAdapter):
    
    def add_color(self, text: str, color: str) -> str:
        colors = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'blue': '\033[94m',
            'reset': '\033[0m'
        }
        return f"{colors.get(color, '')}{text}{colors['reset']}"
    
    def add_bold(self, text: str) -> str:
        return f"\033[1m{text}\033[0m"
    
    def format_indentation(self, level: int) -> str:
        return "  " * level
    
    def section_separator(self) -> str:
        return "━" * 100
    
    def subsection_separator(self) -> str:
        return "─" * 60
    
    @abstractmethod
    def serialize(self) -> str:
        pass
    
    @abstractmethod
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)

class JSONAdapter(ChannelAdapter):
    
    @abstractmethod
    def to_dict(self) -> Dict:
        pass
    
    def serialize(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)

class MarkdownAdapter(TextAdapter):
    
    def format_header(self, level: int, text: str) -> str:
        return f"{'#' * level} {text}\n"
    
    def format_list_item(self, text: str, indent: int = 0) -> str:
        return f"{'  ' * indent}- {text}\n"
    
    def format_code_block(self, content: str, language: str = "") -> str:
        return f"```{language}\n{content}\n```\n"
    
    @abstractmethod
    def serialize(self) -> str:
        pass
    
    @abstractmethod
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)

class JSONProgressAdapter(JSONAdapter):
    
    def include_progress_fields(self, is_completed: bool, is_current: bool) -> Dict:
        return {
            'is_completed': is_completed,
            'is_current': is_current,
            'completion_marker': '[X]' if is_completed else '[ ]'
        }

class TTYProgressAdapter(TTYAdapter):
    
    def render_marker(self, is_completed: bool, is_current: bool) -> str:
        if is_completed:
            return self.add_color('[X]', 'green')
        elif is_current:
            return self.add_color('[>]', 'yellow')
        else:
            return '[ ]'

class MarkdownProgressAdapter(MarkdownAdapter):
    
    def render_progress_marker(self, is_completed: bool, is_current: bool) -> str:
        if is_completed:
            return '[X]'
        elif is_current:
            return '[>]'
        else:
            return '[ ]'

class GenericJSONAdapter(JSONAdapter):
    
    def __init__(self, data: Any):
        self.data = data
    
    def to_dict(self) -> Dict:
        if isinstance(self.data, dict):
            return self.data
        return {'data': self.data}

class GenericTTYAdapter(TTYAdapter):
    
    def __init__(self, data: Any):
        self.data = data
    
    def serialize(self) -> str:
        if isinstance(self.data, dict):
            if 'scope' in self.data and isinstance(self.data['scope'], dict):
                scope_data = self.data['scope']
                scope_type = scope_data.get('type', 'all')
                target = scope_data.get('target', [])
                
                if target:
                    target_str = ', '.join(str(t) for t in target)
                    return f"\x1b[1mScope:\x1b[0m {scope_type}: {target_str}"
                else:
                    return f"\x1b[1mScope:\x1b[0m {scope_type}"
            elif 'status' in self.data and 'behavior' in self.data and 'action' in self.data:
                lines = []
                lines.append(f"\x1b[1mStatus:\x1b[0m {self.data['status']}")
                lines.append(f"\x1b[1mBehavior:\x1b[0m {self.data['behavior']}")
                lines.append(f"\x1b[1mAction:\x1b[0m {self.data['action']}")
                if 'message' in self.data:
                    lines.append(f"\x1b[1mMessage:\x1b[0m {self.data['message']}")
                if 'result' in self.data:
                    lines.append(f"\x1b[1mResult:\x1b[0m {self.data['result']}")
                return '\n'.join(lines)
            else:
                lines = []
                for key, value in self.data.items():
                    lines.append(f"\x1b[1m{key}:\x1b[0m {value}")
                return '\n'.join(lines)
        import json
        return json.dumps(self.data, indent=2)
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)

class GenericMarkdownAdapter(MarkdownAdapter):
    
    def __init__(self, data: Any):
        self.data = data
    
    def serialize(self) -> str:
        if isinstance(self.data, dict) and 'scope' in self.data and isinstance(self.data['scope'], dict):
            scope_data = self.data['scope']
            scope_type = scope_data.get('type', 'all')
            target = scope_data.get('target', [])
            
            if target:
                target_str = ', '.join(str(t) for t in target)
                return f"**Scope:** {scope_type}: {target_str}"
            else:
                return f"**Scope:** {scope_type}"
        import json
        return f"```json\n{json.dumps(self.data, indent=2)}\n```"
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)