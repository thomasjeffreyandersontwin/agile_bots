from pathlib import Path
import runpy
import sys

# This wrapper exists so the VS Code extension can find a CLI at
# c:\dev\agile_bots\agile_bot\src\cli\cli_main.py while the
# actual CLI lives at c:\dev\agile_bots\src\cli\cli_main.py

this = Path(__file__).resolve()

# Search upward from this file for a parent that contains src/cli/cli_main.py
original = None
for parent in this.parents:
    candidate = parent / 'src' / 'cli' / 'cli_main.py'
    if not candidate.exists():
        continue
    try:
        if candidate.resolve() == this:
            # skip the wrapper file itself
            continue
    except Exception:
        pass
    original = candidate
    break

if original is None:
    # Fallback: try the workspace assumed four levels up (legacy layout)
    try:
        legacy = this.parents[4] / 'src' / 'cli' / 'cli_main.py'
    except Exception:
        legacy = None
    if legacy and legacy.exists():
        original = legacy

if original is None or not original.exists():
    print(f"ERROR: Could not locate original CLI script (searched parents) ", file=sys.stderr)
    print(f"Searched from: {this}", file=sys.stderr)
    sys.exit(1)

# Run the real CLI as __main__ so behavior matches running the original script
runpy.run_path(str(original), run_name='__main__')
