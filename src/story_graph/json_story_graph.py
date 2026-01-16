
import json
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.story_graph.story_graph import StoryGraph

class JSONStoryGraph(JSONAdapter):
    
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
    
    def to_dict(self) -> dict:
        return {
            'path': str(self.story_graph.path),
            'has_epics': self.story_graph.has_epics,
            'has_increments': self.story_graph.has_increments,
            'has_domain_concepts': self.story_graph.has_domain_concepts,
            'epic_count': self.story_graph.epic_count,
            'content': self.story_graph.content
        }
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
