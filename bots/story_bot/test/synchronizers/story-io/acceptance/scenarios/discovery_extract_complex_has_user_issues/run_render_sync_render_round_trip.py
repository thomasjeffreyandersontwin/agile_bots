"""
Test extract and render workflow.

Given -> When -> Then workflow:
1. Given: Original DrawIO file (source of truth)
2. When: Extract from DrawIO to JSON
3. Then: Render JSON to DrawIO and assert extracted JSON matches expected

Asserts extracted JSON matches expected JSON.
"""
import sys
import io
import json
import shutil
from pathlib import Path

# Fix encoding for Windows - ensure output is visible and unbuffered
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Set up logging to file
test_dir = Path(__file__).parent
log_file = test_dir / "test_output.log"
log_handle = open(log_file, 'w', encoding='utf-8', buffering=1)

class TeeOutput:
    """Tee output to both stdout and file."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except (ValueError, OSError):
                pass
    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except (ValueError, OSError):
                pass

sys.stdout = TeeOutput(sys.stdout, log_handle)
sys.stderr = TeeOutput(sys.stderr, log_handle)

# Add parent directories to path
scenario_dir = test_dir
acceptance_dir = scenario_dir.parent.parent
story_io_dir = acceptance_dir.parent
src_dir = story_io_dir.parent
sys.path.insert(0, str(src_dir))


def main():
    """Run extract and render workflow."""
    print(f"\n{'='*80}", flush=True)
    print("EXTRACT AND RENDER TEST", flush=True)
    print(f"{'='*80}", flush=True)
    
    given_dir = test_dir / "1_given"
    when_dir = test_dir / "2_when"
    then_dir = test_dir / "3_then"
    
    # Step 1: Given - original DrawIO (source of truth)
    print("\nGIVEN: Original DrawIO file (source of truth)...", flush=True)
    original_drawio = given_dir / "original.drawio"
    
    if not original_drawio.exists():
        print(f"   [ERROR] Original DrawIO not found: {original_drawio}", flush=True)
        return False
    
    print(f"   [OK] Original DrawIO: {original_drawio}", flush=True)
    
    # Step 2: When - Extract from DrawIO to JSON and Render JSON to DrawIO
    print("\nWHEN: Extract from DrawIO to JSON and Render...", flush=True)
    when_dir.mkdir(parents=True, exist_ok=True)
    extracted_json = when_dir / "actual-extracted.json"
    rendered_drawio = when_dir / "actual-rendered.drawio"
    
    from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_diagram import StoryIODiagram
    
    diagram = StoryIODiagram()
    diagram.synchronize_outline(
        drawio_path=original_drawio,
        output_path=extracted_json
    )
    
    print(f"   [OK] Extracted JSON: {extracted_json}", flush=True)
    
    # Render JSON to DrawIO
    print("   Rendering DrawIO from extracted JSON...", flush=True)
    with open(extracted_json, 'r', encoding='utf-8') as f:
        extracted_graph = json.load(f)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=extracted_graph,
        output_path=rendered_drawio,
        layout_data=None
    )
    
    print(f"   [OK] Rendered DrawIO: {rendered_drawio}", flush=True)
    
    # Assert extracted JSON matches expected
    expected_json = given_dir / "expected-extracted.json"
    if expected_json.exists():
        print("\nASSERT: Extracted JSON matches expected...", flush=True)
        with open(extracted_json, 'r', encoding='utf-8') as f:
            actual_data = json.load(f)
        with open(expected_json, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)
        
        if actual_data != expected_data:
            print(f"   [FAIL] Extracted JSON does not match expected!", flush=True)
            print(f"   Actual:   {extracted_json}", flush=True)
            print(f"   Expected: {expected_json}", flush=True)
            return False
        else:
            print(f"   [OK] Extracted JSON matches expected", flush=True)
    else:
        print(f"   [SKIP] Expected JSON not found: {expected_json}", flush=True)
        print(f"   [INFO] To create expected JSON, copy actual-extracted.json to expected-extracted.json", flush=True)
    
    # Step 3: Then - Move extracted JSON to then directory
    print("\nTHEN: Move extracted JSON to then directory...", flush=True)
    then_dir.mkdir(parents=True, exist_ok=True)
    
    # Move extracted JSON to then directory
    actual_json_then = then_dir / "actual-extracted.json"
    shutil.move(str(extracted_json), str(actual_json_then))
    print(f"   [OK] Moved extracted JSON to: {actual_json_then}", flush=True)
    
    # Assert against expected JSON in then directory if it exists
    assertion_passed = True
    expected_json_then = then_dir / "expected.json"
    if expected_json_then.exists():
        print("\nASSERT: Extracted JSON in then matches expected...", flush=True)
        with open(actual_json_then, 'r', encoding='utf-8') as f:
            actual_data = json.load(f)
        with open(expected_json_then, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)
        
        if actual_data != expected_data:
            print(f"   [FAIL] Extracted JSON does not match expected!", flush=True)
            print(f"   Actual:   {actual_json_then}", flush=True)
            print(f"   Expected: {expected_json_then}", flush=True)
            assertion_passed = False
        else:
            print(f"   [OK] Extracted JSON matches expected", flush=True)
    
    # Render JSON to DrawIO (but don't assert against expected)
    # Always render, even if assertion failed
    print("\nRendering DrawIO from extracted JSON...", flush=True)
    rendered_drawio = then_dir / "actual-rendered.drawio"
    
    with open(actual_json_then, 'r', encoding='utf-8') as f:
        extracted_graph = json.load(f)
    
    StoryIODiagram.render_outline_from_graph(
        story_graph=extracted_graph,
        output_path=rendered_drawio,
        layout_data=None
    )
    
    print(f"   [OK] Rendered DrawIO: {rendered_drawio}", flush=True)
    
    print(f"\n{'='*80}", flush=True)
    if assertion_passed:
        print("Test completed successfully!", flush=True)
    else:
        print("Test completed with assertion failure (rendering still executed)", flush=True)
    print(f"  Original DrawIO:  {original_drawio}", flush=True)
    print(f"  Extracted JSON (then): {actual_json_then}", flush=True)
    print(f"  Rendered DrawIO:  {rendered_drawio}", flush=True)
    print(f"{'='*80}", flush=True)
    
    return assertion_passed

if __name__ == '__main__':
    success = False
    try:
        success = main()
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        success = False
    finally:
        try:
            if 'log_handle' in globals() and log_handle:
                log_handle.close()
        except Exception:
            pass
    sys.exit(0 if success else 1)
