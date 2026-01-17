"""Extract layout data from a DrawIO file."""
import sys
from pathlib import Path

from .story_io_diagram import StoryIODiagram

def extract_layout(drawio_path: Path, output_dir: Path = None):
    """Extract layout data from DrawIO file."""
    # Resolve to absolute paths
    drawio_path = drawio_path.resolve()
    
    if output_dir is None:
        output_dir = drawio_path.parent
    else:
        output_dir = Path(output_dir).resolve()
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output path (ensure it's absolute)
    output_path = (output_dir / f"{drawio_path.stem}-extracted.json").resolve()
    
    print(f"Extracting layout from: {drawio_path}")
    print(f"Output directory: {output_dir}")
    print(f"Output path: {output_path}")
    
    # Load diagram and synchronize to extract layout
    diagram = StoryIODiagram(drawio_file=drawio_path)
    result = diagram.synchronize_outline(
        drawio_path=drawio_path.resolve(),
        output_path=output_path,
        generate_report=True
    )
    
    # Layout file is automatically created with pattern: {output_path.stem}-layout.json
    layout_path = output_path.parent.resolve() / f"{output_path.stem}-layout.json"
    
    # If layout file wasn't created, try to create it manually from the result
    if not layout_path.exists() and 'layout' in result:
        import json
        layout_path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(layout_path), 'w', encoding='utf-8') as f:
            json.dump(result['layout'], f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Layout data manually saved to: {layout_path}")
    
    if layout_path.exists():
        print(f"\n[OK] Layout data extracted to: {layout_path}")
        return layout_path
    else:
        print(f"\n[ERROR] Layout file not found at: {layout_path}")
        print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract_layout.py <drawio_file> [output_dir]")
        sys.exit(1)
    
    drawio_path = Path(sys.argv[1])
    if not drawio_path.exists():
        print(f"Error: File not found: {drawio_path}")
        sys.exit(1)
    
    output_dir = None
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    
    extract_layout(drawio_path, output_dir)

