from pathlib import Path
from typing import Dict

class CliGenerator:
    
    def __init__(self, workspace_root: Path, bot_location: str):
        self.workspace_root = Path(workspace_root)
        self.bot_location = Path(bot_location)
        self.bot_name = self.bot_location.name
    
    def generate_cli_code(self) -> Dict[str, str]:
        results = {}
        
        shell_script_path = self._create_shell_script()
        results['cli_script'] = str(shell_script_path)
        
        powershell_script_path = self._create_powershell_script()
        results['cli_powershell'] = str(powershell_script_path)
        
        results['cli_python'] = 'agile_bot.src.cli.cli_main'
        
        return results
    
    def _create_shell_script(self) -> Path:
        script_name = 'story_cli.sh' if self.bot_name == 'story_bot' else f'{self.bot_name}_cli.sh'
        script_file = self.workspace_root / 'agile_bots' / script_name
        
        script_content = f"""#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export PYTHONPATH="$WORKSPACE_ROOT"
export BOT_DIRECTORY="$WORKSPACE_ROOT/{self.bot_location}"

python -m agile_bot.src.cli.cli_main
"""
        script_file.write_text(script_content, encoding='utf-8')
        script_file.chmod(0o755)
        
        return script_file
    
    def _create_powershell_script(self) -> Path:
        script_name = 'story_cli.ps1' if self.bot_name == 'story_bot' else f'{self.bot_name}_cli.ps1'
        script_file = self.workspace_root / 'agile_bots' / script_name
        
        script_content = f"""# {self.bot_name.replace('_', ' ').title()} CLI Launcher (Windows/PowerShell)

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$WORKSPACE_ROOT = Split-Path -Parent $SCRIPT_DIR

$env:PYTHONPATH = $WORKSPACE_ROOT
$env:BOT_DIRECTORY = Join-Path $WORKSPACE_ROOT "{self.bot_location}"

python -m agile_bot.src.cli.cli_main
"""
        script_file.write_text(script_content, encoding='utf-8')
        
        return script_file
