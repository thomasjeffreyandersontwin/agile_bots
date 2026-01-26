
import json
from cli.adapters import JSONAdapter
from story_graph.story_graph import StoryGraph

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
        # Load domain objects and serialize them directly
        from story_graph.nodes import StoryMap
        story_map = StoryMap(self.story_graph.content, bot=None)
        
        # Serialize domain objects to JSON by reading their properties
        content = {
            'epics': [self._serialize_epic(epic) for epic in story_map._epics]
        }
        
        # Add increments and other top-level fields from original content
        if 'increments' in self.story_graph.content:
            content['increments'] = self.story_graph.content['increments']
        
        return {
            'path': str(self.story_graph.path),
            'has_epics': self.story_graph.has_epics,
            'has_increments': self.story_graph.has_increments,
            'has_domain_concepts': self.story_graph.has_domain_concepts,
            'epic_count': self.story_graph.epic_count,
            'content': content
        }
    
    def _serialize_epic(self, epic) -> dict:
        """Serialize Epic object to dict by reading its properties."""
        return {
            'name': epic.name,
            'behavior_needed': epic.behavior_needed,
            'domain_concepts': epic.domain_concepts if hasattr(epic, 'domain_concepts') else [],
            'sub_epics': [self._serialize_sub_epic(child) for child in epic.children]
        }
    
    def _serialize_sub_epic(self, sub_epic) -> dict:
        """Serialize SubEpic object to dict by reading its properties."""
        from story_graph.nodes import SubEpic, Story, StoryGroup
        
        result = {
            'name': sub_epic.name,
            'behavior_needed': sub_epic.behavior_needed,
            'test_file': sub_epic.test_file if hasattr(sub_epic, 'test_file') else None,
            'test_class': sub_epic.test_class if hasattr(sub_epic, 'test_class') else None,
            'sub_epics': [],
            'story_groups': []
        }
        
        # Collect nested sub-epics and story groups
        current_story_group = None
        for child in sub_epic.children:
            if isinstance(child, SubEpic):
                result['sub_epics'].append(self._serialize_sub_epic(child))
            elif isinstance(child, StoryGroup):
                result['story_groups'].append(self._serialize_story_group(child))
            elif isinstance(child, Story):
                # Direct story child - add to unnamed story group
                if current_story_group is None:
                    current_story_group = {'name': None, 'stories': []}
                    result['story_groups'].append(current_story_group)
                current_story_group['stories'].append(self._serialize_story(child))
        
        return result
    
    def _serialize_story_group(self, story_group) -> dict:
        """Serialize StoryGroup object to dict."""
        return {
            'name': story_group.name if hasattr(story_group, 'name') else None,
            'stories': [self._serialize_story(story) for story in story_group.children]
        }
    
    def _serialize_story(self, story) -> dict:
        """Serialize Story object to dict by reading its properties."""
        return {
            'name': story.name,
            'behavior_needed': story.behavior_needed,
            'test_file': story.test_file if hasattr(story, 'test_file') else None,
            'test_class': story.test_class if hasattr(story, 'test_class') else None,
            'acceptance_criteria': [self._serialize_ac(ac) for ac in story.acceptance_criteria],
            'scenarios': [self._serialize_scenario(sc) for sc in story.scenarios]
        }
    
    def _serialize_ac(self, ac) -> dict:
        """Serialize AcceptanceCriteria object."""
        return {
            'name': ac.name,
            'text': ac.name,
            'sequential_order': ac.sequential_order
        }
    
    def _serialize_scenario(self, scenario) -> dict:
        """Serialize Scenario object to dict by reading its properties."""
        # Serialize background steps
        background_steps = []
        if hasattr(scenario, 'background'):
            for step in scenario.background:
                if isinstance(step, str):
                    background_steps.append(step)
                else:
                    background_steps.append(self._serialize_step(step))
        
        # Serialize main steps
        main_steps = []
        if hasattr(scenario, 'steps'):
            for step in scenario.steps:
                if isinstance(step, str):
                    main_steps.append(step)
                else:
                    main_steps.append(self._serialize_step(step))
        
        return {
            'name': scenario.name,
            'behavior_needed': scenario.behavior_needed,
            'test_method': scenario.test_method if hasattr(scenario, 'test_method') else None,
            'type': scenario.type if hasattr(scenario, 'type') else '',
            'sequential_order': scenario.sequential_order,
            'background': background_steps,
            'steps': main_steps,
            'examples': scenario.examples if hasattr(scenario, 'examples') else None
        }
    
    def _serialize_step(self, step) -> dict:
        """Serialize Step object to dict."""
        return {
            'text': step.text,
            'sequential_order': step.sequential_order
        }
    
    def deserialize(self, data: str) -> dict:
        return json.loads(data)
