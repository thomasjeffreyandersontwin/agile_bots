
import json
from pathlib import Path
from cli.adapters import JSONAdapter
from scope.scope import Scope

class JSONScope(JSONAdapter):
    
    def __init__(self, scope: Scope):
        self.scope = scope
    
    @property
    def type(self):
        return self.scope.type
    
    @property
    def value(self):
        return self.scope.value
    
    @property
    def exclude(self):
        return self.scope.exclude
    
    @property
    def skiprule(self):
        return self.scope.skiprule
    
    @property
    def story_graph_filter(self):
        return self.scope.story_graph_filter
    
    @property
    def file_filter(self):
        return self.scope.file_filter
    
    def to_dict(self) -> dict:
        result = {
            'type': self.scope.type.value,
            'filter': ', '.join(self.scope.value) if self.scope.value else '',
            'content': None,
            'graphLinks': []
        }
        
        if self.scope.type.value in ('story', 'showAll'):
            story_graph = self.scope._get_story_graph_results()
            if story_graph:
                from story_graph.json_story_graph import JSONStoryGraph
                graph_adapter = JSONStoryGraph(story_graph)
                content = graph_adapter.to_dict().get('content', [])
                
                if content and 'epics' in content:
                    # Always enrich scenarios with test links
                    enrich_scenarios = True
                    self._enrich_with_links(content['epics'], story_graph, enrich_scenarios)
                    result['content'] = content
                else:
                    result['content'] = {'epics': []}
                
                if self.scope.bot_paths:
                    from pathlib import Path
                    docs_path = self.scope.bot_paths.documentation_path
                    docs_stories = self.scope.workspace_directory / docs_path
                    story_map_file = docs_stories / 'story-map' / 'story-map.md'
                    if story_map_file.exists():
                        result['graphLinks'].append({
                            'text': 'map',
                            'url': str(story_map_file)
                        })
        elif self.scope.type.value == 'files':
            files = self.scope._get_file_results()
            result['content'] = [{'path': str(f)} for f in files]
        
        return result
    
    def _enrich_with_links(self, epics: list, story_graph, enrich_scenarios: bool = True):
        if not self.scope.workspace_directory or not self.scope.bot_paths:
            return
        
        test_dir = self.scope.workspace_directory / self.scope.bot_paths.test_path
        docs_path = self.scope.bot_paths.documentation_path
        docs_stories_map = self.scope.workspace_directory / docs_path / 'map'
        
        for epic in epics:
            epic_folder = docs_stories_map / f"🎯 {epic['name']}"
            if epic_folder.exists() and epic_folder.is_dir():
                if 'links' not in epic:
                    epic['links'] = []
                epic['links'].append({
                    'text': 'docs',
                    'url': str(epic_folder),
                    'icon': 'document'
                })
            
            if 'sub_epics' in epic:
                for sub_epic in epic['sub_epics']:
                    self._enrich_sub_epic_with_links(sub_epic, test_dir, docs_stories_map, epic['name'], enrich_scenarios=enrich_scenarios)
    
    def _enrich_sub_epic_with_links(self, sub_epic: dict, test_dir: Path, docs_stories_map: Path, epic_name: str, parent_path: str = None, enrich_scenarios: bool = True):
        if parent_path:
            sub_epic_doc_folder = Path(parent_path) / f"⚙️ {sub_epic['name']}"
        else:
            sub_epic_doc_folder = docs_stories_map / f"🎯 {epic_name}" / f"⚙️ {sub_epic['name']}"
        
        if 'links' not in sub_epic:
            sub_epic['links'] = []
        
        if 'test_file' in sub_epic and sub_epic['test_file']:
            test_file_path = test_dir / sub_epic['test_file']
            if test_file_path.exists():
                sub_epic['links'].append({
                    'text': 'test',
                    'url': str(test_file_path),
                    'icon': 'test_tube'
                })
        
        if sub_epic_doc_folder.exists() and sub_epic_doc_folder.is_dir():
            sub_epic['links'].append({
                'text': 'docs',
                'url': str(sub_epic_doc_folder),
                'icon': 'document'
            })
        
        if 'sub_epics' in sub_epic:
            for nested_sub_epic in sub_epic['sub_epics']:
                self._enrich_sub_epic_with_links(nested_sub_epic, test_dir, docs_stories_map, epic_name, str(sub_epic_doc_folder), enrich_scenarios=enrich_scenarios)
        
        if 'story_groups' in sub_epic:
            for story_group in sub_epic['story_groups']:
                if 'stories' in story_group:
                    for story in story_group['stories']:
                        self._enrich_story_with_links(story, test_dir, sub_epic_doc_folder, sub_epic.get('test_file'), enrich_scenarios=enrich_scenarios)
    
    def _enrich_story_with_links(self, story: dict, test_dir: Path, parent_doc_folder: Path, parent_test_file: str, enrich_scenarios: bool = True):
        if 'links' not in story:
            story['links'] = []
        
        story_doc_file = parent_doc_folder / f"📄 {story['name']}.md"
        if story_doc_file.exists():
            story['links'].append({
                'text': 'story',
                'url': str(story_doc_file),
                'icon': 'document'
            })
        
        test_file = story.get('test_file') or parent_test_file
        test_class = story.get('test_class')
        
        # Only add test icon if we have both test_file and test_class with a valid file AND the class exists
        if test_file and test_class:
            test_file_path = test_dir / test_file
            if test_file_path.exists():
                from utils import find_test_class_line
                line_number = find_test_class_line(test_file_path, test_class)
                
                if line_number:
                    test_url = f"{test_file_path}#L{line_number}"
                    story['links'].append({
                        'text': 'test',
                        'url': test_url,
                        'icon': 'test_tube'
                    })
        
        # Only enrich scenarios if requested (skip for 'scope showall' to avoid expensive AST parsing)
        if enrich_scenarios and 'scenarios' in story:
            for scenario in story['scenarios']:
                self._enrich_scenario_with_links(scenario, test_dir, test_file, test_class)
    
    def _enrich_scenario_with_links(self, scenario: dict, test_dir: Path, story_test_file: str, story_test_class: str):
        test_method = scenario.get('test_method')
        
        if story_test_file and test_method:
            test_file_path = test_dir / story_test_file
            if test_file_path.exists():
                from utils import find_test_method_line
                line_number = find_test_method_line(test_file_path, test_method)
                
                if line_number:
                    test_url = f"{test_file_path}#L{line_number}"
                    scenario['test_file'] = test_url
                else:
                    pass
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
