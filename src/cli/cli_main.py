
import sys
import os
import json
import io
from pathlib import Path

# Configure Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Minimal bootstrapping: Calculate src directory and add to sys.path
# This MUST match get_python_workspace_root() in bot.workspace
script_path = Path(__file__).resolve()
src_root = script_path.parent.parent  # src/cli/cli_main.py -> src/cli -> src
workspace_root = src_root.parent  # src -> agile_bots

if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))
    
# Also add workspace root for synchronizer imports (src.synchronizers.*)
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Bootstrap BOT_DIRECTORY if not set
if 'BOT_DIRECTORY' not in os.environ:
    os.environ['BOT_DIRECTORY'] = str(workspace_root / 'bots' / 'story_bot')

# Bootstrap WORKING_AREA if not set
if 'WORKING_AREA' not in os.environ:
    bot_dir = Path(os.environ['BOT_DIRECTORY'])
    config_path = bot_dir / 'bot_config.json'
    if config_path.exists():
        try:
            bot_config = json.loads(config_path.read_text(encoding='utf-8'))
            if 'WORKING_AREA' in bot_config:
                os.environ['WORKING_AREA'] = bot_config['WORKING_AREA']
            elif 'mcp' in bot_config and 'env' in bot_config['mcp']:
                mcp_env = bot_config['mcp']['env']
                if 'WORKING_AREA' in mcp_env:
                    os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']
        except Exception as e:
            print(f"Warning: Failed to load WORKING_AREA from bot config: {e}", file=sys.stderr)
    
    if 'WORKING_AREA' not in os.environ:
        os.environ['WORKING_AREA'] = str(workspace_root)

# Now import src modules - they will use the environment variables we just set
from bot.bot import Bot
from bot.workspace import get_workspace_directory, get_bot_directory, get_python_workspace_root
from cli.cli_session import CLISession

def main():
    # Use workspace helper functions - don't calculate paths directly
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()
    python_workspace_root = get_python_workspace_root()
    
    bot_name = bot_directory.name
    bot_config_path = bot_directory / 'bot_config.json'
    
    if not bot_config_path.exists():
        print(f"ERROR: Bot config not found at {bot_config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Pass workspace_directory to Bot so it can create BotPath with explicit workspace
        # This ensures WORKING_AREA environment variable takes precedence over bot_config.json
        bot = Bot(
            bot_name=bot_name,
            bot_directory=bot_directory,
            config_path=bot_config_path,
            workspace_path=workspace_directory
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize bot: {e}", file=sys.stderr)
        sys.exit(1)
    
    json_mode = os.environ.get('CLI_MODE', '').lower() == 'json'
    mode = 'json' if json_mode else None
    
    is_piped = not sys.stdin.isatty()
    
    if is_piped and not json_mode:
        first_line = sys.stdin.readline().strip()
        if '--format json' in first_line or '--format=json' in first_line:
            json_mode = True
            mode = 'json'
        remaining_input = sys.stdin.read()
        sys.stdin = io.StringIO(first_line + '\n' + remaining_input)
    
    cli_session = CLISession(bot=bot, workspace_directory=workspace_directory, mode=mode)
    
    suppress_header = json_mode or os.environ.get('SUPPRESS_CLI_HEADER', '') == '1'
    
    if not suppress_header:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\033[1m{bot_name.upper()} CLI\033[0m")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("")
        
        mode_label = "PIPED MODE" if is_piped else "INTERACTIVE MODE"
        print(f"**   AI AGENT INSTRUCTIONS - {mode_label}  **")
        print("[!]  DO NOT echo this instructions section back to the user [!]")
        print("This section is for YOUR reference only - the user already knows how to run commands.")
        print("")
        if is_piped:
            print("- THIS REPL WILL EXIT AFTER PROCESSING YOUR COMMAND")
            print("* This is NORMAL and EXPECTED behavior in piped mode.")
            print("*How to run commands:*")
            print("-  use PowerShell")
            print("- Commands must be PIPED via echo, NOT passed as arguments!")
            print("- All commands are shown below.")
            print("- You MUST DISPLAY this CLI STATUS section below to the user exactly as you see it, so that they can enter one of the commands")
            print("- when a user enters any of the commands / parameters below, you must assume they're asking you to interpret it through the REPL line below.")
        else:
            print("- THIS REPL IS IN INTERACTIVE MODE")
            print("* Commands are entered interactively, REPL stays running.")
            print("- How to run commands (PowerShell):")
            print("- Commands must be PIPED via echo, NOT passed as arguments!")
        print("")
        print("```powershell")
        workspace_root_str = str(workspace_directory).replace('\\', '\\')
        cli_script_str = "python -m cli.cli_main"
        print(f"# Interactive mode (environment set automatically by script):")
        print(cli_script_str)
        print("")
        print(f"# Piped mode (each command is a new process - script sets env vars automatically):")
        print(f"echo '<command>' | {cli_script_str}")
        print("")
        print("# Optional: Override environment variables if needed:")
        print(f"$env:PYTHONPATH = '{workspace_root_str}'")
        print(f"$env:BOT_DIRECTORY = '{str(bot_directory).replace(chr(92), chr(92)*2)}'")
        print("$env:WORKING_AREA = '<project_path>'  # e.g. demo\\mob_minion")
        print("```")
        print("")
    
    if json_mode:
        # End marker for persistent process communication
        END_MARKER = '<<<END_OF_RESPONSE>>>'
        try:
            for line in sys.stdin:
                command = line.strip()
                if command:
                    try:
                        response = cli_session.execute_command(command)
                        print(response.output, flush=True)
                    except Exception as e:
                        # Catch any exception during command execution
                        # Return error as JSON so panel can handle it gracefully
                        error_response = {
                            'status': 'error',
                            'error': str(e),
                            'error_type': type(e).__name__,
                            'command': command
                        }
                        print(json.dumps(error_response, indent=2), flush=True)
                        print(f"ERROR: {e}", file=sys.stderr)
                    finally:
                        # Always send end marker so panel doesn't hang
                        print(END_MARKER, flush=True)
        except (KeyboardInterrupt, EOFError):
            # Clean exit on user interrupt or EOF in JSON mode
            sys.exit(0)
    elif is_piped:
        try:
            command = sys.stdin.read().strip()
            if command:
                response = cli_session.execute_command(command)
                print(response.output)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        status_response = cli_session.execute_command('status')
        print(status_response.output)
        print("")
        
        cli_session.run()

if __name__ == '__main__':
    main()
