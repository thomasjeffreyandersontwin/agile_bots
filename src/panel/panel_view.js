/**
 * Base class for all panel views.
 * Provides CLI command execution - each command spawns a new Python process.
 * This is the proven legacy approach that works reliably.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class PanelView {
    // Workspace/bot configuration (shared across views)
    static _workspaceDir = null;
    static _botDir = null;
    static _commandQueue = [];
    static _processingCommand = false;
    static _firstCommandSent = false;
    static _lastResponse = null;
    
    /**
     * Base class for all panel views.
     * Views access CLI execution - no parameters needed.
     */
    constructor() {
        // Views just inherit from base
    }
    
    /**
     * Log to file for debugging
     */
    static _log(message) {
        // Skip logging if no log file path configured (e.g., in tests)
        if (!PanelView._logFilePath) {
            return;
        }
        
        try {
            const timestamp = new Date().toISOString();
            const logMessage = `${timestamp} [PanelView] ${message}\n`;
            fs.appendFileSync(PanelView._logFilePath, logMessage, 'utf8');
        } catch (err) {
            console.error('[PanelView] Failed to write to log file:', err);
        }
    }
    
    /**
     * Initialize CLI configuration (call once at startup)
     * @param {string} workspaceDirectory - Workspace root path
     * @param {string} botDirectory - Bot directory path
     * @param {string} logFilePath - Path to log file
     */
    static initializeCLI(workspaceDirectory, botDirectory, logFilePath) {
        PanelView._workspaceDir = workspaceDirectory;
        PanelView._botDir = botDirectory || process.env.BOT_DIRECTORY;
        PanelView._logFilePath = logFilePath;
        
        if (!PanelView._botDir) {
            throw new Error('BOT_DIRECTORY environment variable must be set or botDirectory must be provided');
        }
        
        console.log('[PanelView] CLI configuration initialized:', {
            workspaceDir: PanelView._workspaceDir,
            botDir: PanelView._botDir
        });
    }
    
    /**
     * Get workspace directory
     */
    static getWorkspaceDir() {
        return PanelView._workspaceDir;
    }
    
    /**
     * Get bot directory
     */
    static getBotDir() {
        return PanelView._botDir;
    }
    
    /**
     * Cleanup (for tests).
     */
    static cleanupSharedCLI() {
        // Legacy approach has no persistent process to clean up
        PanelView._workspaceDir = null;
        PanelView._botDir = null;
    }
    
    /**
     * Execute command by spawning a new Python process (legacy approach).
     * Each command gets its own process - simple, reliable, no synchronization issues.
     */
    async execute(command) {
        PanelView._log(`=== EXECUTE START ===`);
        PanelView._log(`Command: "${command}"`);
        
        if (!PanelView._workspaceDir) {
            const error = 'CLI not initialized. Call PanelView.initializeCLI() first.';
            PanelView._log(`ERROR: ${error}`);
            throw new Error(error);
        }
        
        console.log(`[PanelView] Executing command: "${command}"`);
        
        return new Promise((resolve, reject) => {
            const workspaceRoot = PanelView._workspaceDir;
            const cliPath = path.join(workspaceRoot, 'agile_bots', 'src', 'cli', 'cli_main.py');
            
            PanelView._log(`CLI path: ${cliPath}`);
            PanelView._log(`Workspace root: ${workspaceRoot}`);
            PanelView._log(`Bot directory: ${PanelView._botDir}`);
            
            // Verify CLI path exists
            try {
                if (!fs.existsSync(cliPath)) {
                    const error = `CLI script not found at: ${cliPath}`;
                    PanelView._log(`ERROR: ${error}`);
                    throw new Error(error);
                }
            } catch (err) {
                const error = `Cannot find CLI script: ${cliPath}`;
                PanelView._log(`ERROR: ${error}`);
                reject(new Error(error));
                return;
            }
            
            const env = {
                ...process.env,
                PYTHONPATH: workspaceRoot,
                BOT_DIRECTORY: PanelView._botDir,
                // DO NOT set WORKING_AREA - let bot use its own saved workspace
                CLI_MODE: 'json',  // Use JSON mode for panel
                SUPPRESS_CLI_HEADER: '1'  // Skip header for pure JSON output
            };
            
            PanelView._log('Spawning Python process...');
            console.log('[PanelView] Spawning Python process for command');
            
            const pythonProcess = spawn('python', [cliPath], {
                cwd: workspaceRoot,
                env: env,
                stdio: ['pipe', 'pipe', 'pipe']
            });
            
            let stdout = '';
            let stderr = '';
            let timedOut = false;
            
            // Set timeout (30 seconds like legacy)
            const timeoutId = setTimeout(() => {
                timedOut = true;
                pythonProcess.kill();
                const error = 'Python process timed out after 30 seconds';
                PanelView._log(`ERROR: ${error}`);
                reject(new Error(error));
            }, 30000);
            
            // Send command via stdin and close it (this makes Python process exit after running command)
            try {
                const commandWithFormat = command.includes('--format json') ? command : `${command} --format json`;
                PanelView._log(`Sending to CLI: "${commandWithFormat}"`);
                pythonProcess.stdin.write(commandWithFormat + '\n');
                pythonProcess.stdin.end(); // Close stdin - tells Python we're done sending input
                PanelView._log('Command written to stdin, stdin closed');
                console.log('[PanelView] Command written to stdin, stdin closed');
            } catch (err) {
                clearTimeout(timeoutId);
                const error = `Failed to communicate with Python process: ${err.message}`;
                PanelView._log(`ERROR: ${error}`);
                reject(new Error(error));
                return;
            }
            
            // Collect stdout
            pythonProcess.stdout.on('data', (data) => {
                const chunk = data.toString();
                stdout += chunk;
                PanelView._log(`STDOUT chunk (${chunk.length} bytes): ${chunk.substring(0, 200)}...`);
            });
            
            // Collect stderr
            pythonProcess.stderr.on('data', (data) => {
                const chunk = data.toString();
                stderr += chunk;
                PanelView._log(`STDERR chunk: ${chunk}`);
            });
            
            // Handle process error
            pythonProcess.on('error', (err) => {
                clearTimeout(timeoutId);
                const error = `Python process error: ${err.message}`;
                PanelView._log(`ERROR: ${error}`);
                console.error('[PanelView] Python process error:', err);
                reject(new Error(error));
            });
            
            // Handle process completion
            pythonProcess.on('close', (code) => {
                clearTimeout(timeoutId);
                
                if (timedOut) {
                    return; // Already rejected
                }
                
                PanelView._log(`Python process closed with exit code: ${code}`);
                PanelView._log(`STDOUT length: ${stdout.length} bytes`);
                PanelView._log(`STDERR length: ${stderr.length} bytes`);
                PanelView._log(`Full STDOUT: ${stdout}`);
                if (stderr) {
                    PanelView._log(`Full STDERR: ${stderr}`);
                }
                
                console.log('[PanelView] Python process closed', {
                    exitCode: code,
                    stdoutLength: stdout.length,
                    stderrLength: stderr.length
                });
                
                if (stderr) {
                    console.error('[PanelView] Python stderr:', stderr);
                }
                
                if (code !== 0 && stderr) {
                    const error = `Python CLI failed (exit ${code}): ${stderr}`;
                    PanelView._log(`ERROR: ${error}`);
                    reject(new Error(error));
                    return;
                }
                
                if (!stdout || stdout.trim().length === 0) {
                    const error = 'No output from Python CLI';
                    PanelView._log(`ERROR: ${error}`);
                    reject(new Error(error));
                    return;
                }
                
                // Parse JSON response
                try {
                    // Find the JSON object in the output (skip any header text)
                    const jsonMatch = stdout.match(/\{[\s\S]*\}/);
                    if (!jsonMatch) {
                        const error = 'No JSON found in CLI output';
                        PanelView._log(`ERROR: ${error}`);
                        reject(new Error(error));
                        return;
                    }
                    
                    PanelView._log(`JSON extracted: ${jsonMatch[0].substring(0, 500)}...`);
                    const jsonData = JSON.parse(jsonMatch[0]);
                    // Cache last non-status response so views (e.g., instructions) can re-use it without re-running commands
                    // Avoid overwriting navigation/instruction responses with plain status (which lacks instructions)
                    if (command !== 'status') {
                        PanelView._lastResponse = jsonData;
                    }
                    PanelView._log(`JSON parsed successfully`);
                    PanelView._log(`=== EXECUTE SUCCESS ===`);
                    console.log('[PanelView] Command executed successfully, JSON parsed');
                    resolve(jsonData);
                } catch (parseError) {
                    const error = `Failed to parse CLI JSON output: ${parseError.message}`;
                    PanelView._log(`ERROR: ${error}`);
                    PanelView._log(`Raw output (first 500 chars): ${stdout.substring(0, 500)}`);
                    console.error('[PanelView] JSON parse error:', parseError.message);
                    console.error('[PanelView] Raw output:', stdout.substring(0, 500));
                    reject(new Error(error));
                }
            });
        });
    }
    
    /**
     * Get unique element ID
     */
    getElementId() {
        return `view-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Render to HTML. Override in subclasses.
     */
    render(jsonData) {
        throw new Error('render() must be implemented by subclass');
    }
}

module.exports = PanelView;
