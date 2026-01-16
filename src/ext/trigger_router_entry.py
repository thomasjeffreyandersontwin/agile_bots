import json
import sys
from pathlib import Path
from agile_bots.src.ext.trigger_router import TriggerRouter
from agile_bots.src.bot.workspace import get_bot_directory, get_workspace_directory
_here = Path(__file__).resolve()
_workspace_root = None
for anc in _here.parents:
    if anc.name == 'agile_bots':
        _workspace_root = anc.parent
        break
if _workspace_root and str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

def main() -> None:
    message = sys.argv[1] if len(sys.argv) > 1 else ''
    current_behavior = sys.argv[2] if len(sys.argv) > 2 else None
    current_action = sys.argv[3] if len(sys.argv) > 3 else None
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()
    router = TriggerRouter(bot_directory=bot_directory, workspace_path=workspace_directory)
    route = router.match_trigger(message=message.lower(), current_behavior=current_behavior, current_action=current_action)
    print(json.dumps(route or {}))
if __name__ == '__main__':
    main()
