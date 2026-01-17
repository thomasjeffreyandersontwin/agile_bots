"""
StoryIODiagram Domain Component

Main diagram class that orchestrates the story map with rendering and synchronization capabilities.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import field
from .story_io_component import StoryIOComponent
from .story_io_epic import Epic
from .story_io_feature import Feature
from .story_io_story import Story
from .story_io_user import User
from .story_io_increment import Increment
from .story_io_renderer import DrawIORenderer
from .story_io_synchronizer import DrawIOSynchronizer


class StoryIODiagram(StoryIOComponent):
    """
    Main diagram class representing a complete story map.
    
    Supports both outline mode (epics/features/stories) and increments mode
    (with marketable releases).
    """
    
    def __init__(self, name: str = "Story Map",
                 drawio_file: Optional[Union[str, Path]] = None,
                 story_graph_file: Optional[Union[str, Path]] = None):
        super().__init__(name, None, None, None, False, None)
        self._drawio_file = Path(drawio_file) if drawio_file else None
        self._story_graph_file = Path(story_graph_file) if story_graph_file else None
        self._renderer = DrawIORenderer()
        self._synchronizer = DrawIOSynchronizer()
    
    @property
    def drawio_file(self) -> Optional[Path]:
        """Get the DrawIO file path."""
        return self._drawio_file
    
    @property
    def story_graph_file(self) -> Optional[Path]:
        """Get the story graph JSON file path."""
        return self._story_graph_file
    
    @property
    def epics(self) -> List[Epic]:
        """Get all epics in this diagram."""
        return [child for child in self.children if isinstance(child, Epic)]
    
    @property
    def sub_epics(self) -> List[Feature]:
        """Get all sub-epics directly in this diagram (not through epics)."""
        return [child for child in self.children if isinstance(child, Feature)]
    
    @property
    def features(self) -> List[Feature]:
        """Deprecated: Use sub_epics instead."""
        return self.sub_epics
    
    @property
    def stories(self) -> List[Story]:
        """Get all stories directly in this diagram."""
        return [child for child in self.children if isinstance(child, Story)]
    
    @property
    def increments(self) -> List[Increment]:
        """Get all increments in this diagram."""
        return [child for child in self.children if isinstance(child, Increment)]
    
    def search_for_any(self, query: str) -> List[StoryIOComponent]:
        """Search for any component matching the query."""
        return self.search_for_all_children(query)
    
    def search_for_epics(self, query: str) -> List[Epic]:
        """Search for epics matching the query."""
        results = self.search_for_any(query)
        return [r for r in results if isinstance(r, Epic)]
    
    def search_for_sub_epics(self, query: str) -> List[Feature]:
        """Search for sub-epics matching the query."""
        results = self.search_for_any(query)
        return [r for r in results if isinstance(r, Feature)]
    
    def search_for_features(self, query: str) -> List[Feature]:
        """Deprecated: Use search_for_sub_epics instead."""
        return self.search_for_sub_epics(query)
    
    def search_for_stories(self, query: str) -> List[Story]:
        """Search for stories matching the query."""
        results = self.search_for_any(query)
        return [r for r in results if isinstance(r, Story)]
    
    def add_user_to_story(self, story_name: str, user_name: str,
                          epic_name: Optional[str] = None,
                          sub_epic_name: Optional[str] = None) -> Story:
        """
        Find a story by name and add a user to it.
        
        Args:
            story_name: Name of the story to find
            user_name: Name of the user to add
            epic_name: Optional epic name to narrow search
            sub_epic_name: Optional sub-epic name to narrow search
        
        Returns:
            The Story object that was modified
        
        Raises:
            ValueError: If story is not found
        """
        story = None
        
        # Try to find story by epic/sub-epic context if provided
        if epic_name and sub_epic_name:
            for epic in self.epics:
                if epic.name == epic_name:
                    for sub_epic in epic.sub_epics:
                        if sub_epic.name == sub_epic_name:
                            for s in sub_epic.stories:
                                if s.name == story_name:
                                    story = s
                                    break
                            if story:
                                break
                    if story:
                        break
        
        # Fall back to search if not found or no context provided
        if not story:
            stories = self.search_for_stories(story_name)
            # Find exact match
            for s in stories:
                if s.name == story_name:
                    story = s
                    break
            # If no exact match, use first result
            if not story and stories:
                story = stories[0]
        
        if not story:
            raise ValueError(f"Story '{story_name}' not found" + 
                           (f" in Epic '{epic_name}', Sub-Epic '{sub_epic_name}'" 
                            if epic_name and sub_epic_name else ""))
        
        story.add_user(user_name)
        return story
    
    def remove_user_from_story(self, story_name: str, user_name: str,
                               epic_name: Optional[str] = None,
                               sub_epic_name: Optional[str] = None) -> Story:
        """
        Find a story by name and remove a user from it.
        
        Args:
            story_name: Name of the story to find
            user_name: Name of the user to remove
            epic_name: Optional epic name to narrow search
            sub_epic_name: Optional sub-epic name to narrow search
        
        Returns:
            The Story object that was modified
        
        Raises:
            ValueError: If story is not found
        """
        story = None
        
        # Try to find story by epic/sub-epic context if provided
        if epic_name and sub_epic_name:
            for epic in self.epics:
                if epic.name == epic_name:
                    for sub_epic in epic.sub_epics:
                        if sub_epic.name == sub_epic_name:
                            for s in sub_epic.stories:
                                if s.name == story_name:
                                    story = s
                                    break
                            if story:
                                break
                    if story:
                        break
        
        # Fall back to search if not found
        if not story:
            stories = self.search_for_stories(story_name)
            story = next((s for s in stories if s.name == story_name), None)
        
        if not story:
            raise ValueError(f"Story '{story_name}' not found" + 
                           (f" in Epic '{epic_name}', Sub-Epic '{sub_epic_name}'" 
                            if epic_name and sub_epic_name else ""))
        
        story.remove_user(user_name)
        return story
    
    def create_epic(self, epic_name: str, sequential_order: Optional[float] = None,
                    target_epic_name: Optional[str] = None) -> 'Epic':
        """
        Create a new epic in this diagram.
        
        Args:
            epic_name: Name of the new epic
            sequential_order: Optional sequential order (defaults to end)
            target_epic_name: Optional epic name to insert before
        
        Returns:
            The created Epic object
        """
        epic = Epic(name=epic_name, sequential_order=sequential_order)
        
        if target_epic_name:
            target = next((e for e in self.epics if e.name == target_epic_name), None)
            if target:
                epic.change_parent(self, target)
            else:
                epic.change_parent(self)
        else:
            epic.change_parent(self)
        
        return epic
    
    def create_sub_epic(self, sub_epic_name: str, epic_name: str,
                      sequential_order: Optional[float] = None,
                      target_sub_epic_name: Optional[str] = None) -> 'Feature':
        """
        Create a new sub-epic in an epic.
        
        Args:
            sub_epic_name: Name of the new sub-epic
            epic_name: Name of the epic to add sub-epic to
            sequential_order: Optional sequential order (defaults to end)
            target_sub_epic_name: Optional sub-epic name to insert before
        
        Returns:
            The created Feature object
        
        Raises:
            ValueError: If epic is not found
        """
        epic = next((e for e in self.epics if e.name == epic_name), None)
        if not epic:
            raise ValueError(f"Epic '{epic_name}' not found")
        
        feature = Feature(name=sub_epic_name, sequential_order=sequential_order)
        
        if target_sub_epic_name:
            target = next((f for f in epic.sub_epics if f.name == target_sub_epic_name), None)
            epic.add_sub_epic(feature, target)
        else:
            epic.add_sub_epic(feature)
        
        return feature
    
    def create_story(self, story_name: str, epic_name: str, sub_epic_name: str,
                    sequential_order: Optional[float] = None,
                    users: Optional[List[str]] = None,
                    story_type: Optional[str] = None,
                    target_story_name: Optional[str] = None) -> 'Story':
        """
        Create a new story in a sub-epic.
        
        Args:
            story_name: Name of the new story
            epic_name: Name of the epic containing the sub-epic
            sub_epic_name: Name of the sub-epic to add story to
            sequential_order: Optional sequential order (defaults to end)
            users: Optional list of user names
            story_type: Optional story type ('user', 'system', 'technical')
            target_story_name: Optional story name to insert before
        
        Returns:
            The created Story object
        
        Raises:
            ValueError: If epic or sub-epic is not found
        """
        epic = next((e for e in self.epics if e.name == epic_name), None)
        if not epic:
            raise ValueError(f"Epic '{epic_name}' not found")
        
        sub_epic = next((f for f in epic.sub_epics if f.name == sub_epic_name), None)
        if not sub_epic:
            raise ValueError(f"Sub-epic '{sub_epic_name}' not found in epic '{epic_name}'")
        
        story = Story(name=story_name, sequential_order=sequential_order,
                     users=users, story_type=story_type)
        
        if target_story_name:
            target = next((s for s in sub_epic.stories if s.name == target_story_name), None)
            story.change_parent(sub_epic, target)
        else:
            story.change_parent(sub_epic)
        
        return story
    
    def update_component(self, component_name: str, component_type: str,
                        new_name: Optional[str] = None,
                        sequential_order: Optional[float] = None,
                        epic_name: Optional[str] = None,
                        sub_epic_name: Optional[str] = None) -> 'StoryIOComponent':
        """
        Update a component's name or sequential order.
        
        Args:
            component_name: Name of the component to update
            component_type: Type of component ('epic', 'sub_epic', 'story')
            new_name: Optional new name for the component
            sequential_order: Optional new sequential order
            epic_name: Optional epic name for sub-epic/story search
            sub_epic_name: Optional sub-epic name for story search
        
        Returns:
            The updated component
        
        Raises:
            ValueError: If component is not found
        """
        component = None
        
        if component_type == "epic":
            component = next((e for e in self.epics if e.name == component_name), None)
        elif component_type == "feature":
            if epic_name:
                epic = next((e for e in self.epics if e.name == epic_name), None)
                if epic:
                    component = next((f for f in epic.sub_epics if f.name == component_name), None)
            if not component:
                for epic in self.epics:
                    component = next((f for f in epic.sub_epics if f.name == component_name), None)
                    if component:
                        break
        elif component_type == "story":
            if epic_name and sub_epic_name:
                epic = next((e for e in self.epics if e.name == epic_name), None)
                if epic:
                    sub_epic = next((f for f in epic.sub_epics if f.name == sub_epic_name), None)
                    if sub_epic:
                        component = next((s for s in sub_epic.stories if s.name == component_name), None)
            if not component:
                stories = self.search_for_stories(component_name)
                component = next((s for s in stories if s.name == component_name), None)
        
        if not component:
            raise ValueError(f"{component_type.capitalize()} '{component_name}' not found")
        
        if new_name:
            component.name = new_name
        if sequential_order is not None:
            component.sequential_order = sequential_order
            # Reorder siblings
            if component.parent:
                component.parent._reorder_siblings(component.parent.children)
        
        return component
    
    def remove_component(self, component_name: str, component_type: str,
                        epic_name: Optional[str] = None,
                        sub_epic_name: Optional[str] = None) -> 'StoryIOComponent':
        """
        Remove a component from the diagram.
        
        Args:
            component_name: Name of the component to remove
            component_type: Type of component ('epic', 'sub_epic', 'story')
            epic_name: Optional epic name for sub-epic/story search
            sub_epic_name: Optional sub-epic name for story search
        
        Returns:
            The removed component
        
        Raises:
            ValueError: If component is not found
        """
        component = None
        
        if component_type == "epic":
            component = next((e for e in self.epics if e.name == component_name), None)
            if component:
                self._remove_child(component)
        elif component_type == "feature":
            if epic_name:
                epic = next((e for e in self.epics if e.name == epic_name), None)
                if epic:
                    component = next((f for f in epic.sub_epics if f.name == component_name), None)
                    if component:
                        epic.remove_sub_epic(component)
            if not component:
                for epic in self.epics:
                    component = next((f for f in epic.sub_epics if f.name == component_name), None)
                    if component:
                        epic.remove_sub_epic(component)
                        break
        elif component_type == "story":
            if epic_name and sub_epic_name:
                epic = next((e for e in self.epics if e.name == epic_name), None)
                if epic:
                    sub_epic = next((f for f in epic.sub_epics if f.name == sub_epic_name), None)
                    if sub_epic:
                        component = next((s for s in sub_epic.stories if s.name == component_name), None)
                        if component:
                            feature._remove_child(component)
            if not component:
                stories = self.search_for_stories(component_name)
                component = next((s for s in stories if s.name == component_name), None)
                if component and component.parent:
                    component.parent._remove_child(component)
        
        if not component:
            raise ValueError(f"{component_type.capitalize()} '{component_name}' not found")
        
        return component
    
    def reorder_component(self, component_name: str, component_type: str,
                         target_component_name: str,
                         epic_name: Optional[str] = None,
                         sub_epic_name: Optional[str] = None) -> 'StoryIOComponent':
        """
        Move a component before another component (reorder).
        
        Args:
            component_name: Name of the component to move
            component_type: Type of component ('epic', 'sub_epic', 'story')
            target_component_name: Name of the component to move before
            epic_name: Optional epic name for sub-epic/story search
            sub_epic_name: Optional sub-epic name for story search
        
        Returns:
            The moved component
        
        Raises:
            ValueError: If component or target is not found
        """
        component = None
        target = None
        
        if component_type == "epic":
            component = next((e for e in self.epics if e.name == component_name), None)
            target = next((e for e in self.epics if e.name == target_component_name), None)
        elif component_type == "feature":
            if epic_name:
                epic = next((e for e in self.epics if e.name == epic_name), None)
                if epic:
                    component = next((f for f in epic.sub_epics if f.name == component_name), None)
                    target = next((f for f in epic.features if f.name == target_component_name), None)
        elif component_type == "story":
            if epic_name and sub_epic_name:
                epic = next((e for e in self.epics if e.name == epic_name), None)
                if epic:
                    sub_epic = next((f for f in epic.sub_epics if f.name == sub_epic_name), None)
                    if sub_epic:
                        component = next((s for s in sub_epic.stories if s.name == component_name), None)
                        target = next((s for s in sub_epic.stories if s.name == target_component_name), None)
        
        if not component:
            raise ValueError(f"{component_type.capitalize()} '{component_name}' not found")
        if not target:
            raise ValueError(f"{component_type.capitalize()} '{target_component_name}' not found")
        
        component.move_before(target)
        return component
    
    def render_outline(self, output_path: Optional[Union[str, Path]] = None,
                      layout_data: Optional[Dict[str, Any]] = None,
                      story_graph: Optional[Dict[str, Any]] = None,
                      force_outline: bool = False) -> Dict[str, Any]:
        """
        Render diagram as outline (no increments).
        
        Args:
            output_path: Optional path for DrawIO output file
            layout_data: Optional layout data to preserve positions
            story_graph: Optional story graph dictionary to render directly (if provided, uses this instead of diagram state)
            force_outline: If True, force outline mode (disable auto-exploration mode)
        
        Returns:
            Dictionary with output_path and summary
        """
        if output_path is None and self._drawio_file:
            output_path = self._drawio_file.parent / "story-map-outline.drawio"
        elif output_path:
            output_path = Path(output_path)
        else:
            raise ValueError("No output path specified and no drawio_file set")
        
        # Use provided story_graph or convert diagram to story graph format
        if story_graph is not None:
            graph_data = story_graph
        else:
            graph_data = self._to_story_graph_format(include_increments=False)
        
        # Render using renderer
        return self._renderer.render_outline(
            story_graph=graph_data,
            output_path=output_path,
            layout_data=layout_data,
            force_outline=force_outline
        )
    
    @staticmethod
    def render_outline_from_graph(story_graph: Union[Dict[str, Any], str, Path],
                                  output_path: Union[str, Path],
                                  layout_data: Optional[Dict[str, Any]] = None,
                                  force_outline: bool = False) -> Dict[str, Any]:
        """
        Render outline directly from story graph JSON (static method).
        
        Args:
            story_graph: Story graph as dict, JSON file path, or Path
            output_path: Path for DrawIO output file
            layout_data: Optional layout data to preserve positions
            force_outline: If True, force outline mode (disable auto-exploration mode)
        
        Returns:
            Dictionary with output_path and summary
        
        Example:
            >>> # From dictionary
            >>> graph = {'epics': [...]}
            >>> StoryIODiagram.render_outline_from_graph(graph, 'output.drawio')
            
            >>> # From JSON file
            >>> StoryIODiagram.render_outline_from_graph('story_graph.json', 'output.drawio')
        """
        import json
        
        # Load story graph if path provided
        if isinstance(story_graph, (str, Path)):
            story_graph_path = Path(story_graph)
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
        else:
            graph_data = story_graph
        
        output_path = Path(output_path)
        
        # Create temporary diagram instance just for rendering
        diagram = StoryIODiagram()
        return diagram._renderer.render_outline(
            story_graph=graph_data,
            output_path=output_path,
            layout_data=layout_data,
            force_outline=force_outline
        )
    
    def render_exploration(self, output_path: Optional[Union[str, Path]] = None,
                          layout_data: Optional[Dict[str, Any]] = None,
                          scope: Optional[str] = None,
                          story_graph: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render diagram with acceptance criteria (exploration mode).
        
        Args:
            output_path: Optional path for DrawIO output file
            layout_data: Optional layout data to preserve positions
            scope: Optional scope identifier for filtering stories
            story_graph: Optional story graph dictionary to render directly (if provided, uses this instead of diagram state)
        
        Returns:
            Dictionary with output_path and summary
        """
        if output_path is None and self._drawio_file:
            output_path = self._drawio_file.parent / "story-map-exploration.drawio"
        elif output_path:
            output_path = Path(output_path)
        else:
            raise ValueError("No output path specified and no drawio_file set")
        
        # Use provided story_graph or convert diagram to story graph format
        if story_graph is not None:
            graph_data = story_graph
        else:
            graph_data = self._to_story_graph_format(include_increments=False)
        
        # Render using renderer
        return self._renderer.render_exploration(
            story_graph=graph_data,
            output_path=output_path,
            layout_data=layout_data,
            scope=scope
        )
    
    def render_increments(self, output_path: Optional[Union[str, Path]] = None,
                         layout_data: Optional[Dict[str, Any]] = None,
                         story_graph: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render diagram with increments.
        
        Args:
            output_path: Optional path for DrawIO output file
            layout_data: Optional layout data to preserve positions
            story_graph: Optional story graph dictionary to render directly (if provided, uses this instead of diagram state)
        
        Returns:
            Dictionary with output_path and summary
        """
        if output_path is None and self._drawio_file:
            output_path = self._drawio_file.parent / "story-map.drawio"
        elif output_path:
            output_path = Path(output_path)
        else:
            raise ValueError("No output path specified and no drawio_file set")
        
        # Use provided story_graph or convert diagram to story graph format
        if story_graph is not None:
            graph_data = story_graph
        else:
            graph_data = self._to_story_graph_format(include_increments=True)
        
        # If we have a source JSON file, load it directly to preserve stories in increments
        if self._source_path and self._source_path.exists():
            import json
            with open(self._source_path, 'r', encoding='utf-8') as f:
                raw_graph_data = json.load(f)
            # Use raw JSON data which preserves stories in increments' sub_epics
            graph_data = raw_graph_data
        
        # Render using renderer
        return self._renderer.render_increments(
            story_graph=graph_data,
            output_path=output_path,
            layout_data=layout_data
        )
    
    def render_discovery(self, output_path: Optional[Union[str, Path]] = None,
                        layout_data: Optional[Dict[str, Any]] = None,
                        increment_names: Optional[list] = None,
                        story_graph: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render diagram with discovery increments (filtered by increment names).
        
        Args:
            output_path: Optional path for DrawIO output file
            layout_data: Optional layout data to preserve positions
            increment_names: Optional list of increment names to filter to
            story_graph: Optional story graph dictionary to render directly
        
        Returns:
            Dictionary with output_path and summary
        """
        if output_path is None and self._drawio_file:
            output_path = self._drawio_file.parent / "story-map-discovery.drawio"
        elif output_path:
            output_path = Path(output_path)
        else:
            raise ValueError("No output path specified and no drawio_file set")
        
        # Use provided story_graph or convert diagram to story graph format
        if story_graph is not None:
            graph_data = story_graph
        else:
            graph_data = self._to_story_graph_format(include_increments=True)
        
        # If we have a source JSON file, load it directly to preserve stories in increments
        if self._source_path and self._source_path.exists():
            import json
            with open(self._source_path, 'r', encoding='utf-8') as f:
                raw_graph_data = json.load(f)
            # Use raw JSON data which preserves stories in increments' sub_epics
            graph_data = raw_graph_data
        
        # Render using renderer
        return self._renderer.render_discovery(
            story_graph=graph_data,
            output_path=output_path,
            layout_data=layout_data,
            increment_names=increment_names
        )
    
    @staticmethod
    def render_exploration_from_graph(story_graph: Union[Dict[str, Any], str, Path],
                                     output_path: Union[str, Path],
                                     layout_data: Optional[Dict[str, Any]] = None,
                                     scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Static method to render exploration diagram directly from story graph data.
        
        Args:
            story_graph: Story graph dictionary, JSON file path, or Path object
            output_path: Output DrawIO file path
            layout_data: Optional layout data to preserve positions
            scope: Optional scope identifier for filtering stories
        
        Returns:
            Dictionary with output_path and summary
        
        Examples:
            >>> graph = {"epics": [...]}
            >>> StoryIODiagram.render_exploration_from_graph(graph, 'output.drawio')
            >>> StoryIODiagram.render_exploration_from_graph('story_graph.json', 'output.drawio')
        """
        # Load story graph if it's a file path
        if isinstance(story_graph, (str, Path)):
            story_graph_path = Path(story_graph)
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                import json
                story_graph = json.load(f)
        
        # Create renderer and render
        renderer = DrawIORenderer()
        output_path = Path(output_path)
        return renderer.render_exploration(
            story_graph=story_graph,
            output_path=output_path,
            layout_data=layout_data,
            scope=scope
        )
    
    @staticmethod
    def render_increments_from_graph(story_graph: Union[Dict[str, Any], str, Path],
                                    output_path: Union[str, Path],
                                    layout_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Render increments directly from story graph JSON (static method).
        
        Args:
            story_graph: Story graph as dict, JSON file path, or Path
            output_path: Path for DrawIO output file
            layout_data: Optional layout data to preserve positions
        
        Returns:
            Dictionary with output_path and summary
        
        Example:
            >>> # From dictionary
            >>> graph = {'epics': [...], 'increments': [...]}
            >>> StoryIODiagram.render_increments_from_graph(graph, 'output.drawio')
            
            >>> # From JSON file
            >>> StoryIODiagram.render_increments_from_graph('story_graph.json', 'output.drawio')
        """
        import json
        
        # Load story graph if path provided
        if isinstance(story_graph, (str, Path)):
            story_graph_path = Path(story_graph)
            with open(story_graph_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
        else:
            graph_data = story_graph
        
        output_path = Path(output_path)
        
        # Create temporary diagram instance just for rendering
        diagram = StoryIODiagram()
        return diagram._renderer.render_increments(
            story_graph=graph_data,
            output_path=output_path,
            layout_data=layout_data
        )
    
    def synchronize_outline(self, drawio_path: Optional[Union[str, Path]] = None,
                           original_path: Optional[Union[str, Path]] = None,
                           output_path: Optional[Union[str, Path]] = None,
                           generate_report: bool = False) -> Dict[str, Any]:
        """
        Synchronize diagram from DrawIO outline file.
        
        Args:
            drawio_path: Path to DrawIO outline file
            original_path: Optional path to original story graph for comparison
            output_path: Optional path to write extracted JSON (also saves layout file)
            generate_report: If True, include synchronization report in result
        
        Returns:
            Synchronized diagram data (with optional report if generate_report=True)
        """
        if drawio_path:
            drawio_path = Path(drawio_path)
        elif self._drawio_file:
            drawio_path = self._drawio_file
        else:
            raise ValueError("No drawio_path specified and no drawio_file set")
        
        # Store state before sync for comparison
        before_state = None
        if generate_report:
            before_state = {
                'epics_count': len(self.epics),
                'sub_epics_count': len(self.sub_epics),
                'stories_count': len(self.stories)
            }
        
        # Synchronize using synchronizer (pass output_path to enable layout saving)
        if output_path:
            output_path = Path(output_path)
        
        extracted_data = self._synchronizer.synchronize_outline(
            drawio_path=drawio_path,
            original_path=original_path,
            output_path=output_path
        )
        
        # Load into diagram structure
        self._load_from_story_graph_format(extracted_data)
        
        # Generate report if requested
        if generate_report:
            report = self.generate_sync_report(before_state, extracted_data, original_path)
            extracted_data['sync_report'] = report
        
        # Extract layout file path if it was created
        if output_path:
            layout_path = output_path.parent / f"{output_path.stem}-layout.json"
            if layout_path.exists():
                extracted_data['layout_file'] = str(layout_path)
        
        return extracted_data
    
    def synchronize_increments(self, drawio_path: Optional[Union[str, Path]] = None,
                              original_path: Optional[Union[str, Path]] = None,
                              output_path: Optional[Union[str, Path]] = None,
                              generate_report: bool = False) -> Dict[str, Any]:
        """
        Synchronize diagram from DrawIO increments file.
        
        Args:
            drawio_path: Path to DrawIO file with increments
            original_path: Optional path to original story graph for comparison
            output_path: Optional path to write extracted JSON (also saves layout file)
            generate_report: If True, include synchronization report in result
        
        Returns:
            Synchronized diagram data (with optional report if generate_report=True)
        """
        if drawio_path:
            drawio_path = Path(drawio_path)
        elif self._drawio_file:
            drawio_path = self._drawio_file
        else:
            raise ValueError("No drawio_path specified and no drawio_file set")
        
        # Store state before sync for comparison
        before_state = None
        if generate_report:
            before_state = {
                'epics_count': len(self.epics),
                'sub_epics_count': len(self.sub_epics),
                'stories_count': len(self.stories),
                'increments_count': len(self.increments)
            }
        
        # Synchronize using synchronizer (pass output_path to enable layout saving)
        if output_path:
            output_path = Path(output_path)
        
        extracted_data = self._synchronizer.synchronize_increments(
            drawio_path=drawio_path,
            original_path=original_path,
            output_path=output_path
        )
        
        # Load into diagram structure
        self._load_from_story_graph_format(extracted_data)
        
        # Generate report if requested
        if generate_report:
            report = self.generate_sync_report(before_state, extracted_data, original_path)
            extracted_data['sync_report'] = report
        
        # Extract layout file path if it was created
        if output_path:
            layout_path = output_path.parent / f"{output_path.stem}-layout.json"
            if layout_path.exists():
                extracted_data['layout_file'] = str(layout_path)
        
        return extracted_data
    
    def _to_story_graph_format(self, include_increments: bool = False) -> Dict[str, Any]:
        """Convert diagram to story graph JSON format."""
        result = {
            'epics': [epic.render() for epic in self.epics]
        }
        
        if include_increments and self.increments:
            result['increments'] = [inc.render() for inc in self.increments]
        
        return result
    
    def _load_from_story_graph_format(self, data: Dict[str, Any]) -> None:
        """Load diagram from story graph JSON format."""
        # Clear existing children
        self._children.clear()
        
        # Load epics
        for epic_data in data.get('epics', []):
            epic = self._create_epic_from_data(epic_data)
            epic.change_parent(self)
        
        # Load increments
        for inc_data in data.get('increments', []):
            increment = self._create_increment_from_data(inc_data)
            increment.change_parent(self)
    
    def _create_epic_from_data(self, data: Dict[str, Any]) -> Epic:
        """Create epic from dictionary data."""
        from .story_io_position import Position, Boundary
        
        epic = Epic(
            name=data['name'],
            sequential_order=data.get('sequential_order'),
            estimated_stories=data.get('estimated_stories')
        )
        
        # Handle sub_epics (recursive)
        for sub_epic_data in data.get('sub_epics', []):
            sub_epic = self._create_feature_from_sub_epic_data(sub_epic_data, epic)
            sub_epic.change_parent(epic)
        
        # Add direct stories (new format allows stories directly under epic)
        for story_data in data.get('stories', []):
            story = self._create_story_from_data(story_data)
            story.change_parent(epic)
        
        return epic
    
    def _create_feature_from_sub_epic_data(self, data: Dict[str, Any], parent_epic: Epic) -> Feature:
        """Create feature from sub_epic data (new format, supports nested sub_epics)."""
        # Support both story_count (legacy) and estimated_stories (new)
        story_count = data.get('story_count') or data.get('estimated_stories')
        feature = Feature(
            name=data['name'],
            sequential_order=data.get('sequential_order'),
            story_count=story_count
        )
        
        # Handle nested sub_epics (recursive)
        for nested_sub_epic_data in data.get('sub_epics', []):
            nested_feature = self._create_feature_from_sub_epic_data(nested_sub_epic_data, parent_epic)
            nested_feature.change_parent(feature)
        
        # Handle story_groups in sub_epic (new format)
        story_groups_data = data.get('story_groups', [])
        if story_groups_data:
            # Preserve story_groups structure for rendering
            feature._story_groups_data = story_groups_data
            # Also load stories as children for internal operations
            for story_group_data in story_groups_data:
                group_stories = story_group_data.get('stories', [])
                for story_data in group_stories:
                    story = self._create_story_from_data(story_data)
                    story.change_parent(feature)
        else:
            # Handle stories in sub_epic (only if no story_groups)
            for story_data in data.get('stories', []):
                story = self._create_story_from_data(story_data)
                story.change_parent(feature)
        
        return feature
    
    def _create_feature_from_data(self, data: Dict[str, Any]) -> Feature:
        """Create feature from dictionary data."""
        # Support both story_count (legacy) and estimated_stories (new)
        story_count = data.get('story_count') or data.get('estimated_stories')
        feature = Feature(
            name=data['name'],
            sequential_order=data.get('sequential_order'),
            story_count=story_count
        )
        return feature
    
    def _create_story_from_data(self, data: Dict[str, Any]) -> Story:
        """Create Story from data dictionary, handling story_type."""
        from .story_io_position import Position
        
        # Handle Steps (from structured.json) or steps (from story graph)
        steps = data.get('Steps', []) or data.get('steps', [])
        # Handle behavioral_ac as Steps for compatibility
        if not steps and 'behavioral_ac' in data:
            steps = data['behavioral_ac']
        # Handle new format: acceptance_criteria (convert to Steps format)
        if not steps and 'acceptance_criteria' in data:
            steps = []
            for i, ac in enumerate(data.get('acceptance_criteria', [])):
                if isinstance(ac, dict):
                    steps.append({
                        'description': ac.get('description', ''),
                        'user': ac.get('user', ''),
                        'sequential_order': ac.get('sequential_order', i + 1)
                    })
                elif isinstance(ac, str):
                    # Handle string format - treat as description
                    steps.append({
                        'description': ac,
                        'user': '',
                        'sequential_order': i + 1
                    })
        
        story = Story(
            name=data['name'],
            sequential_order=data.get('sequential_order'),
            users=data.get('users', []),
            steps=steps,
            vertical_order=data.get('vertical_order'),
            story_type=data.get('story_type'),  # 'user' (default), 'system', or 'technical'
            connector=data.get('connector')  # 'and', 'or', 'opt', or None
        )
        
        # Handle nested stories (new format: stories can contain nested stories)
        for nested_story_data in data.get('stories', []):
            nested_story = self._create_story_from_data(nested_story_data)
            nested_story.change_parent(story)
        
        return story
    
    def _create_increment_from_data(self, data: Dict[str, Any]) -> Increment:
        """Create increment from dictionary data."""
        # Preserve priority as-is (can be string like "NOW" or int)
        priority = data.get('priority', 1)
        if not isinstance(priority, (int, str)):
            priority = 1
        
        # Handle both 'name' and 'title' fields (title is used in base_bot format)
        increment_name = data.get('name') or data.get('title', '')
        increment = Increment(
            name=increment_name,
            priority=priority  # Pass as-is to preserve string format
        )
        
        # Store story names if provided (increments reference stories by name)
        # Only support flat stories array structure (no nested epics/sub_epics)
        if 'stories' in data and isinstance(data['stories'], list):
            story_list = data['stories']
            if story_list:
                # Check if stories are names (strings) or objects
                if isinstance(story_list[0], str):
                    # Stories are names - store as story_names
                    increment.story_names = story_list
                else:
                    # Stories are objects - create story objects and add to increment
                    for story_data in story_list:
                        if isinstance(story_data, dict):
                            story = self._create_story_from_data(story_data)
                            story.change_parent(increment)
        
        # Store additional increment metadata
        if 'relative_size' in data:
            increment._relative_size = data['relative_size']
        if 'approach' in data:
            increment._approach = data['approach']
        if 'focus' in data:
            increment._focus = data['focus']
        
        return increment
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize diagram from external source."""
        if self._drawio_file and self._drawio_file.exists():
            return self.synchronize_outline(self._drawio_file)
        return {'status': 'no_source_file'}
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for current diagram state."""
        return {
            'diagram': self.name,
            'epics_count': len(self.epics),
            'sub_epics_count': len(self.sub_epics),
            'stories_count': len(self.stories),
            'increments_count': len(self.increments),
            'status': 'ready'
        }
    
    def generate_sync_report(self, before_state: Optional[Dict[str, Any]] = None,
                            extracted_data: Optional[Dict[str, Any]] = None,
                            original_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Generate detailed synchronization report with before/after comparison.
        
        Args:
            before_state: Optional state before sync (dict with counts)
            extracted_data: Optional extracted data from sync
            original_path: Optional path to original file for comparison
        
        Returns:
            Detailed synchronization report
        """
        current_report = self.synchronize_report()
        
        report = {
            'timestamp': self._get_timestamp(),
            'current_state': current_report,
            'sync_summary': {
                'status': 'completed',
                'source': str(self._drawio_file) if self._drawio_file else 'unknown'
            }
        }
        
        # Add before/after comparison if before_state provided
        if before_state:
            report['changes'] = {
                'epics_count_delta': current_report['epics_count'] - before_state.get('epics_count', 0),
                'sub_epics_count_delta': current_report['sub_epics_count'] - before_state.get('sub_epics_count', 0),
                'stories_count_delta': current_report['stories_count'] - before_state.get('stories_count', 0),
                'before': before_state,
                'after': {
                    'epics_count': current_report['epics_count'],
                    'sub_epics_count': current_report['sub_epics_count'],
                    'stories_count': current_report['stories_count']
                }
            }
            
            if 'increments_count' in before_state:
                report['changes']['increments_count_delta'] = (
                    current_report['increments_count'] - before_state.get('increments_count', 0)
                )
                report['changes']['after']['increments_count'] = current_report['increments_count']
        
        # Add component details
        if extracted_data:
            report['extracted'] = {
                'epics_found': len(extracted_data.get('epics', [])),
                'increments_found': len(extracted_data.get('increments', []))
            }
        
        # Add comparison with original if provided
        if original_path:
            import json
            original_path = Path(original_path)
            if original_path.exists():
                try:
                    with open(original_path, 'r', encoding='utf-8') as f:
                        original_data = json.load(f)
                    
                    report['comparison'] = {
                        'original_file': str(original_path),
                        'original_epics': len(original_data.get('epics', [])),
                        'current_epics': current_report['epics_count'],
                        'epics_match': len(original_data.get('epics', [])) == current_report['epics_count']
                    }
                except Exception as e:
                    report['comparison'] = {
                        'error': f"Could not compare with original: {str(e)}"
                    }
        
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this diagram with another."""
        if not isinstance(other, StoryIODiagram):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name,
            'epics_count_match': len(self.epics) == len(other.epics),
            'stories_count_match': len(self.stories) == len(other.stories)
        }
    
    def render(self) -> Dict[str, Any]:
        """Render diagram to JSON representation."""
        return self._to_story_graph_format(include_increments=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diagram to dictionary."""
        result = super().to_dict()
        result['type'] = 'diagram'
        result['epics'] = [e.to_dict() for e in self.epics]
        result['increments'] = [i.to_dict() for i in self.increments]
        return result
    
    def save_story_graph(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        """Save diagram as story graph JSON."""
        if output_path is None:
            if self._story_graph_file:
                output_path = self._story_graph_file
            else:
                raise ValueError("No output path specified and no story_graph_file set")
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.render(), f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @classmethod
    def load_from_story_graph(cls, story_graph_path: Union[str, Path],
                              drawio_file: Optional[Union[str, Path]] = None) -> 'StoryIODiagram':
        """Load diagram from story graph JSON file."""
        import json
        
        story_graph_path = Path(story_graph_path)
        with open(story_graph_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        diagram = cls(
            name="Story Map",
            drawio_file=drawio_file,
            story_graph_file=story_graph_path
        )
        diagram._load_from_story_graph_format(data)
        diagram._source_path = story_graph_path  # Store source path for raw JSON access
        
        return diagram
    
    @classmethod
    def sync_from_drawio(cls, drawio_path: Union[str, Path],
                        original_path: Optional[Union[str, Path]] = None,
                        generate_report: bool = False) -> 'StoryIODiagram':
        """
        Create diagram by synchronizing from DrawIO file (convenience method).
        
        Args:
            drawio_path: Path to DrawIO file
            original_path: Optional original story graph for comparison
            generate_report: If True, include synchronization report in result
        
        Returns:
            StoryIODiagram loaded with synchronized data
        
        Example:
            >>> diagram = StoryIODiagram.sync_from_drawio('story-map.drawio')
            >>> diagram.save_story_graph('synced.json')
            
            >>> # With report
            >>> diagram = StoryIODiagram.sync_from_drawio('story-map.drawio', generate_report=True)
            >>> print(diagram.synchronize_report())
        """
        drawio_path = Path(drawio_path)
        diagram = cls(drawio_file=drawio_path)
        diagram.synchronize_outline(drawio_path, original_path, generate_report=generate_report)
        return diagram
    
    def generate_merge_report(self, extracted_path: Union[str, Path],
                             original_path: Union[str, Path],
                             report_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Generate a merge report comparing extracted and original story graphs.
        
        Args:
            extracted_path: Path to extracted story graph JSON (from sync)
            original_path: Path to original story graph JSON
            report_path: Optional path to write report JSON
        
        Returns:
            Dictionary containing merge report with matches, new stories, removed stories
        
        Example:
            >>> diagram = StoryIODiagram.sync_from_drawio('story-map.drawio')
            >>> diagram.save_story_graph('extracted.json')
            >>> report = diagram.generate_merge_report('extracted.json', 'original.json')
            >>> print(f"Matches: {report['summary']['exact_matches']}")
        """
        return self._synchronizer.generate_merge_report(extracted_path, original_path, report_path)
    
    def merge_story_graphs(self, extracted_path: Union[str, Path],
                          original_path: Union[str, Path],
                          report_path: Union[str, Path],
                          output_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Merge extracted story graph with original, preserving Steps from original.
        Uses merge report to match stories and merge their data.
        
        Args:
            extracted_path: Path to extracted story graph JSON (from sync)
            original_path: Path to original story graph JSON
            report_path: Path to merge report JSON (from generate_merge_report)
            output_path: Path to write merged story graph JSON
        
        Returns:
            Dictionary containing merged story graph
        
        Example:
            >>> # Generate report first
            >>> diagram = StoryIODiagram.sync_from_drawio('story-map.drawio')
            >>> diagram.save_story_graph('extracted.json')
            >>> report = diagram.generate_merge_report('extracted.json', 'original.json', 'report.json')
            >>> 
            >>> # Then merge using the report
            >>> merged = diagram.merge_story_graphs('extracted.json', 'original.json', 'report.json', 'merged.json')
        """
        return self._synchronizer.merge_story_graphs(extracted_path, original_path, report_path, output_path)
    
    @staticmethod
    def merge_from_report(extracted_path: Union[str, Path],
                         original_path: Union[str, Path],
                         report_path: Union[str, Path],
                         output_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Static method to merge story graphs using a merge report.
        
        Args:
            extracted_path: Path to extracted story graph JSON
            original_path: Path to original story graph JSON
            report_path: Path to merge report JSON
            output_path: Path to write merged story graph JSON
        
        Returns:
            Dictionary containing merged story graph
        
        Example:
            >>> merged = StoryIODiagram.merge_from_report(
            ...     'extracted.json',
            ...     'original.json',
            ...     'merge-report.json',
            ...     'merged.json'
            ... )
        """
        from .story_io_synchronizer import DrawIOSynchronizer
        synchronizer = DrawIOSynchronizer()
        return synchronizer.merge_story_graphs(extracted_path, original_path, report_path, output_path)

