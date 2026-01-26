/**
 * Base class for all panel views.
 * Provides CLI command execution via a persistent Python process.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const vscode = require("vscode");

/**
 * Check if a path is a temp directory
 */
function isTempPath(filePath) {
    if (!filePath) return false;
    const normalized = path.resolve(filePath);
    const tempDir = os.tmpdir();
    return normalized.startsWith(tempDir);
}

/**
 * Check if a path is the production repo root
 * This is used to prevent tests from accidentally using production paths
 */
function isProductionRepoPath(filePath) {
    if (!filePath) return false;
    const normalized = path.resolve(filePath);
    // Check if it's the repo root by looking for src/ and test/ directories
    return fs.existsSync(path.join(normalized, 'src')) && 
           fs.existsSync(path.join(normalized, 'test')) &&
           fs.existsSync(path.join(normalized, 'bots'));
}

// End-of-response marker that Python CLI sends after each JSON response
const END_MARKER = '<<<END_OF_RESPONSE>>>';

class PanelView {
    /**
     * Static logging method for panel views
     * @param {string} message - Message to log
     */
    static _log(message) {
        console.log(message);
    }
    
    /**
     * Create a PanelView.
     * @param {string|PanelView} botPathOrCli - Full path to bot directory, or CLI instance to reuse
     */
    constructor(botPathOrCli) {
        if (botPathOrCli && typeof botPathOrCli === 'object') {
            // CLI instance passed - reuse it
            this._cli = botPathOrCli;
            this._botPath = null;
            this._workspaceDir = null;
            this._pythonProcess = null;
        } else {
            // Bot path passed - create own CLI
            this._cli = null;
            this._botPath = botPathOrCli || process.env.BOT_DIRECTORY;
            // Derive workspace from bot path (bot is at workspace/bots/botname)
            const path = require('path');
            this._workspaceDir = path.resolve(this._botPath, '..', '..');
            this._pythonProcess = null;
        }
        this._pendingResolve = null;
        this._pendingReject = null;
        this._responseBuffer = '';
    }
    
    /**
     * Spawn the persistent Python CLI process
     */
    _spawnProcess() {
        if (this._pythonProcess) {
            return;
        }
        
        const cliPath = path.join(this._workspaceDir, 'src', 'cli', 'cli_main.py');
        
        if (!fs.existsSync(cliPath)) {
            throw new Error(`CLI script not found at: ${cliPath}`);
        }
        
        // PYTHONPATH must point to agile_bots src/test directories
        // _workspaceDir is the agile_bots root (derived from bot path)
        const srcDir = path.join(this._workspaceDir, 'src');
        const testDir = path.join(this._workspaceDir, 'test');
        const pythonPath = `${srcDir}${path.delimiter}${testDir}${path.delimiter}${this._workspaceDir}`;
        
        // Respect WORKING_AREA if already set, UNLESS it's the production repo root
        // This allows:
        // - Tests to use temp directories (safe)
        // - Users to set custom working areas via UI commands (workspace command)
        // - Prevents accidental use of production repo root in tests
        const envWorkingArea = process.env.WORKING_AREA;
        const workingArea = (envWorkingArea && !isProductionRepoPath(envWorkingArea))
            ? envWorkingArea 
            : this._workspaceDir;
        
        const env = {
            ...process.env,
            PYTHONPATH: pythonPath,
            BOT_DIRECTORY: this._botPath,
            WORKING_AREA: workingArea,
            CLI_MODE: 'json',
            SUPPRESS_CLI_HEADER: '1',            
            IDE: vscode.env.uriScheme.toLowerCase().includes('cursor') ? 'cursor' : 'vscode'
        };
                
        let pythonExe = os.platform().includes('darwin') ? 'python3' : 'python';
        if (fs.existsSync(path.join(this._workspaceDir, '.venv', 'bin'))) {            
            pythonExe = path.join(this._workspaceDir, '.venv', 'bin', 'python');
        }
        else if (fs.existsSync(path.join(this._workspaceDir, '.venv', 'Scripts'))) {            
            pythonExe = path.join(this._workspaceDir, '.venv', 'Scripts', 'python.exe');
        }
        else {
            console.log("Could not find Python virtual environment in workspace. Falling back to system Python.");
        }
        
        this._pythonProcess = spawn(pythonExe, [cliPath], {        
            cwd: this._workspaceDir,
            env: env,
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        console.log('[PanelView] Python process spawned');
        
        this._pythonProcess.stdout.on('data', (data) => {
            const dataStr = data.toString();
            this._responseBuffer += dataStr;
            
            // Log first chunk received
            if (this._responseBuffer.length === dataStr.length) {
                console.log('[PanelView] First response chunk received, size:', dataStr.length);
            }
            
            const markerIndex = this._responseBuffer.indexOf(END_MARKER);
            if (markerIndex !== -1) {
                console.log('[PanelView] End marker found, response size:', markerIndex);
                const jsonOutput = this._responseBuffer.substring(0, markerIndex).trim();
                this._responseBuffer = this._responseBuffer.substring(markerIndex + END_MARKER.length);
                
                if (this._pendingResolve) {
                    try {
                        console.log('[PanelView] Parsing JSON response...');
                        const jsonMatch = jsonOutput.match(/\{[\s\S]*\}/);
                        if (!jsonMatch) {
                            console.error('[PanelView] No JSON found in CLI output');
                            this._pendingReject(new Error('No JSON found in CLI output'));
                        } else {
                            const jsonData = JSON.parse(jsonMatch[0]);
                            
                            // Check if response indicates an error from CLI
                            if (jsonData.status === 'error' && jsonData.error) {
                                console.error('[PanelView] CLI returned error:', jsonData.error);
                                // Resolve with the error object so it can be handled gracefully
                                this._pendingResolve(jsonData);
                            } else {
                                console.log('[PanelView] Command executed successfully, response keys:', Object.keys(jsonData));
                                this._pendingResolve(jsonData);
                            }
                        }
                    } catch (parseError) {
                        console.error('[PanelView] JSON parse error:', parseError.message);
                        this._pendingReject(new Error(`Failed to parse CLI JSON: ${parseError.message}`));
                    }
                    this._pendingResolve = null;
                    this._pendingReject = null;
                }
            }
        });
        
        this._pythonProcess.stderr.on('data', (data) => {
            console.error('[PanelView] Python stderr:', data.toString());
        });
        
        this._pythonProcess.on('error', (err) => {
            console.error('[PanelView] Python process error:', err);
            this._pythonProcess = null;
            if (this._pendingReject) {
                this._pendingReject(new Error(`Python process error: ${err.message}`));
                this._pendingResolve = null;
                this._pendingReject = null;
            }
        });
        
        this._pythonProcess.on('close', (code) => {
            console.log('[PanelView] Python process closed with code:', code);
            this._pythonProcess = null;
            if (this._pendingReject) {
                this._pendingReject(new Error(`Python process exited unexpectedly (code ${code})`));
                this._pendingResolve = null;
                this._pendingReject = null;
            }
        });
    }
    
    /**
     * Cleanup - kill the Python process
     */
    cleanup() {
        if (this._pythonProcess) {
            console.log('[PanelView] Killing Python process');
            this._pythonProcess.kill();
            this._pythonProcess = null;
        }
    }
    
    /**
     * Execute command using the persistent Python process.
     */
    async execute(command) {
        // Delegate to injected CLI if present
        if (this._cli) {
            return this._cli.execute(command);
        }
        
        if (!this._pythonProcess) {
            this._spawnProcess();
        }
        
        console.log(`[PanelView] Executing command: "${command}"`);
        
        // Increase timeout for scope/status commands (they enrich scenarios with test links)
        const timeoutMs = (command.includes('scope') || command.includes('status')) ? 60000 : 30000;
        console.log(`[PanelView] Using timeout: ${timeoutMs}ms for command: "${command}"`);
        
        return new Promise((resolve, reject) => {
            this._pendingResolve = resolve;
            this._pendingReject = reject;
            
            const timeoutId = setTimeout(() => {
                if (this._pendingReject) {
                    console.error(`[PanelView] Command timed out after ${timeoutMs}ms: "${command}"`);
                    this._pendingReject(new Error(`Command timed out after ${timeoutMs / 1000} seconds: ${command}`));
                    this._pendingResolve = null;
                    this._pendingReject = null;
                }
            }, timeoutMs);
            
            const originalResolve = resolve;
            const originalReject = reject;
            this._pendingResolve = (value) => {
                clearTimeout(timeoutId);
                originalResolve(value);
            };
            this._pendingReject = (err) => {
                clearTimeout(timeoutId);
                originalReject(err);
            };
            
            try {
                const cmd = command.includes('--format json') ? command : `${command} --format json`;
                this._pythonProcess.stdin.write(cmd + '\n');
            } catch (err) {
                clearTimeout(timeoutId);
                this._pendingResolve = null;
                this._pendingReject = null;
                reject(new Error(`Failed to send command: ${err.message}`));
            }
        });
    }
}

module.exports = PanelView;
