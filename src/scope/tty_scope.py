
from pathlib import Path
from cli.adapters import TTYAdapter
from scope.scope import Scope

class TTYScope(TTYAdapter):
    
    def __init__(self, scope: Scope):
        self.scope = scope
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.add_bold("🎯 Scope"))
        
        if self.scope.type.value == 'all':
            filter_display = "all (entire project)"
        else:
            filter_display = ', '.join(self.scope.value) if isinstance(self.scope.value, list) else str(self.scope.value) if self.scope.value else "all"
        
        lines.append(f"🎯 {self.add_bold('Current Scope:')} {filter_display}")
        lines.append("")
        
        results = self.scope.results
        
        if results is not None:
            from story_graph.story_graph import StoryGraph
            
            if isinstance(results, StoryGraph):
                from cli.adapter_factory import AdapterFactory
                storyGrapgAdapter = AdapterFactory.create(results, 'tty')
                lines.append(storyGrapgAdapter.serialize())
            elif isinstance(results, list):
                if results:
                    for file_path in sorted(results):
                        try:
                            rel_path = file_path.relative_to(self.scope.workspace_directory)
                            lines.append(f"  - {rel_path}")
                        except ValueError:
                            lines.append(f"  - {file_path}")
                else:
                    lines.append("  (no files found)")
        else:
            lines.append("  (no scope set)")
        
        lines.append("To change scope (pick ONE - setting a new scope replaces the previous):")
        lines.append("scope all                            # Clear scope, work on entire project")
        lines.append('scope "Story Name"                   # Filter by story (replaces any file scope)')
        lines.append('scope "file:C:/path/to/**/*.py"      # Filter by files (replaces any story scope)')
        lines.append(self.subsection_separator())
        
        return '\n'.join(lines)
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from utils import parse_command_text
        return parse_command_text(text)
