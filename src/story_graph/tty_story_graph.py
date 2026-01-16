
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.story_graph.story_graph import StoryGraph

class TTYStoryGraph(TTYAdapter):
    
    def __init__(self, story_graph: StoryGraph):
        self.story_graph = story_graph
    
    @property
    def path(self):
        return self.story_graph.path
    
    @property
    def has_epics(self):
        return self.story_graph.has_epics
    
    @property
    def has_increments(self):
        return self.story_graph.has_increments
    
    @property
    def has_domain_concepts(self):
        return self.story_graph.has_domain_concepts
    
    @property
    def epic_count(self):
        return self.story_graph.epic_count
    
    @property
    def content(self):
        return self.story_graph.content
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.add_bold("Story Graph"))
        lines.append(f"Path: {self.story_graph.path}")
        lines.append(f"Epics: {self.story_graph.epic_count}")
        
        flags = []
        if self.story_graph.has_increments:
            flags.append("increments")
        if self.story_graph.has_domain_concepts:
            flags.append("domain concepts")
        
        if flags:
            lines.append(f"Features: {', '.join(flags)}")
        
        lines.append("")
        
        content = self.story_graph.content
        if content and 'epics' in content:
            lines.append(self.add_color("Epics:", 'cyan'))
            for epic in content['epics']:
                epic_name = epic.get('name', 'Unknown')
                lines.append(f"  🎯  {epic_name}")
                
                for sub_epic in epic.get('sub_epics', []):
                    self._render_sub_epic(sub_epic, lines, indent_level=1)
        
        return '\n'.join(lines)
    
    def _render_sub_epic(self, sub_epic: dict, lines: list, indent_level: int):
        sub_epic_name = sub_epic.get('name', 'Unknown')
        indent = "  " * (indent_level + 1)
        lines.append(f"{indent}⚙️  {sub_epic_name}")
        
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                story_name = story.get('name', 'Unknown')
                story_indent = "  " * (indent_level + 2)
                lines.append(f"{story_indent}📝  {story_name}")
        
        for story in sub_epic.get('stories', []):
            story_name = story.get('name', 'Unknown')
            story_indent = "  " * (indent_level + 2)
            lines.append(f"{story_indent}📝  {story_name}")
        
        for nested_sub_epic in sub_epic.get('sub_epics', []):
            self._render_sub_epic(nested_sub_epic, lines, indent_level + 1)
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from agile_bots.src.utils import parse_command_text
        return parse_command_text(text)
