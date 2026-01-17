"""
MCP Server for Story IO Operations

Provides MCP tools for rendering, synchronizing, and manipulating story maps.
"""

import json
import sys
from pathlib import Path
from typing import Optional, List

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Warning: mcp.server.fastmcp not available. MCP server functionality disabled.", file=sys.stderr)
    FastMCP = None

from .story_io_diagram import StoryIODiagram


if FastMCP:
    mcp = FastMCP("Story IO")
else:
    mcp = None


def _load_diagram_from_path(story_graph_path: Optional[str] = None,
                           drawio_path: Optional[str] = None) -> StoryIODiagram:
    """Load diagram from file path."""
    if drawio_path:
        # Load from DrawIO (sync from diagram)
        return StoryIODiagram.sync_from_drawio(Path(drawio_path))
    elif story_graph_path:
        return StoryIODiagram.load_from_story_graph(Path(story_graph_path))
    else:
        return StoryIODiagram()


def _save_diagram(diagram: StoryIODiagram, 
                 story_graph_path: Optional[str] = None,
                 drawio_path: Optional[str] = None,
                 output_path: Optional[str] = None) -> str:
    """
    Save diagram to file(s). Returns the output path used.
    Real-time sync between DrawIO and JSON is handled by StoryIODiagram itself.
    """
    # If output_path specified, determine type by extension or input source
    if output_path:
        output = Path(output_path)
        # If extension suggests DrawIO or we loaded from DrawIO, render to DrawIO
        if output.suffix == '.drawio' or drawio_path:
            diagram.render_outline(output_path=output)
            return str(output)
        else:
            # Save to JSON story graph
            diagram.save_story_graph(output)
            return str(output)
    elif drawio_path:
        # Render back to DrawIO (same file)
        output_drawio = Path(drawio_path)
        diagram.render_outline(output_path=output_drawio)
        return str(output_drawio)
    elif story_graph_path:
        # Save to JSON story graph (same file)
        output = Path(story_graph_path)
        diagram.save_story_graph(output)
        return str(output)
    else:
        raise ValueError("Must provide either drawio_path or story_graph_path")


if mcp:
    @mcp.tool()
    def render_outline(
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        output_path: str = "story-map-outline.drawio",
        layout_json: Optional[str] = None
    ) -> str:
        """
        Render story graph as outline DrawIO diagram (no increments).
        
        Args:
            story_graph_path: Path to story graph JSON file
            drawio_path: Optional DrawIO file path
            output_path: Output path for DrawIO file
            layout_json: Optional JSON string with layout data
        
        Returns:
            JSON string with result information
        """
        try:
            if story_graph_path:
                diagram = StoryIODiagram.load_from_story_graph(Path(story_graph_path), Path(drawio_path) if drawio_path else None)
            else:
                raise ValueError("story_graph_path is required")
            
            layout_data = None
            if layout_json:
                layout_data = json.loads(layout_json)
            
            result = diagram.render_outline(output_path=Path(output_path), layout_data=layout_data)
            
            return json.dumps({
                "success": True,
                "output_path": str(result["output_path"]),
                "summary": result["summary"]
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def render_increments(
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        output_path: str = "story-map.drawio",
        layout_json: Optional[str] = None
    ) -> str:
        """
        Render story graph with increments as DrawIO diagram.
        
        Args:
            story_graph_path: Path to story graph JSON file
            drawio_path: Optional DrawIO file path
            output_path: Output path for DrawIO file
            layout_json: Optional JSON string with layout data
        
        Returns:
            JSON string with result information
        """
        try:
            if story_graph_path:
                diagram = StoryIODiagram.load_from_story_graph(Path(story_graph_path), Path(drawio_path) if drawio_path else None)
            else:
                raise ValueError("story_graph_path is required")
            
            layout_data = None
            if layout_json:
                layout_data = json.loads(layout_json)
            
            result = diagram.render_increments(output_path=Path(output_path), layout_data=layout_data)
            
            return json.dumps({
                "success": True,
                "output_path": str(result["output_path"]),
                "summary": result["summary"]
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def synchronize_outline(
        drawio_path: str,
        original_path: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Synchronize story graph from DrawIO outline file.
        
        Args:
            drawio_path: Path to DrawIO outline file
            original_path: Optional path to original story graph for comparison
            output_path: Optional path to save synchronized story graph
        
        Returns:
            JSON string with synchronized data
        """
        try:
            diagram = StoryIODiagram(drawio_file=Path(drawio_path))
            
            original = Path(original_path) if original_path else None
            result = diagram.synchronize_outline(
                drawio_path=Path(drawio_path),
                original_path=original
            )
            
            if output_path:
                diagram.save_story_graph(Path(output_path))
            
            return json.dumps({
                "success": True,
                "epics_count": len(result.get("epics", [])),
                "output_path": output_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def synchronize_increments(
        drawio_path: str,
        original_path: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Synchronize story graph from DrawIO increments file.
        
        Args:
            drawio_path: Path to DrawIO file with increments
            original_path: Optional path to original story graph for comparison
            output_path: Optional path to save synchronized story graph
        
        Returns:
            JSON string with synchronized data
        """
        try:
            diagram = StoryIODiagram(drawio_file=Path(drawio_path))
            
            original = Path(original_path) if original_path else None
            result = diagram.synchronize_increments(
                drawio_path=Path(drawio_path),
                original_path=original
            )
            
            if output_path:
                diagram.save_story_graph(Path(output_path))
            
            return json.dumps({
                "success": True,
                "epics_count": len(result.get("epics", [])),
                "increments_count": len(result.get("increments", [])),
                "output_path": output_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def search_story_map(
        story_graph_path: str,
        query: str,
        component_type: str = "any"
    ) -> str:
        """
        Search for components in story graph.
        
        Args:
            story_graph_path: Path to story graph JSON file
            query: Search query string
            component_type: Type to search for (any, epic, feature, story)
        
        Returns:
            JSON string with search results
        """
        try:
            diagram = StoryIODiagram.load_from_story_graph(Path(story_graph_path))
            
            results = []
            if component_type == "any":
                results = diagram.search_for_any(query)
            elif component_type == "epic":
                results = diagram.search_for_epics(query)
            elif component_type == "feature":
                results = diagram.search_for_features(query)
            elif component_type == "story":
                results = diagram.search_for_stories(query)
            
            results_data = []
            for result in results:
                results_data.append({
                    "type": result.__class__.__name__,
                    "name": result.name,
                    "sequential_order": result.sequential_order
                })
            
            return json.dumps({
                "success": True,
                "query": query,
                "component_type": component_type,
                "results": results_data,
                "count": len(results_data)
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def create_epic(
        epic_name: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        sequential_order: Optional[float] = None,
        target_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a new epic in the story graph or diagram.
        
        Args:
            epic_name: Name of the new epic
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            sequential_order: Optional sequential order (defaults to end)
            target_epic_name: Optional epic name to insert before
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            diagram.create_epic(epic_name, sequential_order, target_epic_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "epic_name": epic_name,
                "epics_count": len(diagram.epics),
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def create_sub_epic(
        sub_epic_name: str,
        epic_name: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        sequential_order: Optional[float] = None,
        target_sub_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a new sub-epic in an epic.
        
        Args:
            sub_epic_name: Name of the new sub-epic
            epic_name: Name of the epic to add sub-epic to
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            sequential_order: Optional sequential order (defaults to end)
            target_sub_epic_name: Optional sub-epic name to insert before
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            sub_epic = diagram.create_sub_epic(sub_epic_name, epic_name, sequential_order, target_sub_epic_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "sub_epic_name": sub_epic_name,
                "epic_name": epic_name,
                "sub_epics_count": len(sub_epic.parent.sub_epics),
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def create_story(
        story_name: str,
        epic_name: str,
        sub_epic_name: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        sequential_order: Optional[float] = None,
        users: Optional[List[str]] = None,
        story_type: Optional[str] = None,
        target_story_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a new story in a sub-epic.
        
        Args:
            story_name: Name of the new story
            epic_name: Name of the epic containing the sub-epic
            sub_epic_name: Name of the sub-epic to add story to
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            sequential_order: Optional sequential order (defaults to end)
            users: Optional list of user names
            story_type: Optional story type ('user', 'system', 'technical')
            target_story_name: Optional story name to insert before
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            story = diagram.create_story(story_name, epic_name, sub_epic_name, sequential_order, users, story_type, target_story_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "story_name": story_name,
                "sub_epic_name": sub_epic_name,
                "epic_name": epic_name,
                "stories_count": len(story.parent.stories),
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def update_component(
        component_name: str,
        component_type: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        new_name: Optional[str] = None,
        sequential_order: Optional[float] = None,
        epic_name: Optional[str] = None,
        sub_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Update a component's name or sequential order.
        
        Args:
            component_name: Name of the component to update
            component_type: Type of component ('epic', 'sub_epic', 'story')
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            new_name: Optional new name for the component
            sequential_order: Optional new sequential order
            epic_name: Optional epic name for feature/story search
            sub_epic_name: Optional sub-epic name for story search
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            component = diagram.update_component(component_name, component_type, new_name, sequential_order, epic_name, sub_epic_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "component_type": component_type,
                "old_name": component_name,
                "new_name": new_name or component_name,
                "sequential_order": component.sequential_order,
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def remove_component(
        component_name: str,
        component_type: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        epic_name: Optional[str] = None,
        sub_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Remove a component from the story graph or diagram.
        
        Args:
            component_name: Name of the component to remove
            component_type: Type of component ('epic', 'sub_epic', 'story')
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            epic_name: Optional epic name for feature/story search
            sub_epic_name: Optional sub-epic name for story search
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            diagram.remove_component(component_name, component_type, epic_name, sub_epic_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "component_type": component_type,
                "component_name": component_name,
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def add_user_to_story(
        story_name: str,
        user_name: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        epic_name: Optional[str] = None,
        sub_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Add a user to a story.
        
        Args:
            story_name: Name of the story
            user_name: Name of the user to add
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            epic_name: Optional epic name to narrow search
            sub_epic_name: Optional sub-epic name to narrow search
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            
            story = diagram.add_user_to_story(
                story_name=story_name,
                user_name=user_name,
                epic_name=epic_name,
                sub_epic_name=sub_epic_name
            )
            
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "story_name": story_name,
                "user_name": user_name,
                "users": story.users,
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def remove_user_from_story(
        story_name: str,
        user_name: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        epic_name: Optional[str] = None,
        sub_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Remove a user from a story.
        
        Args:
            story_name: Name of the story
            user_name: Name of the user to remove
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            epic_name: Optional epic name to narrow search
            sub_epic_name: Optional sub-epic name to narrow search
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            story = diagram.remove_user_from_story(story_name, user_name, epic_name, sub_epic_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "story_name": story_name,
                "user_name": user_name,
                "users": story.users,
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)
    
    
    @mcp.tool()
    def reorder_component(
        component_name: str,
        component_type: str,
        target_component_name: str,
        story_graph_path: Optional[str] = None,
        drawio_path: Optional[str] = None,
        epic_name: Optional[str] = None,
        sub_epic_name: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Move a component before another component (reorder).
        
        Args:
            component_name: Name of the component to move
            component_type: Type of component ('epic', 'sub_epic', 'story')
            target_component_name: Name of the component to move before
            story_graph_path: Optional path to story graph JSON file
            drawio_path: Optional path to DrawIO diagram file (takes precedence)
            epic_name: Optional epic name for feature/story search
            sub_epic_name: Optional sub-epic name for story search
            output_path: Optional path to save modified file (defaults to input file)
        
        Returns:
            JSON string with result information
        """
        try:
            if not drawio_path and not story_graph_path:
                raise ValueError("Must provide either drawio_path or story_graph_path")
            
            diagram = _load_diagram_from_path(story_graph_path, drawio_path)
            component = diagram.reorder_component(component_name, component_type, target_component_name, epic_name, sub_epic_name)
            saved_path = _save_diagram(diagram, story_graph_path, drawio_path, output_path)
            
            return json.dumps({
                "success": True,
                "component_type": component_type,
                "component_name": component_name,
                "target_name": target_component_name,
                "sequential_order": component.sequential_order,
                "output_path": saved_path
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2)


def main():
    """Main entry point for MCP server."""
    if not mcp:
        print("Error: MCP server requires mcp.server.fastmcp", file=sys.stderr)
        sys.exit(1)
    
    mcp.run()


if __name__ == "__main__":
    main()

