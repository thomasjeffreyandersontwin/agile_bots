
import sys
import os
import json
import io
from pathlib import Path

# Configure Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Setup paths before importing agile_bot modules
script_path = Path(__file__).resolve()
workspace_root = script_path.parent.parent.parent.parent

if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

if 'BOT_DIRECTORY' in os.environ:
    bot_directory = Path(os.environ['BOT_DIRECTORY'])
else:
    bot_directory = workspace_root / 'agile_bots' / 'bots' / 'story_bot'
os.environ['BOT_DIRECTORY'] = str(bot_directory)

if 'WORKING_AREA' not in os.environ:
    config_path = bot_directory / 'bot_config.json'
    if config_path.exists():
        try:
            bot_config = json.loads(config_path.read_text(encoding='utf-8'))
            if 'WORKING_AREA' in bot_config:
                os.environ['WORKING_AREA'] = bot_config['WORKING_AREA']
            elif 'mcp' in bot_config and 'env' in bot_config['mcp']:
                mcp_env = bot_config['mcp']['env']
                if 'WORKING_AREA' in mcp_env:
                    os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']
        except:
            pass
    
    if 'WORKING_AREA' not in os.environ:
        os.environ['WORKING_AREA'] = str(workspace_root)

# import agile_bots modules after environment setup
from agile_bots.src.bot.bot import Bot
from agile_bots.src.bot.workspace import get_workspace_directory
from agile_bots.src.cli.cli_session import CLISession

def main():
    bot_name = bot_directory.name
    workspace_directory = get_workspace_directory()
    bot_config_path = bot_directory / 'bot_config.json'
    
    if not bot_config_path.exists():
        print(f"ERROR: Bot config not found at {bot_config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        bot = Bot(
            bot_name=bot_name,
            bot_directory=bot_directory,
            config_path=bot_config_path
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
        cli_script_str = "python -m agile_bot.src.cli.cli_main"
        print(f"# Interactive mode (environment set automatically by script):")
        print(cli_script_str)
        print("")
        print(f"# Piped mode (each command is a new process - script sets env vars automatically):")
        print(f"echo '<command>' | {cli_script_str}")
        print("")
        print("# Optional: Override environment variables if needed:")
        print(f"$env:PYTHONPATH = '{workspace_root_str}'")
        print(f"$env:BOT_DIRECTORY = '{bot_directory}'")
        print("$env:WORKING_AREA = '<project_path>'  # e.g. demo\\mob_minion")
        print("```")
        print("")
    
    if json_mode:
        try:
            for line in sys.stdin:
                command = line.strip()
                if command:
                    response = cli_session.execute_command(command)
                    print(response.output, flush=True)
        except (KeyboardInterrupt, EOFError):
            pass
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
