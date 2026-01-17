"""
CLI Interface for Story IO Operations

Command-line interface for rendering, synchronizing, and manipulating story maps.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .story_io_diagram import StoryIODiagram


def render_outline_command(args):
    """Render story graph as outline DrawIO diagram."""
    if args.story_graph:
        diagram = StoryIODiagram.load_from_story_graph(args.story_graph, args.drawio_file)
    elif args.json:
        diagram = _load_from_json(args.json)
    else:
        print("Error: Must provide --story-graph or --json", file=sys.stderr)
        return 1
    
    layout_data = None
    if args.layout:
        with open(args.layout, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
    else:
        # Default: try to find layout file automatically
        output_path = Path(args.output)
        # Try multiple layout file naming patterns
        layout_candidates = [
            output_path.parent / f"{output_path.stem}-layout.json",
            output_path.parent / "story-graph-drawio-extracted-layout.json",
            output_path.parent / f"{output_path.stem}-drawio-extracted-layout.json"
        ]
        for layout_path in layout_candidates:
            if layout_path.exists():
                with open(layout_path, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                print(f"Using layout file: {layout_path}")
                break
    
    force_outline = hasattr(args, 'force_outline') and args.force_outline
    result = diagram.render_outline(output_path=args.output, layout_data=layout_data, force_outline=force_outline)
    print(f"Generated DrawIO diagram: {result['output_path']}")
    print(f"Epics: {result['summary']['epics']}")
    return 0


def render_increments_command(args):
    """Render story graph with increments as DrawIO diagram."""
    if args.story_graph:
        diagram = StoryIODiagram.load_from_story_graph(args.story_graph, args.drawio_file)
    elif args.json:
        diagram = _load_from_json(args.json)
    else:
        print("Error: Must provide --story-graph or --json", file=sys.stderr)
        return 1
    
    layout_data = None
    if args.layout:
        with open(args.layout, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
    
    result = diagram.render_increments(output_path=args.output, layout_data=layout_data)
    print(f"Generated DrawIO diagram: {result['output_path']}")
    print(f"Epics: {result['summary']['epics']}")
    if 'increments' in result['summary']:
        print(f"Increments: {result['summary']['increments']}")
    return 0


def synchronize_outline_command(args):
    """Synchronize story graph from DrawIO outline file."""
    diagram = StoryIODiagram(drawio_file=args.drawio_file)
    
    original_path = None
    if args.original:
        original_path = Path(args.original)
    
    generate_report = getattr(args, 'generate_report', False)
    report_path = getattr(args, 'report', None)
    
    result = diagram.synchronize_outline(
        drawio_path=args.drawio_file,
        original_path=original_path,
        generate_report=generate_report
    )
    
    if args.output:
        diagram.save_story_graph(args.output)
        print(f"Saved story graph to: {args.output}")
    else:
        print("Synchronized story graph (use --output to save)")
    
    if generate_report and report_path:
        report = result.get('sync_report', {})
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Synchronization report saved to: {report_path}")
    
    return 0


def synchronize_increments_command(args):
    """Synchronize story graph from DrawIO increments file."""
    diagram = StoryIODiagram(drawio_file=args.drawio_file)
    
    original_path = None
    if args.original:
        original_path = Path(args.original)
    
    generate_report = getattr(args, 'generate_report', False)
    report_path = getattr(args, 'report', None)
    
    result = diagram.synchronize_increments(
        drawio_path=args.drawio_file,
        original_path=original_path,
        output_path=args.output if args.output else None,
        generate_report=generate_report
    )
    
    # Note: synchronize_increments already writes the file via output_path parameter
    # Don't call save_story_graph() as it would overwrite with incorrect structure
    if not args.output:
        print("Synchronized story graph (use --output to save)")
    
    if generate_report and report_path:
        report = result.get('sync_report', {})
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Synchronization report saved to: {report_path}")
    
    return 0


def synchronize_command(args):
    """Synchronize story graph from DrawIO file (auto-detects outline or increments)."""
    drawio_path = Path(args.drawio_file)
    
    if not drawio_path.exists():
        print(f"Error: DrawIO file not found: {drawio_path}", file=sys.stderr)
        return 1
    
    # Auto-detect type based on filename or file content
    auto_detect = args.type == 'auto' or args.type is None
    
    if auto_detect:
        # Check filename for hints
        filename = drawio_path.name.lower()
        if 'increment' in filename:
            sync_type = 'increments'
        elif 'outline' in filename:
            sync_type = 'outline'
        else:
            # Default to outline
            sync_type = 'outline'
            print(f"Auto-detected sync type: outline (based on filename)")
    else:
        sync_type = args.type
    
    diagram = StoryIODiagram(drawio_file=args.drawio_file)
    
    original_path = None
    if args.original:
        original_path = Path(args.original)
        if not original_path.exists():
            print(f"Warning: Original file not found: {original_path}", file=sys.stderr)
    
    generate_report = args.generate_report
    report_path = args.report
    
    # Perform synchronization
    if sync_type == 'increments':
        print(f"Synchronizing from increments DrawIO file...")
        result = diagram.synchronize_increments(
            drawio_path=drawio_path,
            original_path=original_path,
            generate_report=generate_report
        )
    else:
        print(f"Synchronizing from outline DrawIO file...")
        result = diagram.synchronize_outline(
            drawio_path=drawio_path,
            original_path=original_path,
            generate_report=generate_report
        )
    
    # Save synchronized story graph
    if args.output:
        diagram.save_story_graph(args.output)
        print(f"Saved story graph to: {args.output}")
    else:
        print("Synchronized story graph (use --output to save)")
    
    # Save report if requested
    if generate_report:
        if report_path:
            report = result.get('sync_report', {})
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Synchronization report saved to: {report_path}")
        else:
            report = result.get('sync_report', {})
            if report:
                print("\nSynchronization Report:")
                print(f"  Epics: {report.get('epics_count', 0)}")
                print(f"  Sub-Epics: {report.get('sub_epics_count', 0)}")
                print(f"  Stories: {report.get('stories_count', 0)}")
    
    return 0


def search_command(args):
    """Search for components in story graph."""
    if args.story_graph:
        diagram = StoryIODiagram.load_from_story_graph(args.story_graph)
    elif args.json:
        diagram = _load_from_json(args.json)
    else:
        print("Error: Must provide --story-graph or --json", file=sys.stderr)
        return 1
    
    results = []
    if args.type == 'any' or args.type is None:
        results = diagram.search_for_any(args.query)
    elif args.type == 'epic':
        results = diagram.search_for_epics(args.query)
    elif args.type == 'sub_epic':
        results = diagram.search_for_sub_epics(args.query)
    elif args.type == 'story':
        results = diagram.search_for_stories(args.query)
    
    for result in results:
        print(f"{result.__class__.__name__}: {result.name}")
        if hasattr(result, 'sequential_order') and result.sequential_order:
            print(f"  Order: {result.sequential_order}")
    
    return 0


def add_user_command(args):
    """Add user to story or all stories."""
    # Load diagram
    if args.story_graph:
        diagram = StoryIODiagram.load_from_story_graph(args.story_graph)
    elif args.drawio_file:
        diagram = StoryIODiagram.sync_from_drawio(args.drawio_file)
    else:
        print("Error: Must provide --story-graph or --drawio-file", file=sys.stderr)
        return 1
    
    # Add user to specific story or all stories
    if args.story_name:
        # Add to specific story
        try:
            story = diagram.add_user_to_story(
                story_name=args.story_name,
                user_name=args.user_name,
                epic_name=args.epic_name,
                sub_epic_name=args.sub_epic_name
            )
            print(f"Added user '{args.user_name}' to story: {story.name}")
            print(f"Story users: {story.users}")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        # Add to all stories
        stories_modified = []
        for epic in diagram.epics:
            for sub_epic in epic.sub_epics:
                for story in sub_epic.stories:
                    if args.user_name not in story.users:
                        story.add_user(args.user_name)
                        stories_modified.append(story.name)
        
        print(f"Added user '{args.user_name}' to {len(stories_modified)} stories")
        if stories_modified:
            preview = ', '.join(stories_modified[:10])
            if len(stories_modified) > 10:
                preview += f' ... and {len(stories_modified) - 10} more'
            print(f"Modified stories: {preview}")
    
    # Render output if requested
    if args.output:
        result = diagram.render_outline(output_path=args.output)
        print(f"Rendered to: {result['output_path']}")
    
    return 0


def merge_command(args):
    """Merge extracted story graph with original."""
    if not args.extracted or not args.extracted.exists():
        print(f"Error: Extracted file not found: {args.extracted}", file=sys.stderr)
        return 1
    
    if not args.original or not args.original.exists():
        print(f"Error: Original file not found: {args.original}", file=sys.stderr)
        return 1
    
    diagram = StoryIODiagram.load_from_story_graph(args.original)
    
    # Generate merge report
    report = diagram.generate_merge_report(
        extracted_path=args.extracted,
        original_path=args.original
    )
    
    # Save report if requested
    if args.report_path:
        with open(args.report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Merge report saved to: {args.report_path}")
    
    # Perform merge (use report_path if provided, otherwise use generated report)
    report_path_for_merge = args.report_path if args.report_path else Path(args.output).parent / f"{Path(args.extracted).stem}-merge-report.json"
    merged = diagram.merge_story_graphs(
        extracted_path=args.extracted,
        original_path=args.original,
        report_path=report_path_for_merge,
        output_path=args.output
    )
    
    print(f"Merged story graph saved to: {args.output}")
    return 0


def render_discovery_command(args):
    """
    Render discovery increment(s) DrawIO diagram.
    """
    if args.story_graph:
        diagram = StoryIODiagram.load_from_story_graph(args.story_graph, None)
    else:
        print("Error: Must provide --story-graph", file=sys.stderr)
        return 1
    
    layout_data = None
    if args.layout:
        with open(args.layout, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
    
    increment_names = args.increment_names if args.increment_names else None
    
    result = diagram.render_discovery(
        output_path=args.output,
        layout_data=layout_data,
        increment_names=increment_names
    )
    print(f"Generated DrawIO diagram: {result['output_path']}")
    print(f"Epics: {result['summary']['epics']}")
    print(f"Increments: {result['summary']['increments']}")
    return 0


def sync_discovery_command(args):
    """
    Synchronize discovery increment(s) from DrawIO.
    
    Placeholder - implementation to be added.
    """
    print("Error: sync-discovery command not yet implemented", file=sys.stderr)
    print(f"  DrawIO file: {args.drawio_file}")
    print(f"  Original: {args.original}")
    print(f"  Output: {args.output}")
    print(f"  Increment names: {args.increment_names}")
    return 1


def render_exploration_command(args):
    """Render exploration acceptance criteria DrawIO diagram."""
    story_graph_data = None
    if args.story_graph:
        # Load story graph to pass to render_exploration for proper filtering
        with open(args.story_graph, 'r', encoding='utf-8') as f:
            story_graph_data = json.load(f)
        diagram = StoryIODiagram.load_from_story_graph(args.story_graph, None)
    elif args.json:
        diagram = _load_from_json(args.json)
    else:
        print("Error: Must provide --story-graph or --json", file=sys.stderr)
        return 1
    
    layout_data = None
    if args.layout:
        with open(args.layout, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
    
    # Pass story_graph_data to render_exploration so filtering can work properly
    result = diagram.render_exploration(
        output_path=args.output, 
        layout_data=layout_data, 
        scope=args.scope,
        story_graph=story_graph_data
    )
    print(f"Generated DrawIO diagram: {result['output_path']}")
    print(f"Epics: {result['summary']['epics']}")
    return 0


def sync_exploration_command(args):
    """
    Synchronize exploration acceptance criteria from DrawIO.
    
    Placeholder - implementation to be added.
    """
    print("Error: sync-exploration command not yet implemented", file=sys.stderr)
    print(f"  DrawIO file: {args.drawio_file}")
    print(f"  Original: {args.original}")
    print(f"  Output: {args.output}")
    print(f"  Scope: {args.scope}")
    return 1


def _load_from_json(json_path: Path) -> StoryIODiagram:
    """Load diagram from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    diagram = StoryIODiagram()
    diagram._load_from_story_graph_format(data)
    return diagram


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Story IO CLI - Manage story maps')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Render outline command
    render_outline_parser = subparsers.add_parser('render-outline', help='Render outline diagram')
    render_outline_parser.add_argument('--story-graph', type=Path, help='Story graph JSON file')
    render_outline_parser.add_argument('--json', type=Path, help='Story graph JSON file (alias)')
    render_outline_parser.add_argument('--drawio-file', type=Path, help='DrawIO file path')
    render_outline_parser.add_argument('--output', type=Path, required=True, help='Output DrawIO file')
    render_outline_parser.add_argument('--layout', type=Path, help='Layout JSON file (default: auto-detect from output filename)')
    render_outline_parser.add_argument('--force-outline', action='store_true', help='Force outline mode (disable auto-exploration mode)')
    
    # Render increments command
    render_inc_parser = subparsers.add_parser('render-increments', help='Render increments diagram')
    render_inc_parser.add_argument('--story-graph', type=Path, help='Story graph JSON file')
    render_inc_parser.add_argument('--json', type=Path, help='Story graph JSON file (alias)')
    render_inc_parser.add_argument('--drawio-file', type=Path, help='DrawIO file path')
    render_inc_parser.add_argument('--output', type=Path, required=True, help='Output DrawIO file')
    render_inc_parser.add_argument('--layout', type=Path, help='Layout JSON file')
    
    # Synchronize command (unified, auto-detects type)
    sync_parser = subparsers.add_parser('synchronize', aliases=['sync'], 
                                       help='Synchronize from DrawIO file (auto-detects outline/increments)')
    sync_parser.add_argument('--drawio-file', type=Path, required=True, help='DrawIO file path')
    sync_parser.add_argument('--type', choices=['auto', 'outline', 'increments'], default='auto',
                            help='Sync type: auto (detect from filename), outline, or increments')
    sync_parser.add_argument('--original', type=Path, help='Original story graph for comparison')
    sync_parser.add_argument('--output', type=Path, help='Output story graph JSON file')
    sync_parser.add_argument('--generate-report', action='store_true', 
                            help='Generate synchronization report')
    sync_parser.add_argument('--report', type=Path, 
                            help='Path to save synchronization report (requires --generate-report)')
    
    # Synchronize outline command
    sync_outline_parser = subparsers.add_parser('sync-outline', help='Synchronize from outline DrawIO')
    sync_outline_parser.add_argument('--drawio-file', type=Path, required=True, help='DrawIO file path')
    sync_outline_parser.add_argument('--original', type=Path, help='Original story graph for comparison')
    sync_outline_parser.add_argument('--output', type=Path, help='Output story graph JSON file')
    sync_outline_parser.add_argument('--generate-report', action='store_true', 
                                    help='Generate synchronization report')
    sync_outline_parser.add_argument('--report', type=Path, 
                                    help='Path to save synchronization report (requires --generate-report)')
    
    # Synchronize increments command
    sync_inc_parser = subparsers.add_parser('sync-increments', help='Synchronize from increments DrawIO')
    sync_inc_parser.add_argument('--drawio-file', type=Path, required=True, help='DrawIO file path')
    sync_inc_parser.add_argument('--original', type=Path, help='Original story graph for comparison')
    sync_inc_parser.add_argument('--output', type=Path, help='Output story graph JSON file')
    sync_inc_parser.add_argument('--generate-report', action='store_true', 
                                help='Generate synchronization report')
    sync_inc_parser.add_argument('--report', type=Path, 
                                help='Path to save synchronization report (requires --generate-report)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for components')
    search_parser.add_argument('--story-graph', type=Path, help='Story graph JSON file')
    search_parser.add_argument('--json', type=Path, help='Story graph JSON file (alias)')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--type', choices=['any', 'epic', 'sub_epic', 'story'], 
                              help='Component type to search for')
    
    # Add user command
    add_user_parser = subparsers.add_parser('add-user', help='Add user to story')
    add_user_parser.add_argument('--user-name', required=True, help='User name to add')
    add_user_parser.add_argument('--story-name', help='Story name (optional - if omitted, adds to all stories)')
    add_user_parser.add_argument('--story-graph', type=Path, help='Story graph JSON file')
    add_user_parser.add_argument('--drawio-file', type=Path, help='DrawIO file to load from')
    add_user_parser.add_argument('--epic-name', help='Epic name (optional - to narrow story search)')
    add_user_parser.add_argument('--sub-epic-name', help='Sub-epic name (optional - to narrow story search)')
    add_user_parser.add_argument('--output', type=Path, help='Output DrawIO file (optional - renders result)')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge extracted story graph with original')
    merge_parser.add_argument('--extracted', type=Path, required=True, help='Extracted story graph JSON file')
    merge_parser.add_argument('--original', type=Path, required=True, help='Original story graph JSON file')
    merge_parser.add_argument('--output', type=Path, required=True, help='Output merged story graph JSON file')
    merge_parser.add_argument('--report-path', type=Path, help='Path to save merge report')
    
    # Render discovery increments command (placeholder)
    render_discovery_parser = subparsers.add_parser('render-discovery', help='Render discovery increment(s) DrawIO diagram')
    render_discovery_parser.add_argument('--story-graph', type=Path, help='Story graph JSON file')
    render_discovery_parser.add_argument('--output', type=Path, required=True, help='Output DrawIO file path')
    render_discovery_parser.add_argument('--increment-names', nargs='+', help='Increment name(s) to render')
    render_discovery_parser.add_argument('--layout', type=Path, help='Layout JSON file to preserve positions')
    
    # Synchronize discovery increments command (placeholder)
    sync_discovery_parser = subparsers.add_parser('sync-discovery', help='Synchronize discovery increment(s) from DrawIO')
    sync_discovery_parser.add_argument('--drawio-file', type=Path, required=True, help='DrawIO file path')
    sync_discovery_parser.add_argument('--original', type=Path, help='Original story graph for comparison')
    sync_discovery_parser.add_argument('--output', type=Path, help='Output story graph JSON file')
    sync_discovery_parser.add_argument('--increment-names', nargs='+', help='Increment name(s) to synchronize')
    sync_discovery_parser.add_argument('--generate-report', action='store_true', help='Generate synchronization report')
    sync_discovery_parser.add_argument('--report', type=Path, help='Path to save synchronization report')
    
    # Render exploration acceptance criteria command (placeholder)
    render_exploration_parser = subparsers.add_parser('render-exploration', help='Render exploration acceptance criteria DrawIO diagram')
    render_exploration_parser.add_argument('--story-graph', type=Path, help='Story graph JSON file')
    render_exploration_parser.add_argument('--output', type=Path, required=True, help='Output DrawIO file path')
    render_exploration_parser.add_argument('--scope', required=True, help='Scope identifier for acceptance criteria')
    render_exploration_parser.add_argument('--layout', type=Path, help='Layout JSON file to preserve positions')
    
    # Synchronize exploration acceptance criteria command (placeholder)
    sync_exploration_parser = subparsers.add_parser('sync-exploration', help='Synchronize exploration acceptance criteria from DrawIO')
    sync_exploration_parser.add_argument('--drawio-file', type=Path, required=True, help='DrawIO file path')
    sync_exploration_parser.add_argument('--original', type=Path, help='Original story graph for comparison')
    sync_exploration_parser.add_argument('--output', type=Path, help='Output story graph JSON file')
    sync_exploration_parser.add_argument('--scope', required=True, help='Scope identifier for acceptance criteria')
    sync_exploration_parser.add_argument('--generate-report', action='store_true', help='Generate synchronization report')
    sync_exploration_parser.add_argument('--report', type=Path, help='Path to save synchronization report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    command_handlers = {
        'render-outline': render_outline_command,
        'render-increments': render_increments_command,
        'synchronize': synchronize_command,
        'sync': synchronize_command,  # Alias
        'sync-outline': synchronize_outline_command,
        'sync-increments': synchronize_increments_command,
        'search': search_command,
        'add-user': add_user_command,
        'merge': merge_command,
        'render-discovery': render_discovery_command,
        'sync-discovery': sync_discovery_command,
        'render-exploration': render_exploration_command,
        'sync-exploration': sync_exploration_command,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

