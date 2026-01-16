
from pathlib import Path
from agile_bots.src.cli.adapters import MarkdownAdapter
from agile_bots.src.scope.scope import Scope

class MarkdownScope(MarkdownAdapter):
    
    def __init__(self, scope: Scope, workspace_directory: Path = None):
        self.scope = scope
        self.workspace_directory = workspace_directory or Path.cwd()
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.format_header(2, "🎯 Scope"))
        lines.append("")
        
        if self.scope.type.value == 'all':
            filter_display = "all (entire project)"
        else:
            filter_display = ', '.join(self.scope.value) if isinstance(self.scope.value, list) else str(self.scope.value) if self.scope.value else "all"
        
        lines.append(f"**🎯 Current Scope:** {filter_display}")
        lines.append("")
        
        results = self.scope.results
        
        if results is not None:
            from agile_bots.src.story_graph.story_graph import StoryGraph
            
            if isinstance(results, StoryGraph):
                from agile_bots.src.cli.adapter_factory import AdapterFactory
                story_graph_adapter = AdapterFactory.create(results, 'markdown')
                lines.append(story_graph_adapter.serialize())
            elif isinstance(results, list):
                if results:
                    for file_path in sorted(results):
                        try:
                            rel_path = file_path.relative_to(self.scope.workspace_directory)
                            lines.append(self.format_list_item(str(rel_path)))
                        except ValueError:
                            lines.append(self.format_list_item(str(file_path)))
                else:
                    lines.append("(no files found)")
        else:
            lines.append("(no scope set)")
        
        lines.append("")
        lines.append("To change scope (pick ONE - setting a new scope replaces the previous):")
        lines.append(self.format_list_item("`scope all` - Clear scope, work on entire project"))
        lines.append(self.format_list_item("`scope \"Story Name\"` - Filter by story (replaces any file scope)"))
        lines.append(self.format_list_item("`scope \"file:C:/path/to/**/*.py\"` - Filter by files (replaces any story scope)"))
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return ''.join(lines)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
