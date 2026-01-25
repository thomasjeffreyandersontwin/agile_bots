/**
 * Bot Panel Controller
 * 
 * Manages webview panel lifecycle and coordinates data fetching,
 * parsing, and rendering using the new domain-oriented BotView.
 * Implements singleton pattern.
 */

const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const BotView = require("./bot_view");
const PanelView = require("./panel_view");

class BotPanel {
  static currentPanel = undefined;
  static viewType = "agilebot.botPanel";

  constructor(panel, workspaceRoot, extensionUri) {
    try {
      // Setup file logging first
      const logFile = path.join(workspaceRoot || 'c:\\dev\\augmented-teams', 'panel-debug.log');
      this.logFilePath = logFile;
      this._log = (msg) => {
        const timestamp = new Date().toISOString();
        try {
          fs.appendFileSync(logFile, `${timestamp} ${msg}\n`);
        } catch (e) {
          console.error('[BotPanel] Failed to write to log file:', e);
        }
        console.log(msg);
      };
      
      this._displayError = (errorMsg) => {
        this._log('[BotPanel] Displaying error in webview: ' + errorMsg);
        vscode.window.showErrorMessage('Bot Panel Error: ' + errorMsg);
        if (this._panel && this._panel.webview) {
          this._panel.webview.postMessage({
            command: 'displayError',
            error: errorMsg
          });
        }
      };
      
      this._log("[BotPanel] Constructor invoked");
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:19',message:'Constructor ENTRY',data:{workspaceRoot,hasPanel:!!panel,hasExtensionUri:!!extensionUri},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B,D'})}).catch(()=>{});
      // #endregion
      console.log(`[BotPanel] Constructor called - workspaceRoot: ${workspaceRoot}`);
      this._panel = panel;
      this._workspaceRoot = workspaceRoot;
      this._extensionUri = extensionUri;
      this._disposables = [];
      this._expansionState = {};
      
      // Read panel version from package.json
      console.log("[BotPanel] Reading panel version");
      this._panelVersion = this._readPanelVersion();
      console.log(`[BotPanel] Panel version: ${this._panelVersion}`);
      
      // Determine bot directory (from env var or default to story_bot)
      let botDirectory = process.env.BOT_DIRECTORY || path.join(workspaceRoot, 'bots', 'story_bot');
      // Ensure bot directory is absolute
      if (!path.isAbsolute(botDirectory)) {
        botDirectory = path.join(workspaceRoot, botDirectory);
      }
      console.log(`[BotPanel] Bot directory: ${botDirectory}`);
      
      // Create shared PanelView instance for CLI operations
      console.log("[BotPanel] Creating shared PanelView instance");
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:43',message:'Before PanelView creation',data:{workspaceRoot,botDirectory},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      this._sharedCLI = new PanelView(botDirectory);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:43',message:'After PanelView creation',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      console.log("[BotPanel] Shared PanelView instance created successfully");
      
      // Initialize BotView (uses shared CLI)
      this._botView = null;
      
      // Set initial loading HTML
      console.log("[BotPanel] Setting initial loading HTML");
      this._panel.webview.html = this._getWebviewContent('<div style="padding: 20px;">Loading bot panel...</div>');
      
      // Update content asynchronously (can't await in constructor)
      console.log("[BotPanel] Calling _update()");
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:55',message:'Before _update()',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      this._update().catch(err => {
        console.error(`[BotPanel] ERROR in async _update: ${err.message}`);
        console.error(`[BotPanel] ERROR stack: ${err.stack}`);
        vscode.window.showErrorMessage(`Bot Panel Error: ${err.message}`);
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:55',message:'_update() threw error',data:{error:err.message,stack:err.stack},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
        // #endregion
      });
      console.log("[BotPanel] Constructor completed successfully");
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:60',message:'Constructor EXIT',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
    } catch (error) {
      console.error(`[BotPanel] ERROR in constructor: ${error.message}`);
      console.error(`[BotPanel] ERROR stack: ${error.stack}`);
      vscode.window.showErrorMessage(`Bot Panel Constructor Error: ${error.message}\n${error.stack}`);
      throw error;
    }

    // Listen for when the panel is disposed
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    // Update the content when the webview becomes visible
    this._panel.onDidChangeViewState(
      (e) => {
        if (this._panel.visible) {
          this._update().catch(err => {
            console.error(`[BotPanel] ERROR in visibility update: ${err.message}`);
          });
        }
      },
      null,
      this._disposables
    );

    // Handle messages from the webview
    this._log('[BotPanel] Registering onDidReceiveMessage handler');
    this._panel.webview.onDidReceiveMessage(
      (message) => {
        this._log('[BotPanel] *** MESSAGE HANDLER FIRED ***');
        this._log('[BotPanel] Received message from webview: ' + message.command + ' ' + JSON.stringify(message));
        switch (message.command) {
          case "refresh":
            // Delete the enriched cache to force regeneration of test links
            const fs = require('fs');
            const cachePath = path.join(this._workspaceRoot, 'docs', 'stories', '.story-graph-enriched-cache.json');
            try {
              if (fs.existsSync(cachePath)) {
                fs.unlinkSync(cachePath);
                this._log('[BotPanel] Deleted enriched cache file');
              }
            } catch (err) {
              this._log(`[BotPanel] Warning: Could not delete cache: ${err.message}`);
            }
            this._update().catch(err => console.error(`[BotPanel] Refresh error: ${err.message}`));
            return;
          case "logToFile":
            if (message.message) {
              const fs = require('fs');
              const logPath = path.join(this._workspaceRoot, 'panel_clicks.log');
              const timestamp = new Date().toISOString();
              fs.appendFileSync(logPath, `[${timestamp}] ${message.message}\n`);
            }
            return;
          case "analyzeNode":
            this._log(`[BotPanel] analyzeNode: ${message.nodeName} (${message.nodeType})`);
            
            // Call backend to analyze node and determine behavior
            this._botView?.execute(`analyze_node "${message.nodeName}" type:${message.nodeType}`)
              .then((result) => {
                this._log(`[BotPanel] analyzeNode result: ${JSON.stringify(result)}`);
                
                if (result && result.behavior) {
                  // Send behavior back to webview to update button tooltip
                  this._panel.webview.postMessage({
                    command: 'updateSubmitTooltip',
                    nodeName: message.nodeName,
                    behavior: result.behavior
                  });
                }
              })
              .catch((error) => {
                this._log(`[BotPanel] analyzeNode ERROR: ${error.message}`);
              });
            return;
          case "openFile":
            this._log('[BotPanel] openFile message received with filePath: ' + message.filePath);
            if (message.filePath) {
              const rawPath = message.filePath;
              const cleanPath = rawPath.split('#')[0];
              const fragment = rawPath.includes('#') 
                ? rawPath.split('#')[1] 
                : null;
              
              let lineNumber = null;
              let symbolName = null;
              
              if (fragment) {
                if (fragment.startsWith('L')) {
                  lineNumber = parseInt(fragment.substring(1));
                } else {
                  symbolName = fragment;
                }
              }
              
              // Normalize file path; handle file:// URIs and encoded characters
              let absolutePath;
              if (cleanPath.startsWith('file://')) {
                absolutePath = vscode.Uri.parse(cleanPath).fsPath;
              } else {
                const decoded = decodeURIComponent(cleanPath);
                absolutePath = path.isAbsolute(decoded) 
                  ? decoded 
                  : path.join(this._workspaceRoot, decoded);
              }
              const fileUri = vscode.Uri.file(absolutePath);
              
              // Check if path is a directory
              const fs = require('fs');
              if (fs.existsSync(absolutePath) && fs.statSync(absolutePath).isDirectory()) {
                // Reveal directory in VS Code file explorer
                vscode.commands.executeCommand('revealInExplorer', fileUri).catch((error) => {
                  vscode.window.showErrorMessage(`Failed to reveal folder: ${message.filePath}\n${error.message}`);
                });
              } else {
                const fileExtension = cleanPath.split('.').pop().toLowerCase();
                const binaryOrSpecialExtensions = ['drawio', 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'svg'];
                
                if (binaryOrSpecialExtensions.includes(fileExtension)) {
                  vscode.commands.executeCommand('vscode.open', fileUri).catch((error) => {
                    vscode.window.showErrorMessage(`Failed to open file: ${message.filePath}\n${error.message}`);
                  });
                } else {
                vscode.workspace.openTextDocument(fileUri).then(
                  (doc) => {
                    if (symbolName) {
                      const text = doc.getText();
                      const lines = text.split('\n');
                      let foundLine = -1;
                      
                      for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (line.includes(symbolName) && 
                            (line.trim().startsWith('def ') || 
                             line.trim().startsWith('class ') ||
                             line.trim().startsWith('async def ') ||
                             line.includes(`def ${symbolName}(`) ||
                             line.includes(`class ${symbolName}(`))) {
                          foundLine = i;
                          break;
                        }
                      }
                      
                      if (foundLine >= 0) {
                        lineNumber = foundLine + 1;
                      }
                    }
                    
                    const options = lineNumber 
                      ? { 
                          selection: new vscode.Range(lineNumber - 1, 0, lineNumber - 1, 0),
                          viewColumn: vscode.ViewColumn.One
                        }
                      : { viewColumn: vscode.ViewColumn.One };
                    vscode.window.showTextDocument(doc, options);
                  },
                  (error) => {
                    vscode.window.showErrorMessage(`Failed to open file: ${message.filePath}\n${error.message}`);
                  }
                );
                }
              }
            }
            return;
          case "clearScopeFilter":
            this._botView?.execute('scope all')
              .then(() => this._update())
              .catch((error) => {
                this._log(`[BotPanel] ERROR clearScopeFilter: ${error.message}`);
                vscode.window.showErrorMessage(`Failed to clear scope: ${error.message}`);
                this._displayError(`Failed to clear scope: ${error.message}`);
              });
            return;
          case "showAllScope":
            this._botView?.execute('scope showall')
              .then(() => this._update())
              .catch((error) => {
                this._log(`[BotPanel] ERROR showAllScope: ${error.message}`);
                vscode.window.showErrorMessage(`Failed to show all: ${error.message}`);
                this._displayError(`Failed to show all: ${error.message}`);
              });
            return;
          case "updateFilter":
            this._log('[BotPanel] Received updateFilter: ' + message.filter);
            this._log('[BotPanel] _botView is: ' + this._botView);
            
            if (!this._botView) {
              const errorMsg = '_botView is null, cannot execute scope command';
              this._log('[BotPanel] ERROR: ' + errorMsg);
              this._displayError(errorMsg);
              return;
            }
            
            if (message.filter && message.filter.trim()) {
              const scopeCmd = `scope ${message.filter.trim()}`;
              this._log('[BotPanel] Executing scope command: ' + scopeCmd);
              
              this._botView.execute(scopeCmd)
                .then((result) => {
                  this._log('[BotPanel] Scope filter applied, result: ' + JSON.stringify(result).substring(0, 200));
                  return this._update();
                })
                .then(() => {
                  this._log('[BotPanel] Update completed after scope filter');
                })
                .catch((err) => {
                  const errorMsg = 'Scope filter failed: ' + err.message;
                  this._log('[BotPanel] ERROR: ' + errorMsg);
                  this._log('[BotPanel] ERROR stack: ' + err.stack);
                  this._displayError(errorMsg);
                  vscode.window.showErrorMessage(errorMsg);
                  // Don't re-throw - show error but don't crash panel
                });
            } else {
              // Empty filter = clear filter
              this._log('[BotPanel] Clearing scope filter');
              
              this._botView.execute('scope all')
                .then((result) => {
                  this._log('[BotPanel] Scope cleared successfully');
                  return this._update();
                })
                .catch((err) => {
                  const errorMsg = 'Clear scope failed: ' + err.message;
                  this._log('[BotPanel] ERROR: ' + errorMsg);
                  this._log('[BotPanel] ERROR stack: ' + err.stack);
                  this._displayError(errorMsg);
                  vscode.window.showErrorMessage(errorMsg);
                  // Don't re-throw - show error but don't crash panel
                });
            }
            return;
          case "updateWorkspace":
            this._log('[BotPanel] Received updateWorkspace message: ' + message.workspacePath);
            if (message.workspacePath) {
              this._botView?.handleEvent('updateWorkspace', { workspacePath: message.workspacePath })
                .then((result) => {
                  this._log('[BotPanel] updateWorkspace result: ' + JSON.stringify(result));
                  this._workspaceRoot = message.workspacePath;
                  return this._update();
                })
                .catch((error) => {
                  this._log('[BotPanel] ERROR updateWorkspace: ' + error.message);
                  this._log('[BotPanel] ERROR stack: ' + error.stack);
                  vscode.window.showErrorMessage(`Failed to update workspace: ${error.message}`);
                });
            }
            return;
          case "switchBot":
            if (message.botName) {
              this._botView?.headerView?.handleEvent('switchBot', { botName: message.botName })
                .then(() => this._update())
                .catch((error) => {
                  vscode.window.showErrorMessage(`Failed to switch bot: ${error.message}`);
                });
            }
            return;
          case "getBehaviorRules":
            if (message.behaviorName) {
              this._log(`[BotPanel] getBehaviorRules -> ${message.behaviorName}`);
              this._log(`[getBehaviorRules] STARTED for behavior: ${message.behaviorName}`);
              
              // Execute submitrules CLI command to submit rules to chat
              this._botView?.execute(`submitrules:${message.behaviorName}`)
                .then((result) => {
                  this._log('[BotPanel] Rules submitted:', result);
                  this._log(`[getBehaviorRules] Result received: ${JSON.stringify(result, null, 2)}`);
                  
                  // Handle dictionary response from Python
                  if (result && typeof result === 'object') {
                    this._log(`[getBehaviorRules] Result is object with status: ${result.status}`);
                    if (result.status === 'success') {
                      const msg = result.message || `${message.behaviorName} rules submitted to chat!`;
                      this._log(`[getBehaviorRules] SUCCESS - showing message: ${msg}`);
                      vscode.window.showInformationMessage(msg);
                    } else if (result.status === 'error') {
                      const errorMsg = result.message || 'Unknown error';
                      this._log(`[getBehaviorRules] ERROR status - showing error: ${errorMsg}`);
                      vscode.window.showErrorMessage(`Failed to submit rules: ${errorMsg}`);
                    } else {
                      // Legacy format: check output field
                      const outputStr = typeof result.output === 'string' ? result.output : '';
                      this._log(`[getBehaviorRules] Legacy format - output: ${outputStr}`);
                      if (outputStr.includes('submitted')) {
                        this._log(`[getBehaviorRules] Output includes 'submitted' - SUCCESS`);
                        vscode.window.showInformationMessage(`${message.behaviorName} rules submitted to chat!`);
                      } else {
                        const errorMsg = result.message || outputStr || 'Unknown error';
                        this._log(`[getBehaviorRules] Output does NOT include 'submitted' - ERROR: ${errorMsg}`);
                        vscode.window.showErrorMessage(`Failed to submit rules: ${errorMsg}`);
                      }
                    }
                  } else {
                    this._log(`[getBehaviorRules] Result is NOT an object - type: ${typeof result}, value: ${result}`);
                    vscode.window.showWarningMessage('Submit completed with unknown result');
                  }
                  
                  // Refresh panel to show current position
                  this._log(`[getBehaviorRules] About to refresh panel`);
                  return this._update();
                })
                .catch((error) => {
                  this._log(`[BotPanel] ERROR getting behavior rules: ${error.message}`);
                  this._log(`[getBehaviorRules] CATCH BLOCK - Error: ${error.message}, Stack: ${error.stack}`);
                  vscode.window.showErrorMessage(`Failed to get rules: ${error.message}`);
                });
            }
            return;
          case "executeNavigationCommand":
            if (message.commandText) {
              this._log(`[BotPanel] executeNavigationCommand -> ${message.commandText}`);
              this._botView?.execute(message.commandText)
                .then((result) => {
                  this._log(`[BotPanel] executeNavigationCommand success: ${message.commandText} | result keys: ${Object.keys(result || {})}`);
                  return this._update();
                })
                .catch((error) => {
                  this._log(`[BotPanel] executeNavigationCommand ERROR: ${error.message}`);
                  this._log(`[BotPanel] executeNavigationCommand STACK: ${error.stack}`);
                  vscode.window.showErrorMessage(`Failed to execute ${message.commandText}: ${error.message}`);
                });
            }
            return;
          case "renameNode":
            if (message.nodePath && message.currentName) {
              // Prompt for new name
              vscode.window.showInputBox({
                prompt: `Rename "${message.currentName}"`,
                value: message.currentName,
                placeHolder: 'Enter new name'
              }).then((newName) => {
                if (newName && newName !== message.currentName) {
                  // Optimistic update: tell webview to update DOM immediately
                  this._panel.webview.postMessage({
                    command: 'optimisticRename',
                    nodePath: message.nodePath,
                    oldName: message.currentName,
                    newName: newName
                  });
                  
                  // Escape quotes and backslashes in the new name
                  const escapedName = newName.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
                  const command = `${message.nodePath}.rename name:"${escapedName}"`;
                  this._log(`[BotPanel] Rename command: ${command}`);
                  
                  // Log to file
                  const fs = require('fs');
                  const logPath = path.join(this._workspaceRoot, 'story_graph_operations.log');
                  const timestamp = new Date().toISOString();
                  const logEntry = `\n${'='.repeat(80)}\n[${timestamp}] RENAME COMMAND: ${command}\n`;
                  
                  try {
                    fs.appendFileSync(logPath, logEntry);
                  } catch (err) {
                    this._log(`[BotPanel] Failed to write to log file: ${err.message}`);
                  }
                  
                  // Execute backend command asynchronously (no await, no _update on success)
                  this._botView?.execute(command)
                    .then((result) => {
                      this._log(`[BotPanel] Rename success: ${JSON.stringify(result).substring(0, 500)}`);
                      
                      // Log result to file
                      const resultLog = `[${timestamp}] RESULT: ${JSON.stringify(result, null, 2)}\n`;
                      try {
                        fs.appendFileSync(logPath, resultLog);
                      } catch (err) {
                        this._log(`[BotPanel] Failed to write result to log file: ${err.message}`);
                      }
                      
                      // NO _update() call - optimistic update already happened
                    })
                    .catch((error) => {
                      this._log(`[BotPanel] Rename ERROR: ${error.message}`);
                      
                      // Log error to file
                      const errorLog = `[${timestamp}] ERROR: ${error.message}\nSTACK: ${error.stack}\n`;
                      try {
                        fs.appendFileSync(logPath, errorLog);
                      } catch (err) {
                        this._log(`[BotPanel] Failed to write error to log file: ${err.message}`);
                      }
                      
                      vscode.window.showErrorMessage(`Failed to rename: ${error.message}`);
                      
                      // Revert optimistic update on error
                      this._panel.webview.postMessage({
                        command: 'revertRename',
                        nodePath: message.nodePath,
                        oldName: message.currentName
                      });
                    });
                }
              });
            }
            return;
          case "executeCommand":
            if (message.commandText) {
              this._log(`\n${'='.repeat(80)}`);
              this._log(`[BotPanel] *** RECEIVED executeCommand MESSAGE ***`);
              this._log(`[BotPanel] commandText: ${message.commandText}`);
              this._log(`[BotPanel] Full message: ${JSON.stringify(message)}`);
              
              // Check if this is a create/delete/move operation (optimistic update candidates)
              const isCreateOp = message.commandText.includes('.create_') || message.commandText.includes('create child') || message.commandText.includes('create epic');
              const isDeleteOp = message.commandText.includes('.delete');
              const isMoveOp = message.commandText.includes('.move_to');
              const needsOptimisticUpdate = isCreateOp || isDeleteOp || isMoveOp;
              
              // Log to file for create/delete/rename operations
              const fs = require('fs');
              const logPath = path.join(this._workspaceRoot, 'story_graph_operations.log');
              const timestamp = new Date().toISOString();
              const logEntry = `\n${'='.repeat(80)}\n[${timestamp}] RECEIVED COMMAND: ${message.commandText}\n`;
              
              try {
                fs.appendFileSync(logPath, logEntry);
              } catch (err) {
                this._log(`[BotPanel] Failed to write to log file: ${err.message}`);
              }
              
              this._log(`[BotPanel] Calling botView.execute... (optimistic: ${needsOptimisticUpdate})`);
              this._botView?.execute(message.commandText)
                .then((result) => {
                  this._log(`[BotPanel] *** executeCommand SUCCESS ***`);
                  this._log(`[BotPanel] command: ${message.commandText}`);
                  this._log(`[BotPanel] result: ${JSON.stringify(result).substring(0, 500)}`);
                  
                  // Log result to file
                  const resultLog = `[${timestamp}] SUCCESS RESULT: ${JSON.stringify(result, null, 2)}\n`;
                  try {
                    fs.appendFileSync(logPath, resultLog);
                  } catch (err) {
                    this._log(`[BotPanel] Failed to write result to log file: ${err.message}`);
                  }
                  
                  // Only refresh for non-optimistic operations
                  if (!needsOptimisticUpdate) {
                    this._log(`[BotPanel] Non-optimistic command - calling _update() to refresh panel...`);
                    return this._update();
                  } else {
                    this._log(`[BotPanel] Optimistic command - skipping _update(), frontend already updated`);
                  }
                })
                .then(() => {
                  if (!needsOptimisticUpdate) {
                    this._log(`[BotPanel] Panel update completed`);
                  }
                  this._log(`${'='.repeat(80)}\n`);
                })
                .catch((error) => {
                  this._log(`[BotPanel] *** executeCommand ERROR ***`);
                  this._log(`[BotPanel] command: ${message.commandText}`);
                  this._log(`[BotPanel] error: ${error.message}`);
                  this._log(`[BotPanel] stack: ${error.stack}`);
                  
                  // Log error to file
                  const errorLog = `[${timestamp}] ERROR: ${error.message}\nSTACK: ${error.stack}\n`;
                  try {
                    fs.appendFileSync(logPath, errorLog);
                  } catch (err) {
                    this._log(`[BotPanel] Failed to write error to log file: ${err.message}`);
                  }
                  
                  vscode.window.showErrorMessage(`Failed to execute ${message.commandText}: ${error.message}`);
                  
                  // On error, refresh to revert optimistic updates
                  if (needsOptimisticUpdate) {
                    this._log(`[BotPanel] Optimistic command failed - calling _update() to revert`);
                    this._update().catch(err => {
                      this._log(`[BotPanel] ERROR in revert _update: ${err.message}`);
                    });
                  }
                  
                  this._log(`${'='.repeat(80)}\n`);
                });
            } else {
              this._log(`[BotPanel] WARNING: executeCommand received with no commandText`);
            }
            return;
          case "navigateToBehavior":
            if (message.behaviorName) {
              const cmd = `${message.behaviorName}`;
              this._log(`[BotPanel] navigateToBehavior -> ${cmd}`);
              this._botView?.execute(cmd)
                .then((result) => {
                  this._log(`[BotPanel] navigateToBehavior success: ${cmd} | result keys: ${Object.keys(result || {})}`);
                  return this._update();
                })
                .catch((error) => {
                  this._log(`[BotPanel] navigateToBehavior ERROR: ${error.message}`);
                  this._log(`[BotPanel] navigateToBehavior STACK: ${error.stack}`);
                  vscode.window.showErrorMessage(`Failed to navigate to behavior: ${error.message}`);
                });
            }
            return;
          case "navigateToAction":
            if (message.behaviorName && message.actionName) {
              const cmd = `${message.behaviorName}.${message.actionName}`;
              this._log(`[BotPanel] navigateToAction -> ${cmd}`);
              this._botView?.execute(cmd)
                .then((result) => {
                  this._log(`[BotPanel] navigateToAction success: ${cmd} | result keys: ${Object.keys(result || {})}`);
                  const currentAction = result?.bot?.current_action || result?.current_action;
                  const currentBehavior = result?.bot?.current_behavior || result?.current_behavior;
                  this._log(`[BotPanel] After navigation - current_behavior: ${currentBehavior}, current_action: ${currentAction}`);
                  return this._update();
                })
                .catch((error) => {
                  this._log(`[BotPanel] navigateToAction ERROR: ${error.message}`);
                  this._log(`[BotPanel] navigateToAction STACK: ${error.stack}`);
                  vscode.window.showErrorMessage(`Failed to navigate to action: ${error.message}`);
                });
            }
            return;
          case "navigateAndExecute":
            if (message.behaviorName && message.actionName && message.operationName) {
              const command = `${message.behaviorName}.${message.actionName}.${message.operationName}`;
              this._log(`[BotPanel] navigateAndExecute -> ${command}`);
              this._botView?.execute(command)
                .then((result) => {
                  this._log(`[BotPanel] navigateAndExecute success: ${command} | result keys: ${Object.keys(result || {})}`);
                  return this._update();
                })
                .catch((error) => {
                  this._log(`[BotPanel] navigateAndExecute ERROR: ${error.message}`);
                  this._log(`[BotPanel] navigateAndExecute STACK: ${error.stack}`);
                  vscode.window.showErrorMessage(`Failed to execute operation: ${error.message}`);
                });
            }
            return;
          case "toggleSection":
            if (message.sectionId) {
              // Expansion state is handled client-side via JavaScript
            }
            return;
          case "toggleCollapse":
            if (message.elementId) {
              // Expansion state is handled client-side via JavaScript
            }
            return;
          case "sendToChat":
            this._log('sendToChat - calling bot submit command');
            
            // Call the bot's submit command (Python handles everything)
            this._botView?.execute('submit')
              .then((output) => {
                this._log('Bot submit command output:', output);
                
                // Handle dictionary response from Python
                if (output && typeof output === 'object' && output.status) {
                  if (output.status === 'success') {
                    const msg = output.message || 'Instructions submitted to chat!';
                    vscode.window.showInformationMessage(msg);
                  } else {
                    const errorMsg = output.message || 'Unknown error';
                    vscode.window.showErrorMessage(`Submit failed: ${errorMsg}`);
                  }
                }
                // Handle string response (legacy/CLI format)
                else {
                  const outputStr = typeof output === 'string' ? output : JSON.stringify(output || '');
                  
                  if (outputStr && (outputStr.includes('SUCCESS:') || outputStr.includes('submitted to Cursor chat successfully'))) {
                    vscode.window.showInformationMessage('Instructions submitted to chat!');
                  }
                  else if (outputStr && (outputStr.includes('ERROR:') || outputStr.includes('FAILED:'))) {
                    const errorMatch = outputStr.match(/ERROR:|FAILED:\s*(.+)/);
                    const errorMsg = errorMatch ? errorMatch[1] : 'Unknown error';
                    vscode.window.showErrorMessage(`Submit failed: ${errorMsg}`);
                  }
                  else {
                    vscode.window.showWarningMessage('Submit completed with unknown result');
                    this._log('[PANEL] Submit output:', output);
                  }
                }
              })
              .catch((error) => {
                this._log('Submit command failed:', error);
                vscode.window.showErrorMessage(`Submit command failed: ${error.message}`);
              });
            return;
          case "saveClarifyAnswers":
            if (message.answers) {
              this._log(`[BotPanel] saveClarifyAnswers -> ${JSON.stringify(message.answers)}`);
              const answersJson = JSON.stringify(message.answers).replace(/'/g, "\\'");
              const cmd = `save --answers '${answersJson}'`;
              this._botView?.execute(cmd)
                .then(() => {
                  this._log(`[BotPanel] saveClarifyAnswers success`);
                  vscode.window.showInformationMessage('Answers saved successfully');
                })
                .catch((error) => {
                  this._log(`[BotPanel] saveClarifyAnswers ERROR: ${error.message}`);
                  vscode.window.showErrorMessage(`Failed to save clarify answers: ${error.message}`);
                });
            }
            return;
          case "saveClarifyEvidence":
            if (message.evidence_provided) {
              this._log(`[BotPanel] saveClarifyEvidence -> ${JSON.stringify(message.evidence_provided)}`);
              const evidenceJson = JSON.stringify(message.evidence_provided).replace(/'/g, "\\'");
              const cmd = `save --evidence_provided '${evidenceJson}'`;
              this._botView?.execute(cmd)
                .then(() => {
                  this._log(`[BotPanel] saveClarifyEvidence success`);
                  vscode.window.showInformationMessage('Evidence saved successfully');
                })
                .catch((error) => {
                  this._log(`[BotPanel] saveClarifyEvidence ERROR: ${error.message}`);
                  vscode.window.showErrorMessage(`Failed to save clarify evidence: ${error.message}`);
                });
            }
            return;
          case "saveStrategyDecision":
            if (message.criteriaKey && message.selectedOption) {
              this._log(`[BotPanel] saveStrategyDecision -> ${message.criteriaKey}: ${message.selectedOption}`);
              // Build decisions object with just this one decision
              const decisions = {};
              decisions[message.criteriaKey] = message.selectedOption;
              const decisionsJson = JSON.stringify(decisions).replace(/'/g, "\\'");
              const cmd = `save --decisions '${decisionsJson}'`;
              this._botView?.execute(cmd)
                .then(() => {
                  this._log(`[BotPanel] saveStrategyDecision success`);
                  vscode.window.showInformationMessage('Strategy decision saved successfully');
                })
                .catch((error) => {
                  this._log(`[BotPanel] saveStrategyDecision ERROR: ${error.message}`);
                  vscode.window.showErrorMessage(`Failed to save strategy decision: ${error.message}`);
                });
            }
            return;
          case "saveStrategyAssumptions":
            if (message.assumptions) {
              this._log(`[BotPanel] saveStrategyAssumptions -> ${JSON.stringify(message.assumptions)}`);
              const assumptionsJson = JSON.stringify(message.assumptions).replace(/'/g, "\\'");
              const cmd = `save --assumptions '${assumptionsJson}'`;
              this._botView?.execute(cmd)
                .then(() => {
                  this._log(`[BotPanel] saveStrategyAssumptions success`);
                  vscode.window.showInformationMessage('Strategy assumptions saved successfully');
                })
                .catch((error) => {
                  this._log(`[BotPanel] saveStrategyAssumptions ERROR: ${error.message}`);
                  vscode.window.showErrorMessage(`Failed to save strategy assumptions: ${error.message}`);
                });
            }
            return;
        }
      },
      null,
      this._disposables
    );
  }

  static createOrShow(workspaceRoot, extensionUri) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:262',message:'createOrShow ENTRY',data:{workspaceRoot,extensionUri:extensionUri?.toString()},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    console.log(`[BotPanel] >>> ENTERING createOrShow - workspaceRoot: ${workspaceRoot}`);
    console.log(`[BotPanel] >>> extensionUri: ${extensionUri}`);
    
    try {
      const column = vscode.ViewColumn.Two;
      console.log(`[BotPanel] >>> Column set: ${column}`);

      // If we already have a panel, show it
      if (BotPanel.currentPanel) {
        console.log("[BotPanel] >>> Reusing existing panel");
        BotPanel.currentPanel._panel.reveal(column);
        return;
      }

      console.log("[BotPanel] >>> Creating new webview panel");
      // Otherwise, create a new panel
      const panel = vscode.window.createWebviewPanel(
        BotPanel.viewType,
        "Bot Panel",
        column,
        {
          enableScripts: true,
          retainContextWhenHidden: false,
          localResourceRoots: [
            extensionUri
          ],
        }
      );
      console.log("[BotPanel] >>> Webview panel created");

      console.log("[BotPanel] >>> Instantiating BotPanel class");
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:294',message:'Before new BotPanel()',data:{hasPanel:!!panel},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      BotPanel.currentPanel = new BotPanel(panel, workspaceRoot, extensionUri);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:294',message:'After new BotPanel()',data:{instanceCreated:!!BotPanel.currentPanel},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      console.log("[BotPanel] >>> BotPanel instance created successfully");
    } catch (error) {
      console.error(`[BotPanel] >>> EXCEPTION in createOrShow: ${error.message}`);
      console.error(`[BotPanel] >>> Stack: ${error.stack}`);
      vscode.window.showErrorMessage(`Bot Panel Error: ${error.message}`);
      throw error;
    }
  }

  _readPanelVersion() {
    try {
      // Try multiple locations for package.json
      const possiblePaths = [
        path.join(__dirname, "package.json"),
        path.join(__dirname, "..", "package.json"),
        path.join(__dirname, "..", "..", "package.json")
      ];
      
      for (const packageJsonPath of possiblePaths) {
        try {
          if (fs.existsSync(packageJsonPath)) {
            console.log(`[BotPanel] Found package.json at: ${packageJsonPath}`);
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
            if (packageJson.version) {
              console.log(`[BotPanel] Panel version: ${packageJson.version}`);
              return packageJson.version;
            }
          }
        } catch (err) {
          console.log(`[BotPanel] Could not read package.json at ${packageJsonPath}: ${err.message}`);
        }
      }
      
      console.warn("[BotPanel] Could not find package.json in any expected location");
      return null;
    } catch (error) {
      console.error("[BotPanel] Failed to read panel version:", error);
      return null;
    }
  }

  dispose() {
    BotPanel.currentPanel = undefined;

    // Clean up BotView
      this._botView = null;

    // Clean up shared CLI
    console.log("[BotPanel] Cleaning up shared PanelView CLI");
    if (this._sharedCLI) {
      this._sharedCLI.cleanup();
      this._sharedCLI = null;
    }

    // Clean up resources
    this._panel.dispose();

    while (this._disposables.length) {
      const disposable = this._disposables.pop();
      if (disposable) {
        disposable.dispose();
      }
    }
  }

  async _update() {
    console.log('[BotPanel] _update() called');
    this._log('[BotPanel] _update() called - hasBotView: ' + !!this._botView);
    try {
      this._log('[BotPanel] _update() START');
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:384',message:'_update() ENTRY',data:{hasBotView:!!this._botView},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
      console.log('[BotPanel] Fetching bot status...');
      // #endregion
      console.log("[BotPanel] _update() called");
      const webview = this._panel.webview;
      this._panel.title = "Bot Panel";
      
      // Initialize BotView if needed (uses shared CLI)
      if (!this._botView) {
        console.log("[BotPanel] Creating BotView");
        this._log('[BotPanel] Creating BotView');
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:394',message:'Before new BotView()',data:{panelVersion:this._panelVersion,hasWebview:!!webview,hasExtensionUri:!!this._extensionUri},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
        // #endregion
        try {
          this._botView = new BotView(this._sharedCLI, this._panelVersion, webview, this._extensionUri);
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:394',message:'After new BotView()',data:{botViewCreated:!!this._botView},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
          // #endregion
          console.log("[BotPanel] BotView created successfully");
          this._log('[BotPanel] BotView created successfully');
        } catch (botViewError) {
          console.error(`[BotPanel] ERROR creating BotView: ${botViewError.message}`);
          console.error(`[BotPanel] ERROR stack: ${botViewError.stack}`);
          this._log(`[BotPanel] ERROR creating BotView: ${botViewError.message}`);
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:394',message:'BotView construction failed',data:{error:botViewError.message,stack:botViewError.stack},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
          // #endregion
          throw botViewError;
        }
      }
      
      // CRITICAL: Refresh data BEFORE rendering to show latest changes
      console.log("[BotPanel] Refreshing bot data...");
      this._log('[BotPanel] Calling _botView.refresh() to fetch latest data');
      await this._botView.refresh();
      this._log('[BotPanel] Data refreshed successfully');
      
      console.log("[BotPanel] Rendering HTML");
      this._log('[BotPanel] _botView.render() starting');
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:405',message:'Before _botView.render()',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      // Render HTML using BotView (async now)
      const html = this._getWebviewContent(await this._botView.render());
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:405',message:'After _botView.render()',data:{htmlLength:html?.length||0},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      
      // Log HTML update details
      const htmlPreview = html.substring(0, 500).replace(/\s+/g, ' ');
      this._log(`[BotPanel] Setting webview HTML (length: ${html.length}, preview: ${htmlPreview}...)`);
      this._log(`[BotPanel] Current HTML length: ${this._lastHtmlLength || 0}, New HTML length: ${html.length}`);
      
      if (this._lastHtmlLength === html.length) {
        this._log('[BotPanel] WARNING: HTML length unchanged - content may not have updated');
      } else {
        this._log('[BotPanel] HTML length changed - update should be visible');
      }
      
      this._lastHtmlLength = html.length;
      this._panel.webview.html = html;
      this._log('[BotPanel] Webview HTML property set');
      console.log("[BotPanel] _update() completed successfully");
      this._log('[BotPanel] _update() completed successfully');
      this._log('[BotPanel] _update() END');
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:407',message:'_update() EXIT success',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
      // #endregion
      
    } catch (err) {
      console.error(`[BotPanel] ERROR in _update: ${err.message}`);
      console.error(`[BotPanel] ERROR stack: ${err.stack}`);
      this._log(`[BotPanel] ERROR in _update: ${err.message} | Stack: ${err.stack}`);
      
      // Show error in VSCode notification
      const errorMsg = err.isCliError 
        ? `CLI Error: ${err.message}` 
        : `Bot Panel Update Error: ${err.message}`;
      vscode.window.showErrorMessage(errorMsg);
      
      // Display error in panel with retry button
      const errorType = err.errorType || err.constructor.name;
      const command = err.command ? `Command: ${this._escapeHtml(err.command)}` : '';
      
      this._panel.webview.html = this._getWebviewContent(`
        <div style="padding: 20px; color: var(--vscode-errorForeground);">
          <h2>⚠️ Error Loading Bot Panel</h2>
          <div style="background: var(--vscode-inputValidation-errorBackground); border: 1px solid var(--vscode-inputValidation-errorBorder); padding: 15px; margin: 10px 0; border-radius: 4px;">
            <p><strong>Error:</strong> ${this._escapeHtml(err.message)}</p>
            ${command ? `<p style="margin-top: 10px;">${command}</p>` : ''}
            ${err.isCliError ? `<p style="margin-top: 10px;"><strong>Type:</strong> ${this._escapeHtml(errorType)}</p>` : ''}
          </div>
          <details style="margin-top: 15px;">
            <summary style="cursor: pointer; color: var(--vscode-textLink-foreground);">Show Stack Trace</summary>
            <pre style="background: var(--vscode-editor-background); padding: 10px; margin-top: 10px; border-radius: 4px; overflow-x: auto;">${this._escapeHtml(err.stack || 'No stack trace available')}</pre>
          </details>
          <div style="margin-top: 20px;">
            <button onclick="vscode.postMessage({ command: 'refresh' })" 
                    style="background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 8px 16px; cursor: pointer; border-radius: 2px; font-size: 13px;">
              🔄 Retry
            </button>
          </div>
          <p style="margin-top: 20px; color: var(--vscode-descriptionForeground); font-size: 12px;">
            Please ensure Python is installed and the bot CLI is available.
          </p>
        </div>
      `);
    }
  }

  _escapeHtml(text) {
    if (typeof text !== 'string') {
      text = String(text);
    }
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }

  _getWebviewContent(contentHtml) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Panel</title>
    <style>
        /* ============================================================
           THEME SYSTEM - All styling variables in one place
           ============================================================ */
        
        :root {
            /* Colors */
            --bg-base: #000000;
            --accent-color: #ff8c00;
            --border-color: #ff8c00;
            --divider-color: #ff8c00;
            --hover-bg: rgba(255, 255, 255, 0.03);
            
            /* Input styling - chat-like appearance */
            --input-bg: rgba(255, 255, 255, 0.05);
            --input-bg-focus: rgba(255, 255, 255, 0.08);
            --input-border: rgba(255, 255, 255, 0.1);
            --input-border-focus: var(--accent-color);
            --input-padding: 6px;
            --input-border-radius: 6px;
            --input-border-width: 1px;
            --input-border-width-focus: 2px;
            --input-header-border-width: 1px;
            --input-header-border-width-focus: 2px;
            --input-transition: border-color 150ms ease, background-color 150ms ease;
            
            /* Borders */
            --border-width: 1px;
            --border-radius: 0;
            --border-radius-sm: 0;
            --active-border-width: 2px;
            
            /* Spacing */
            --space-xs: 2px;
            --space-sm: 4px;
            --space-md: 6px;
            --space-lg: 8px;
            
            /* Typography */
            --font-size-base: 13px;
            --font-size-sm: 12px;
            --font-size-xs: 11px;
            --font-size-section: 14px;
            --font-weight-normal: 400;
            --line-height-base: 1.6;
            --line-height-compact: 1.4;
        }
        
        body {
            font-family: var(--vscode-font-family), 'Segoe UI', sans-serif;
            padding: var(--space-md);
            color: var(--vscode-foreground);
            background-color: var(--bg-base);
            line-height: var(--line-height-base);
            margin: 0;
            font-size: var(--font-size-base);
            font-weight: var(--font-weight-normal);
        }
        
        .bot-view {
            display: flex;
            flex-direction: column;
            gap: 0;
        }
        
        /* ============================================================
           CARDS & SECTIONS
           ============================================================ */
        
        .card-primary {
            margin-bottom: var(--space-lg);
            padding: var(--space-lg) 0;
            border: none;
            border-top: var(--border-width) solid var(--divider-color);
            background-color: transparent;
        }
        
        .card-secondary {
            margin: var(--space-sm) 0;
            padding: var(--space-md) 0;
            border: none;
            background-color: transparent;
        }
        
        .card-item {
            margin: var(--space-xs) 0;
            padding: var(--space-xs) var(--space-sm);
            border-radius: 0;
            background-color: transparent;
            transition: background-color 80ms ease;
        }
        .card-item:hover {
            background-color: var(--hover-bg);
        }
        
        .card-item.active,
        .card-secondary.active {
            background-color: transparent;
        }
        
        .section {
            margin-bottom: 0;
            padding: var(--space-lg) 0;
            border: none;
            border-top: var(--border-width) solid var(--divider-color);
            background-color: transparent;
        }
        
        .section.card-primary {
            border-top: var(--border-width) solid var(--divider-color);
        }
        
        /* ============================================================
           HIERARCHY & COLLAPSIBLE ITEMS
           ============================================================ */
        
        .behavior-item, .action-item, .operation-item {
            margin: var(--space-xs) 0;
            padding: var(--space-xs) var(--space-sm);
            border-radius: var(--border-radius-sm);
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            transition: background-color 80ms ease;
            font-weight: var(--font-weight-normal);
        }
        
        .behavior-item:hover, .action-item:hover {
            background-color: var(--hover-bg);
        }
        
        .collapsible-header {
            margin: var(--space-xs) 0;
            padding: var(--space-sm);
            border-radius: var(--border-radius-sm);
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            cursor: pointer;
            font-weight: var(--font-weight-normal);
            font-size: var(--font-size-base);
            transition: background-color 80ms ease;
        }
        .collapsible-header:hover {
            background-color: var(--hover-bg);
        }
        .collapsible-header.action-item {
            margin-left: 12px;
            font-weight: var(--font-weight-normal);
        }
        .operation-item {
            margin-left: 24px;
            font-size: var(--font-size-sm);
            color: var(--vscode-descriptionForeground);
        }
        .collapsible-content {
            padding-left: 0;
        }
        #behaviors-content .collapsible-content {
            padding-left: 12px;
        }
        #behaviors-content .collapsible-content .collapsible-content {
            padding-left: 12px;
        }
        
        .behavior-item.active,
        .action-item.active,
        .operation-item.active {
            background-color: transparent;
        }
        
        /* ============================================================
           STORY TREE NODE INTERACTION
           ============================================================ */
        
        .story-node {
            padding: 2px 4px;
            border-radius: 3px;
            transition: background-color 150ms ease;
        }
        
        .story-node:hover {
            background-color: rgba(255, 140, 0, 0.15); /* Faded orange on hover */
        }
        
        .story-node.selected {
            background-color: rgba(255, 140, 0, 0.35); /* Distinct orange when selected */
        }
        
        
        .collapsible-section {
            margin-bottom: var(--space-sm);
        }
        
        .collapsible-section .expand-icon {
            transition: transform 150ms ease;
            display: inline-block;
            transform: rotate(0deg);
            font-style: normal;
            min-width: var(--space-md);
            color: #ff8c00 !important;
            font-size: 28px;
            margin-right: 8px;
        }
        .collapsible-section.expanded .expand-icon {
            transform: rotate(90deg);
        }
        /* Ensure nested subsections have smaller icons */
        .collapsible-content .collapsible-section .expand-icon {
            font-size: 20px;
        }
        .collapsible-content {
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .collapsible-content[style*="display: none"] {
            display: none !important;
        }
        
        .status-marker {
            font-family: inherit;
            font-weight: var(--font-weight-normal);
            min-width: 20px;
            font-size: var(--font-size-base);
            display: inline-block;
            margin-right: 4px;
        }
        
        .marker-current {
            color: var(--vscode-textLink-foreground);
        }
        
        .marker-completed {
            color: var(--vscode-textLink-foreground);
        }
        
        .marker-pending {
            color: var(--vscode-descriptionForeground);
        }
        
        .scope-section {
            background-color: transparent;
            padding: 0;
            border: none;
        }
        
        /* ============================================================
           INPUTS & INTERACTIVE ELEMENTS
           ============================================================ */
        
        .input-container {
            border: var(--input-border-width) solid var(--accent-color);
            border-radius: var(--input-border-radius);
            overflow: hidden;
            transition: border-width 150ms ease, border-color 150ms ease, background-color 150ms ease;
        }
        .input-container:focus-within {
            border-width: var(--input-border-width-focus);
        }
        
        .input-header {
            padding: 4px var(--input-padding);
            background-color: transparent;
            border-bottom: var(--input-header-border-width) solid var(--accent-color);
            font-size: var(--font-size-base);
            color: var(--vscode-foreground);
            font-weight: 600;
            transition: border-bottom-width 150ms ease;
        }
        .input-container:focus-within .input-header {
            border-bottom-width: var(--input-header-border-width-focus);
        }
        
        .info-display {
            padding: var(--space-sm) 0;
            font-size: var(--font-size-base);
            color: var(--vscode-foreground);
        }
        .info-display .label {
            color: var(--vscode-descriptionForeground);
            margin-right: 8px;
        }
        .info-display .value {
            color: var(--vscode-foreground);
        }
        
        .main-header {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 7px 5px 6px 5px;
            border-bottom: 1px solid var(--divider-color);
        }
        .main-header-icon {
            width: 28px;
            height: 28px;
            object-fit: contain;
        }
        .main-header-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--vscode-foreground);
        }
        .main-header-refresh {
            margin-left: auto;
            background-color: transparent;
            border: none;
            color: var(--vscode-foreground);
            font-size: 18px;
            padding: 3px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 150ms ease;
        }
        .main-header-refresh:hover {
            background-color: rgba(255, 140, 0, 0.1);
        }
        
        input[type="text"],
        textarea,
        .text-input {
            width: 100%;
            padding: var(--space-sm) var(--input-padding);
            background-color: var(--input-bg);
            color: var(--vscode-foreground);
            border: none;
            border-radius: 0;
            font-family: var(--vscode-editor-font-family, 'Segoe UI', sans-serif);
            font-size: var(--font-size-base);
        }
        input[type="text"]:focus,
        textarea:focus,
        .text-input:focus {
            outline: none;
        }
        
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: var(--space-xs) var(--space-md);
            cursor: pointer;
            border-radius: var(--border-radius-sm);
            font-size: var(--font-size-base);
            font-family: inherit;
            transition: all 100ms ease;
        }
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        button:active {
            background-color: var(--vscode-button-background);
            opacity: 0.8;
            transform: scale(0.98);
        }
        
        a {
            color: var(--vscode-textLink-foreground);
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .bot-links {
            display: flex;
            gap: var(--space-md);
            flex-wrap: wrap;
            align-items: center;
        }
        .bot-link {
            font-size: var(--font-size-base);
            cursor: pointer;
            text-decoration: underline;
            color: var(--vscode-descriptionForeground);
            opacity: 0.6;
        }
        .bot-link.active {
            color: var(--vscode-foreground);
            font-weight: var(--font-weight-normal);
            text-decoration: none;
            cursor: default;
            opacity: 1;
        }
        .bot-link:not(.active):hover {
            opacity: 0.8;
        }
        
        .empty-state {
            color: var(--vscode-descriptionForeground);
            font-style: italic;
            padding: var(--space-sm);
        }
    </style>
</head>
<body>
    ${contentHtml}
    
    <script>
        const vscode = acquireVsCodeApi();
        console.log('[WebView] ========== SCRIPT LOADING ==========');
        console.log('[WebView] vscode API acquired:', !!vscode);
        console.log('[WebView] vscode.postMessage available:', typeof vscode.postMessage);
        
        // Restore collapse state and selected node when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            try {
                // Restore collapse state
                const savedState = sessionStorage.getItem('collapseState');
                if (savedState) {
                    const state = JSON.parse(savedState);
                    // Use setTimeout to ensure DOM is fully rendered
                    setTimeout(() => window.restoreCollapseState(state), 50);
                    console.log('[WebView] Restored collapse state for', Object.keys(state).length, 'nodes');
                }
                
                // Restore selected node
                const savedSelection = sessionStorage.getItem('selectedNode');
                if (savedSelection) {
                    const selection = JSON.parse(savedSelection);
                    setTimeout(() => {
                        if (window.selectNode) {
                            window.selectNode(selection.type, selection.name, selection);
                            console.log('[WebView] Restored selection for', selection.name);
                        }
                    }, 100);
                }
            } catch (err) {
                console.error('[WebView] Error restoring state:', err);
            }
        });
        
        // Global click handler using event delegation (CSP blocks inline onclick)
        document.addEventListener('click', function(e) {
            const target = e.target;
            const targetInfo = {
                tagName: target.tagName,
                className: target.className,
                id: target.id,
                nodeType: target.getAttribute && target.getAttribute('data-node-type'),
                nodeName: target.getAttribute && target.getAttribute('data-node-name')
            };
            console.log('[WebView] CLICK DETECTED:', targetInfo);
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] CLICK: ' + JSON.stringify(targetInfo)
            });
            
            // Handle story node clicks (epic, sub-epic, story)
            if (target.classList.contains('story-node')) {
                console.log('═══════════════════════════════════════════════════════');
                console.log('[WebView] STORY NODE CLICKED');
                const nodeType = target.getAttribute('data-node-type');
                const nodeName = target.getAttribute('data-node-name');
                const hasChildren = target.getAttribute('data-has-children') === 'true';
                const hasStories = target.getAttribute('data-has-stories') === 'true';
                const hasNestedSubEpics = target.getAttribute('data-has-nested-sub-epics') === 'true';
                const nodePath = target.getAttribute('data-path');
                const fileLink = target.getAttribute('data-file-link');
                
                console.log('[WebView]   nodeType:', nodeType);
                console.log('[WebView]   nodeName:', nodeName);
                console.log('[WebView]   hasChildren:', hasChildren);
                console.log('[WebView]   hasStories:', hasStories);
                console.log('[WebView]   hasNestedSubEpics:', hasNestedSubEpics);
                console.log('[WebView]   nodePath:', nodePath);
                console.log('[WebView]   fileLink:', fileLink);
                
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] Story node clicked: type=' + nodeType + ', name=' + nodeName + ', path=' + nodePath
                });
                
                // Call selectNode
                if (window.selectNode && nodeType && nodeName !== null) {
                    const options = {
                        hasChildren: hasChildren,
                        hasStories: hasStories,
                        hasNestedSubEpics: hasNestedSubEpics,
                        path: nodePath
                    };
                    console.log('[WebView]   Calling selectNode with options:', JSON.stringify(options, null, 2));
                    window.selectNode(nodeType, nodeName, options);
                }
                
                // Call openFile if there's a file link
                if (window.openFile && fileLink) {
                    console.log('[WebView]   Opening file:', fileLink);
                    window.openFile(fileLink);
                }
                
                e.stopPropagation();
                console.log('═══════════════════════════════════════════════════════');
            }
        }, true); // Use capture phase to catch all clicks
        
        // Handle double-click on story nodes to enable edit mode
        document.addEventListener('dblclick', function(e) {
            const target = e.target;
            
            // Handle story node double-clicks (epic, sub-epic, story)
            if (target.classList.contains('story-node')) {
                const nodePath = target.getAttribute('data-path');
                const nodeName = target.getAttribute('data-node-name');
                
                console.log('[WebView] DOUBLE-CLICK on story node:', nodeName, 'path:', nodePath);
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] Double-click on node: ' + nodeName + ', path: ' + nodePath
                });
                
                if (nodePath && window.enableEditMode) {
                    window.enableEditMode(nodePath);
                }
                
                e.stopPropagation();
                e.preventDefault();
            }
        }, true); // Use capture phase to catch all double-clicks
        
        // Handle drag and drop for moving nodes
        let draggedNode = null;
        let dropIndicator = null;
        let currentDropZone = null; // 'before', 'after', or 'inside'
        
        // Create drop indicator line
        function createDropIndicator() {
            if (!dropIndicator) {
                dropIndicator = document.createElement('div');
                dropIndicator.style.position = 'fixed';
                dropIndicator.style.height = '2px';
                dropIndicator.style.backgroundColor = 'rgb(255, 140, 0)'; // Orange to match UI
                dropIndicator.style.pointerEvents = 'none';
                dropIndicator.style.zIndex = '10000';
                dropIndicator.style.transition = 'all 0.1s ease';
                dropIndicator.style.display = 'none'; // Start hidden
                document.body.appendChild(dropIndicator);
            }
            return dropIndicator;
        }
        
        function removeDropIndicator() {
            if (dropIndicator && dropIndicator.parentNode) {
                dropIndicator.parentNode.removeChild(dropIndicator);
                dropIndicator = null;
            }
            currentDropZone = null;
        }
        
        document.addEventListener('dragstart', function(e) {
            console.log('[WebView] DRAGSTART EVENT FIRED');
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] DRAGSTART EVENT - target classList: ' + (e.target.classList ? Array.from(e.target.classList).join(', ') : 'none')
            });
            
            // Find the story-node element (might be dragging a child element)
            let target = e.target;
            while (target && !target.classList.contains('story-node')) {
                target = target.parentElement;
            }
            
            if (target && target.classList.contains('story-node')) {
                draggedNode = {
                    path: target.getAttribute('data-path'),
                    name: target.getAttribute('data-node-name'),
                    type: target.getAttribute('data-node-type')
                };
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', draggedNode.path);
                target.style.opacity = '0.5';
                console.log('[WebView] Drag started:', draggedNode);
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] DRAG STARTED: ' + JSON.stringify(draggedNode)
                });
            } else {
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] DRAGSTART ignored - not a story-node'
                });
            }
        }, true);
        
        document.addEventListener('dragend', function(e) {
            console.log('[WebView] DRAGEND EVENT FIRED');
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] DRAGEND EVENT'
            });
            
            // Find the story-node element
            let target = e.target;
            while (target && !target.classList.contains('story-node')) {
                target = target.parentElement;
            }
            
            if (target && target.classList.contains('story-node')) {
                target.style.opacity = '1';
                draggedNode = null;
                removeDropIndicator();
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] Drag ended, cleared draggedNode'
                });
            }
        }, true);
        
        let dragoverLogCounter = 0; // Throttle dragover logs
        document.addEventListener('dragover', function(e) {
            // Find the story-node element
            let target = e.target;
            let searchDepth = 0;
            while (target && !target.classList.contains('story-node') && searchDepth < 10) {
                target = target.parentElement;
                searchDepth++;
            }
            
            // Log every 20th dragover event to avoid spam
            if (dragoverLogCounter++ % 20 === 0 && draggedNode) {
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] DRAGOVER - found target: ' + (target ? 'YES' : 'NO') + ', draggedNode: ' + (draggedNode ? draggedNode.name : 'null')
                });
            }
            
            if (target && target.classList.contains('story-node') && draggedNode) {
                const targetType = target.getAttribute('data-node-type');
                const targetPath = target.getAttribute('data-path');
                const targetName = target.getAttribute('data-node-name');
                
                // Don't allow dropping on self
                if (draggedNode.path === targetPath) {
                    removeDropIndicator();
                    return;
                }
                
                // Check if target can contain dragged node
                const canContain = (targetType === 'epic' && draggedNode.type === 'sub-epic') ||
                                  (targetType === 'sub-epic' && (draggedNode.type === 'sub-epic' || draggedNode.type === 'story')) ||
                                  (targetType === 'story' && draggedNode.type === 'scenario');
                
                // Check if nodes are same type for reordering
                const sameType = draggedNode.type === targetType;
                
                if (canContain || sameType) {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    
                    // Get mouse position relative to target element
                    const rect = target.getBoundingClientRect();
                    const mouseY = e.clientY;
                    const targetTop = rect.top;
                    const targetHeight = rect.height;
                    const relativeY = mouseY - targetTop;
                    const percentY = relativeY / targetHeight;
                    
                    // Determine drop zone based on mouse position
                    let dropZone;
                    const indicator = createDropIndicator();
                    
                    // Check if target can contain the dragged node
                    const hasStories = target.getAttribute('data-has-stories') === 'true';
                    const hasNestedSubEpics = target.getAttribute('data-has-nested-sub-epics') === 'true';
                    const isEmptyContainer = !hasStories && !hasNestedSubEpics;
                    
                    // "ON" vs "AFTER" logic:
                    // - If hovering directly on item (middle 60%) AND can nest inside: show "inside" (orange background, no line)
                    // - Otherwise: show "after" (orange line below item)
                    if (canContain && percentY >= 0.2 && percentY <= 0.8) {
                        // Hovering ON the item - nest inside
                        dropZone = 'inside';
                        target.style.backgroundColor = 'rgba(255, 140, 0, 0.3)'; // Orange tint for nesting
                        indicator.style.display = 'none';
                        if (dragoverLogCounter % 20 === 0) {
                            vscode.postMessage({
                                command: 'logToFile',
                                message: '[WebView] DRAGOVER ON (inside) - will nest inside ' + target.getAttribute('data-node-name')
                            });
                        }
                    } else if (sameType) {
                        // Same type: insert after
                        dropZone = 'after';
                        target.style.backgroundColor = '';
                        indicator.style.display = 'block';
                        indicator.style.left = rect.left + 'px';
                        indicator.style.top = (rect.top + rect.height) + 'px';
                        indicator.style.width = rect.width + 'px';
                        // Log indicator positioning
                        if (dragoverLogCounter % 20 === 0) {
                            vscode.postMessage({
                                command: 'logToFile',
                                message: '[WebView] DRAGOVER AFTER - hovering over: "' + targetName + '", line at y=' + (rect.top + rect.height) + ' (BOTTOM of node), will insert AFTER this node'
                            });
                        }
                    } else {
                        vscode.postMessage({
                            command: 'logToFile',
                            message: '[WebView] DRAGOVER INVALID - canContain: ' + canContain + ', sameType: ' + sameType + ', dragging ' + draggedNode.type + ' onto ' + targetType
                        });
                        removeDropIndicator();
                        return;
                    }
                    
                    currentDropZone = dropZone;
                } else {
                    removeDropIndicator();
                }
            } else {
                removeDropIndicator();
            }
        }, true);
        
        document.addEventListener('dragleave', function(e) {
            // Find the story-node element
            let target = e.target;
            while (target && !target.classList.contains('story-node')) {
                target = target.parentElement;
            }
            
            if (target && target.classList.contains('story-node')) {
                target.style.backgroundColor = '';
            }
        }, true);
        
        document.addEventListener('drop', function(e) {
            console.log('[WebView] ===== DROP EVENT FIRED =====');
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] ===== DROP EVENT FIRED ===== draggedNode: ' + (draggedNode ? draggedNode.name : 'null') + ', currentDropZone: ' + (currentDropZone || 'null')
            });
            
            // Find the story-node element (might be dropping on a child element)
            let target = e.target;
            while (target && !target.classList.contains('story-node')) {
                target = target.parentElement;
            }
            
            if (target && target.classList.contains('story-node') && draggedNode && currentDropZone) {
                e.preventDefault();
                e.stopPropagation();
                target.style.backgroundColor = '';
                
                // Save dropZone BEFORE removeDropIndicator clears it
                const dropZone = currentDropZone;
                removeDropIndicator();
                
                const targetPath = target.getAttribute('data-path');
                const targetName = target.getAttribute('data-node-name');
                const targetType = target.getAttribute('data-node-type');
                
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] DROP on story-node - dragged: ' + draggedNode.name + ' onto: ' + targetName + ', dropZone: ' + dropZone
                });
                
                if (draggedNode.path !== targetPath) {
                    console.log('[WebView] Drop detected:', {
                        dragged: draggedNode,
                        target: { path: targetPath, name: targetName, type: targetType },
                        dropZone: dropZone
                    });
                    
                    // OPTIMISTIC UPDATE: Move DOM element immediately
                    // Find the dragged element's parent container (the div that contains the node)
                    const draggedElements = document.querySelectorAll('.story-node');
                    let draggedElement = null;
                    for (const el of draggedElements) {
                        if (el.getAttribute('data-path') === draggedNode.path) {
                            draggedElement = el;
                            break;
                        }
                    }
                    
                    if (draggedElement) {
                        // Find the parent div container for the dragged node
                        let draggedContainer = draggedElement.parentElement;
                        while (draggedContainer && !draggedContainer.style.marginLeft && draggedContainer.parentElement) {
                            draggedContainer = draggedContainer.parentElement;
                        }
                        
                        // Perform optimistic DOM move
                        if (dropZone === 'inside') {
                            // Move inside: append to target's collapsible content
                            const targetCollapsible = target.parentElement.nextElementSibling;
                            if (targetCollapsible && targetCollapsible.classList.contains('collapsible-content')) {
                                console.log('[WebView] Optimistically moving inside target container');
                                targetCollapsible.appendChild(draggedContainer);
                            }
                        } else if (dropZone === 'after') {
                            // Move after: insert after target's container
                            let targetContainer = target.parentElement;
                            while (targetContainer && !targetContainer.style.marginLeft && targetContainer.parentElement) {
                                targetContainer = targetContainer.parentElement;
                            }
                            if (targetContainer && targetContainer.parentElement) {
                                console.log('[WebView] Optimistically moving after target');
                                targetContainer.parentElement.insertBefore(draggedContainer, targetContainer.nextSibling);
                            }
                        }
                    }
                    
                    let command;
                    
                    if (dropZone === 'inside') {
                        // ON: Nest inside the target container
                        command = draggedNode.path + '.move_to target:"' + targetName + '"';
                        vscode.postMessage({
                            command: 'logToFile',
                            message: '[WebView] ON - NEST inside container: ' + targetName
                        });
                    } else if (dropZone === 'after') {
                        var targetPos = parseInt(target.getAttribute('data-position') || '0');
                        var parentMatch = targetPath.match(/(.*)\."[^"]+"/);
                        var parentName = parentMatch ? parentMatch[1].match(/\."([^"]+)"$/)[1] : 'story_graph';
                        command = draggedNode.path + '.move_to target:"' + parentName + '" at_position:' + targetPos;
                        vscode.postMessage({
                            command: 'logToFile',
                            message: '[WebView] AFTER - at_position: ' + targetPos + ' in ' + parentName
                        });
                    }
                    
                    console.log('[WebView] Move command:', command);
                    vscode.postMessage({
                        command: 'logToFile',
                        message: '[WebView] SENDING MOVE COMMAND (optimistic update already applied): ' + command
                    });
                    
                    vscode.postMessage({
                        command: 'executeCommand',
                        commandText: command
                    });
                } else {
                    vscode.postMessage({
                        command: 'logToFile',
                        message: '[WebView] DROP ignored - same node'
                    });
                }
            } else {
                removeDropIndicator();
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] DROP ignored - not story-node, no draggedNode, or no dropZone'
                });
            }
        }, true);
        
        // Test if onclick handlers can access functions
        window.testFunction = function() {
            console.log('[WebView] TEST FUNCTION CALLED - functions are accessible!');
            alert('Test function works!');
        };
        console.log('[WebView] window.testFunction defined:', typeof window.testFunction);
        
        window.toggleSection = function(sectionId) {
            console.log('[toggleSection] Called with sectionId:', sectionId);
            const content = document.getElementById(sectionId);
            console.log('[toggleSection] Content element:', content);
            if (content) {
                const section = content.closest('.collapsible-section');
                console.log('[toggleSection] Parent section:', section);
                const isExpanded = section && section.classList.contains('expanded');
                console.log('[toggleSection] isExpanded:', isExpanded);
                
                // Toggle visibility
                if (isExpanded) {
                    // Collapsing
                    content.style.maxHeight = '0px';
                    content.style.display = 'none';
                } else {
                    // Expanding
                    content.style.maxHeight = '2000px';
                    content.style.display = 'block';
                }
                
                // Toggle expanded class (CSS handles icon rotation - ▸ rotates 90deg when expanded)
                const header = content.previousElementSibling;
                console.log('[toggleSection] Header element:', header);
                if (header && section) {
                    section.classList.toggle('expanded', !isExpanded);
                    console.log('[toggleSection] After toggle, section classes:', section.className);
                    // Keep icon as ▸ always - CSS rotation handles the visual state
                    const icon = header.querySelector('.expand-icon');
                    console.log('[toggleSection] Icon element:', icon);
                    if (icon) {
                        icon.textContent = '▸';
                        console.log('[toggleSection] Icon transform:', window.getComputedStyle(icon).transform);
                    }
                }
            }
        };
        
        // Save/restore collapse state across panel refreshes
        window.getCollapseState = function() {
            const state = {};
            document.querySelectorAll('.collapsible-content').forEach(content => {
                if (content.id) {
                    state[content.id] = content.style.display !== 'none';
                }
            });
            return state;
        };
        
        window.restoreCollapseState = function(state) {
            if (!state) return;
            Object.keys(state).forEach(id => {
                const content = document.getElementById(id);
                if (content) {
                    const shouldBeExpanded = state[id];
                    content.style.display = shouldBeExpanded ? 'block' : 'none';
                    
                    // Update icon
                    const header = content.previousElementSibling;
                    if (header) {
                        const icon = header.querySelector('span[id$="-icon"]');
                        if (icon) {
                            const plusSrc = icon.getAttribute('data-plus');
                            const subtractSrc = icon.getAttribute('data-subtract');
                            if (plusSrc && subtractSrc) {
                                const img = icon.querySelector('img');
                                if (img) {
                                    img.src = shouldBeExpanded ? subtractSrc : plusSrc;
                                }
                            }
                        }
                    }
                }
            });
        };
        
        window.toggleCollapse = function(elementId) {
            const content = document.getElementById(elementId);
            if (content) {
                const isHidden = content.style.display === 'none';
                content.style.display = isHidden ? 'block' : 'none';
                
                const header = content.previousElementSibling;
                if (header) {
                    const icon = header.querySelector('span[id$="-icon"]');
                    if (icon) {
                        // Update image src instead of text content - no emojis
                        const plusSrc = icon.getAttribute('data-plus');
                        const subtractSrc = icon.getAttribute('data-subtract');
                        if (plusSrc && subtractSrc) {
                            const img = icon.querySelector('img');
                            if (img) {
                                img.src = isHidden ? subtractSrc : plusSrc;
                            } else {
                                // Create img if it doesn't exist
                                const imgSrc = isHidden ? subtractSrc : plusSrc;
                                const imgAlt = isHidden ? 'Collapse' : 'Expand';
                                icon.innerHTML = '<img src="' + imgSrc + '" style="width: 12px; height: 12px; vertical-align: middle;" alt="' + imgAlt + '" />';
                            }
                        }
                    }
                }
                
                // Save state to sessionStorage
                const currentState = window.getCollapseState();
                sessionStorage.setItem('collapseState', JSON.stringify(currentState));
            }
        };
        
        window.openFile = function(filePath) {
            console.log('[WebView] openFile called with:', filePath);
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] openFile called with: ' + filePath
            });
            vscode.postMessage({
                command: 'openFile',
                filePath: filePath
            });
        };
        
        window.updateFilter = function(filterValue) {
            console.log('[WebView] updateFilter called with:', filterValue);
            const message = {
                command: 'updateFilter',
                filter: filterValue
            };
            console.log('[WebView] Sending message:', message);
            vscode.postMessage(message);
            console.log('[WebView] postMessage sent');
        };
        
        // Test if updateFilter is defined
        console.log('[WebView] updateFilter function exists:', typeof updateFilter);
        
        window.clearScopeFilter = function() {
            vscode.postMessage({
                command: 'clearScopeFilter'
            });
        };
        
        window.showAllScope = function() {
            console.log('[WebView] showAllScope called');
            vscode.postMessage({
                command: 'showAllScope'
            });
        };
        
        window.executeNavigationCommand = function(command) {
            console.log('[WebView] executeNavigationCommand click ->', command);
            vscode.postMessage({
                command: 'executeNavigationCommand',
                commandText: command
            });
        };
        
        window.navigateToBehavior = function(behaviorName) {
            console.log('[WebView] navigateToBehavior click ->', behaviorName);
            vscode.postMessage({
                command: 'navigateToBehavior',
                behaviorName: behaviorName
            });
        };
        
        window.navigateToAction = function(behaviorName, actionName) {
            console.log('[WebView] navigateToAction click ->', behaviorName, actionName);
            vscode.postMessage({
                command: 'navigateToAction',
                behaviorName: behaviorName,
                actionName: actionName
            });
        };
        
        window.navigateAndExecute = function(behaviorName, actionName, operationName) {
            console.log('[WebView] navigateAndExecute click ->', behaviorName, actionName, operationName);
            vscode.postMessage({
                command: 'navigateAndExecute',
                behaviorName: behaviorName,
                actionName: actionName,
                operationName: operationName
            });
        };
        
        function submitToChat() {
            vscode.postMessage({
                command: 'sendToChat'
            });
        }

        function sendInstructionsToChat(event) {
            if (event) {
                event.stopPropagation();
            }
            console.log('[WebView] sendInstructionsToChat triggered');
            const promptContent = window._promptContent || '';
            if (!promptContent) {
                console.warn('[WebView] No prompt content available to submit');
                return;
            }
            vscode.postMessage({
                command: 'sendToChat',
                content: promptContent
            });
        }

        function refreshStatus() {
            vscode.postMessage({
                command: 'refresh'
            });
        }
        
        function updateWorkspace(workspacePath) {
            console.log('[WebView] updateWorkspace called with:', workspacePath);
            vscode.postMessage({
                command: 'updateWorkspace',
                workspacePath: workspacePath
            });
        }
        
        window.switchBot = function(botName) {
            console.log('[WebView] switchBot called with:', botName);
            vscode.postMessage({
                command: 'switchBot',
                botName: botName
            });
        };
        
        window.getBehaviorRules = function(behaviorName) {
            console.log('[WebView] getBehaviorRules called with:', behaviorName);
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] getBehaviorRules BUTTON CLICKED for: ' + behaviorName
            });
            vscode.postMessage({
                command: 'getBehaviorRules',
                behaviorName: behaviorName
            });
        };
        
        // Story Graph Edit functions
        window.createEpic = function() {
            console.log('═══════════════════════════════════════════════════════');
            console.log('[WebView] createEpic CALLED');
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] createEpic called'
            });
            console.log('[WebView] SENDING COMMAND: story_graph.create_epic');
            vscode.postMessage({
                command: 'executeCommand',
                commandText: 'story_graph.create_epic'
            });
            console.log('[WebView] postMessage sent successfully');
            console.log('═══════════════════════════════════════════════════════');
        };
        
        window.createSubEpic = function(parentName) {
            console.log('[WebView] createSubEpic called for:', parentName);
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`story_graph."\${parentName}".create\`
            });
        };
        
        window.createStory = function(parentName) {
            console.log('[WebView] createStory called for:', parentName);
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`story_graph."\${parentName}".create_story\`
            });
        };
        
        window.createScenario = function(storyName) {
            console.log('[WebView] createScenario called for:', storyName);
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`story_graph."\${storyName}".create_scenario\`
            });
        };
        
        window.createScenarioOutline = function(storyName) {
            console.log('[WebView] createScenarioOutline called for:', storyName);
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`story_graph."\${storyName}".create_scenario_outline\`
            });
        };
        
        window.createAcceptanceCriteria = function(storyName) {
            console.log('[WebView] createAcceptanceCriteria called for:', storyName);
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`story_graph."\${storyName}".create_acceptance_criteria\`
            });
        };
        
        window.deleteNode = function(nodePath) {
            console.log('[WebView] deleteNode called for:', nodePath);
            
            // OPTIMISTIC UPDATE: Remove from DOM immediately
            const nodes = document.querySelectorAll('.story-node');
            for (const node of nodes) {
                if (node.getAttribute('data-path') === nodePath) {
                    // Find the container div (parent that has the full node structure)
                    let container = node.parentElement;
                    while (container && !container.style.marginLeft && !container.style.marginTop && container.parentElement) {
                        container = container.parentElement;
                    }
                    if (container) {
                        console.log('[WebView] Optimistically removing node container');
                        container.style.opacity = '0.5';
                        container.style.transition = 'opacity 0.2s';
                        setTimeout(() => {
                            if (container.parentElement) {
                                container.parentElement.removeChild(container);
                            }
                        }, 200);
                    }
                    break;
                }
            }
            
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`\${nodePath}.delete\`
            });
        };
        
        window.deleteNodeIncludingChildren = function(nodePath) {
            console.log('[WebView] deleteNodeIncludingChildren called for:', nodePath);
            
            // OPTIMISTIC UPDATE: Remove from DOM immediately
            const nodes = document.querySelectorAll('.story-node');
            for (const node of nodes) {
                if (node.getAttribute('data-path') === nodePath) {
                    // Find the container div (parent that has the full node structure)
                    let container = node.parentElement;
                    while (container && !container.style.marginLeft && !container.style.marginTop && container.parentElement) {
                        container = container.parentElement;
                    }
                    if (container) {
                        console.log('[WebView] Optimistically removing node container with children');
                        container.style.opacity = '0.5';
                        container.style.transition = 'opacity 0.2s';
                        setTimeout(() => {
                            if (container.parentElement) {
                                container.parentElement.removeChild(container);
                            }
                        }, 200);
                    }
                    break;
                }
            }
            
            vscode.postMessage({
                command: 'executeCommand',
                commandText: \`\${nodePath}.delete_including_children\`
            });
        };
        
        window.enableEditMode = function(nodePath) {
            console.log('[WebView] enableEditMode called for:', nodePath);
            // Extract the current node name from the path
            // Path format: story_graph."Epic"."SubEpic"."Story"
            const matches = nodePath.match(/"([^"]+)"[^"]*$/);
            const currentName = matches ? matches[1] : '';
            
            console.log('[WebView] Double-click detected on node:', nodePath, 'currentName:', currentName);
            vscode.postMessage({
                command: 'renameNode',
                nodePath: nodePath,
                currentName: currentName
            });
        };
        
        // Track selected node for contextual actions (initialize window.selectedNode)
        window.selectedNode = {
            type: 'root', // root, epic, sub-epic, story
            name: null,
            path: null, // Full path like story_graph."Epic"."SubEpic"
            canHaveSubEpic: false,
            canHaveStory: false,
            canHaveTests: false,
            hasChildren: false,
            hasStories: false,
            hasNestedSubEpics: false
        };
        
        // Map behavior names from backend to tooltip text (global function)
        window.behaviorToTooltipText = function(behavior) {
            var behaviorMap = {
                'shape': 'Shape',
                'exploration': 'Explore',
                'scenarios': 'Write Scenarios for',
                'tests': 'Write Tests for',
                'code': 'Write Code for'
            };
            return behaviorMap[behavior] || 'Submit';
        };
        
        // Update contextual action buttons based on selection
        window.updateContextualButtons = function() {
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] updateContextualButtons called, selectedNode=' + JSON.stringify(window.selectedNode)
            });
            
            const btnCreateEpic = document.getElementById('btn-create-epic');
            const btnCreateSubEpic = document.getElementById('btn-create-sub-epic');
            const btnCreateStory = document.getElementById('btn-create-story');
            const btnCreateScenario = document.getElementById('btn-create-scenario');
            const btnCreateAcceptanceCriteria = document.getElementById('btn-create-acceptance-criteria');
            const btnDelete = document.getElementById('btn-delete');
            const btnScopeTo = document.getElementById('btn-scope-to');
            const btnSubmit = document.getElementById('btn-submit');
            
            // Hide all buttons first
            if (btnCreateEpic) btnCreateEpic.style.display = 'none';
            if (btnCreateSubEpic) btnCreateSubEpic.style.display = 'none';
            if (btnCreateStory) btnCreateStory.style.display = 'none';
            if (btnCreateScenario) btnCreateScenario.style.display = 'none';
            if (btnCreateAcceptanceCriteria) btnCreateAcceptanceCriteria.style.display = 'none';
            if (btnDelete) btnDelete.style.display = 'none';
            if (btnScopeTo) btnScopeTo.style.display = 'none';
            if (btnSubmit) btnSubmit.style.display = 'none';
            
            // Show buttons based on selection
            if (window.selectedNode.type === 'root') {
                if (btnCreateEpic) btnCreateEpic.style.display = 'block';
            } else if (window.selectedNode.type === 'epic') {
                if (btnCreateSubEpic) btnCreateSubEpic.style.display = 'block';
                if (btnDelete) btnDelete.style.display = 'block';
                if (btnScopeTo) btnScopeTo.style.display = 'block';
                if (btnSubmit) {
                    btnSubmit.style.display = 'block';
                    btnSubmit.setAttribute('title', 'Loading...');
                    
                    // Ask backend for behavior determination
                    vscode.postMessage({
                        command: 'analyzeNode',
                        nodeName: window.selectedNode.name,
                        nodeType: window.selectedNode.type
                    });
                }
            } else if (window.selectedNode.type === 'sub-epic') {
                // Sub-epics can have EITHER sub-epics OR stories, not both
                // If it has stories, only show create story button
                // If it has sub-epics, only show create sub-epic button
                // If empty, show both options
                if (window.selectedNode.hasStories) {
                    // Has stories - only allow adding more stories
                    if (btnCreateStory) btnCreateStory.style.display = 'block';
                } else if (window.selectedNode.hasNestedSubEpics) {
                    // Has nested sub-epics - only allow adding more sub-epics
                    if (btnCreateSubEpic) btnCreateSubEpic.style.display = 'block';
                } else {
                    // Empty - show both options
                    if (btnCreateSubEpic) btnCreateSubEpic.style.display = 'block';
                    if (btnCreateStory) btnCreateStory.style.display = 'block';
                }
                if (btnDelete) btnDelete.style.display = 'block';
                if (btnScopeTo) btnScopeTo.style.display = 'block';
                if (btnSubmit) {
                    btnSubmit.style.display = 'block';
                    btnSubmit.setAttribute('title', 'Loading...');
                    
                    // Ask backend for behavior determination
                    vscode.postMessage({
                        command: 'analyzeNode',
                        nodeName: window.selectedNode.name,
                        nodeType: window.selectedNode.type
                    });
                }
            } else if (window.selectedNode.type === 'story') {
                // Stories can have both scenarios and acceptance criteria
                if (btnCreateScenario) btnCreateScenario.style.display = 'block';
                if (btnCreateAcceptanceCriteria) btnCreateAcceptanceCriteria.style.display = 'block';
                if (btnDelete) btnDelete.style.display = 'block';
                if (btnScopeTo) btnScopeTo.style.display = 'block';
                if (btnSubmit) {
                    btnSubmit.style.display = 'block';
                    btnSubmit.setAttribute('title', 'Loading...');
                    
                    // Ask backend for behavior determination
                    vscode.postMessage({
                        command: 'analyzeNode',
                        nodeName: window.selectedNode.name,
                        nodeType: window.selectedNode.type
                    });
                }
            } else if (window.selectedNode.type === 'scenario') {
                // Scenarios can also be scoped to
                if (btnDelete) btnDelete.style.display = 'block';
                if (btnScopeTo) btnScopeTo.style.display = 'block';
            }
        };
        
        // Select a node (called when clicking on node name/icon)
        window.selectNode = function(type, name, options = {}) {
            console.log('═══════════════════════════════════════════════════════');
            console.log('[WebView] selectNode CALLED');
            console.log('[WebView]   type:', type);
            console.log('[WebView]   name:', name);
            console.log('[WebView]   options:', JSON.stringify(options, null, 2));
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] selectNode: type=' + type + ', name=' + name + ', options=' + JSON.stringify(options)
            });
            
            // Remove selected class from all nodes
            document.querySelectorAll('.story-node.selected').forEach(node => {
                node.classList.remove('selected');
            });
            
            // Add selected class to the clicked node
            let targetNode = null;
            
            // First try to find by path if available (more specific for nested nodes)
            if (options.path) {
                const allNodes = document.querySelectorAll('.story-node[data-path]');
                for (const node of allNodes) {
                    if (node.getAttribute('data-path') === options.path) {
                        targetNode = node;
                        console.log('[WebView]   Found node by path:', options.path);
                        break;
                    }
                }
            }
            
            // Fallback to name+type if path not found
            if (!targetNode) {
                const nodeName = name || 'Story Map';
                targetNode = document.querySelector(\`.story-node[data-node-type="\${type}"][data-node-name="\${nodeName}"]\`);
                console.log('[WebView]   Found node by type+name:', type, nodeName);
            }
            
            if (targetNode) {
                targetNode.classList.add('selected');
                console.log('[WebView]   Added selected class to node');
            } else {
                console.log('[WebView]   WARNING: Target node not found');
            }
            
            window.selectedNode = {
                type: type,
                name: name,
                path: options.path || null,
                canHaveSubEpic: options.canHaveSubEpic || false,
                canHaveStory: options.canHaveStory || false,
                canHaveTests: options.canHaveTests || false,
                hasChildren: options.hasChildren || false,
                hasStories: options.hasStories || false,
                hasNestedSubEpics: options.hasNestedSubEpics || false
            };
            console.log('[WebView]   window.selectedNode updated:', JSON.stringify(window.selectedNode, null, 2));
            
            // Save selection to sessionStorage
            try {
                sessionStorage.setItem('selectedNode', JSON.stringify(window.selectedNode));
            } catch (err) {
                console.error('[WebView] Error saving selection:', err);
            }
            
            window.updateContextualButtons();
            console.log('[WebView]   updateContextualButtons called');
            console.log('═══════════════════════════════════════════════════════');
        };
        
        // Handle contextual create actions
        window.handleContextualCreate = function(actionType) {
            console.log('═══════════════════════════════════════════════════════');
            console.log('[WebView] handleContextualCreate CALLED');
            console.log('[WebView]   actionType:', actionType);
            console.log('[WebView]   window.selectedNode:', JSON.stringify(window.selectedNode, null, 2));
            
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] handleContextualCreate: ' + actionType + ' | selectedNode: ' + JSON.stringify(window.selectedNode)
            });
            
            if (!window.selectedNode.name) {
                console.error('[WebView] ERROR: No node name for contextual create');
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] ERROR: No node name for contextual create'
                });
                return;
            }
            
            // Validate path: must contain node name, not just "story_graph."
            const hasValidPath = window.selectedNode.path && 
                                window.selectedNode.path.length > 'story_graph.'.length &&
                                window.selectedNode.path.includes(window.selectedNode.name);
            
            console.log('[WebView]   path:', window.selectedNode.path);
            console.log('[WebView]   hasValidPath:', hasValidPath);
            
            // For create operations, send the command using the path or construct from name
            let commandText;
            switch(actionType) {
                case 'sub-epic':
                    commandText = hasValidPath ? \`\${window.selectedNode.path}.create\` : \`story_graph."\${window.selectedNode.name}".create\`;
                    break;
                case 'story':
                    commandText = hasValidPath ? \`\${window.selectedNode.path}.create_story\` : \`story_graph."\${window.selectedNode.name}".create_story\`;
                    break;
                case 'scenario':
                    commandText = hasValidPath ? \`\${window.selectedNode.path}.create_scenario\` : \`story_graph."\${window.selectedNode.name}".create_scenario\`;
                    break;
                case 'acceptance-criteria':
                    commandText = hasValidPath ? \`\${window.selectedNode.path}.create_acceptance_criteria\` : \`story_graph."\${window.selectedNode.name}".create_acceptance_criteria\`;
                    break;
            }
            
            if (commandText) {
                console.log('[WebView]   SENDING COMMAND:', commandText);
                vscode.postMessage({
                    command: 'logToFile',
                    message: '[WebView] SENDING COMMAND: ' + commandText
                });
                vscode.postMessage({
                    command: 'executeCommand',
                    commandText: commandText
                });
                console.log('[WebView]   postMessage sent successfully');
            } else {
                console.error('[WebView] ERROR: No commandText generated');
            }
            console.log('═══════════════════════════════════════════════════════');
        };
        
        // Handle delete action (always cascade)
        window.handleDelete = function() {
            console.log('[WebView] handleDelete called for node:', window.selectedNode);
            
            if (!window.selectedNode.name) {
                console.error('[WebView] ERROR: No node selected for delete');
                return;
            }
            
            const hasValidPath = window.selectedNode.path && 
                                window.selectedNode.path.length > 'story_graph.'.length &&
                                window.selectedNode.path.includes(window.selectedNode.name);
            
            const commandText = hasValidPath 
                ? \`\${window.selectedNode.path}.delete\`
                : \`story_graph."\${window.selectedNode.name}".delete\`;
            
            console.log('[WebView] Delete command:', commandText);
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] SENDING DELETE COMMAND: ' + commandText
            });
            
            vscode.postMessage({
                command: 'executeCommand',
                commandText: commandText
            });
        };
        
        // Handle scope to action - set filter to selected node
        window.handleScopeTo = function() {
            console.log('[WebView] handleScopeTo called for node:', window.selectedNode);
            
            if (!window.selectedNode.name) {
                console.error('[WebView] ERROR: No node selected for scope');
                return;
            }
            
            // Use the node name as the filter value
            const filterValue = window.selectedNode.name;
            
            console.log('[WebView] Scope To filter:', filterValue);
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] SENDING SCOPE TO COMMAND: scope "' + filterValue + '"'
            });
            
            // Execute scope command with the node name as filter
            vscode.postMessage({
                command: 'executeCommand',
                commandText: 'scope "' + filterValue + '"'
            });
        };
        
        // Handle submit scope action - submit selected node and start work
        window.handleSubmitScope = function() {
            console.log('[WebView] handleSubmitScope called for node:', window.selectedNode);
            
            if (!window.selectedNode.name) {
                console.error('[WebView] ERROR: No node selected for submit');
                return;
            }
            
            // Use the node name for submit_scope command
            const nodeName = window.selectedNode.name;
            
            console.log('[WebView] Submit scope for node:', nodeName);
            vscode.postMessage({
                command: 'logToFile',
                message: '[WebView] SENDING SUBMIT SCOPE COMMAND: submit_scope "' + nodeName + '"'
            });
            
            // Execute submit_scope command with the node name
            vscode.postMessage({
                command: 'executeCommand',
                commandText: 'submit_scope "' + nodeName + '"'
            });
        };
        
        // Initialize: show Create Epic button by default
        setTimeout(() => {
            window.selectNode('root', null);
        }, 100);
        
        // Save functions for guardrails
        window.saveClarifyAnswers = function() {
            console.log('[WebView] saveClarifyAnswers triggered');
            const answers = {};
            const answerElements = document.querySelectorAll('[id^="clarify-answer-"]');
            
            answerElements.forEach((textarea) => {
                const question = textarea.getAttribute('data-question');
                const answer = textarea.value?.trim();
                if (question && answer) {
                    answers[question] = answer;
                }
            });
            
            if (Object.keys(answers).length > 0) {
                console.log('[WebView] Saving clarify answers:', answers);
                vscode.postMessage({
                    command: 'saveClarifyAnswers',
                    answers: answers
                });
            }
        };
        
        window.saveClarifyEvidence = function() {
            console.log('[WebView] saveClarifyEvidence triggered');
            const evidenceTextarea = document.getElementById('clarify-evidence');
            if (evidenceTextarea) {
                const evidenceText = evidenceTextarea.value?.trim();
                if (evidenceText) {
                    // Parse evidence text as key:value pairs
                    const evidenceProvided = {};
                    evidenceText.split('\\n').forEach(line => {
                        const colonIdx = line.indexOf(':');
                        if (colonIdx > 0) {
                            const key = line.substring(0, colonIdx).trim();
                            const value = line.substring(colonIdx + 1).trim();
                            if (key && value) {
                                evidenceProvided[key] = value;
                            }
                        }
                    });
                    
                    if (Object.keys(evidenceProvided).length > 0) {
                        console.log('[WebView] Saving clarify evidence:', evidenceProvided);
                        vscode.postMessage({
                            command: 'saveClarifyEvidence',
                            evidence_provided: evidenceProvided
                        });
                    }
                }
            }
        };
        
        window.saveStrategyDecision = function(criteriaKey, selectedOption) {
            console.log('[WebView] saveStrategyDecision triggered:', criteriaKey, selectedOption);
            vscode.postMessage({
                command: 'saveStrategyDecision',
                criteriaKey: criteriaKey,
                selectedOption: selectedOption
            });
        };
        
        window.saveStrategyAssumptions = function() {
            console.log('[WebView] saveStrategyAssumptions triggered');
            const assumptionsTextarea = document.getElementById('strategy-assumptions');
            if (assumptionsTextarea) {
                const assumptionsText = assumptionsTextarea.value?.trim();
                if (assumptionsText) {
                    const assumptions = assumptionsText.split('\\n').filter(a => a.trim());
                    console.log('[WebView] Saving strategy assumptions:', assumptions);
                    vscode.postMessage({
                        command: 'saveStrategyAssumptions',
                        assumptions: assumptions
                    });
                }
            }
        };
        
        // Listen for messages from extension host (e.g. error displays)
        window.addEventListener('message', event => {
            const message = event.data;
            console.log('[WebView] Received message from extension:', message);
            
            if (message.command === 'displayError') {
                // Display error prominently in the panel
                const errorDiv = document.createElement('div');
                errorDiv.style.cssText = 'position: fixed; top: 10px; left: 10px; right: 10px; z-index: 10000; background: #f44336; color: white; padding: 16px; border-radius: 4px; font-family: monospace; font-size: 12px; white-space: pre-wrap; max-height: 80vh; overflow-y: auto;';
                errorDiv.textContent = '[ERROR] ' + message.error;
                
                // Add button container
                const btnContainer = document.createElement('div');
                btnContainer.style.cssText = 'margin-top: 12px; display: flex; gap: 8px;';
                
                // Add retry button
                const retryBtn = document.createElement('button');
                retryBtn.textContent = '🔄 Retry';
                retryBtn.style.cssText = 'background: white; color: #f44336; border: none; padding: 8px 16px; cursor: pointer; border-radius: 3px; font-weight: bold;';
                retryBtn.onclick = () => {
                    errorDiv.remove();
                    vscode.postMessage({ command: 'refresh' });
                };
                
                // Add close button
                const closeBtn = document.createElement('button');
                closeBtn.textContent = 'Close';
                closeBtn.style.cssText = 'background: rgba(255,255,255,0.8); color: #f44336; border: none; padding: 8px 16px; cursor: pointer; border-radius: 3px;';
                closeBtn.onclick = () => errorDiv.remove();
                
                btnContainer.appendChild(retryBtn);
                btnContainer.appendChild(closeBtn);
                errorDiv.appendChild(btnContainer);
                
                document.body.appendChild(errorDiv);
                
                // Auto-remove after 30 seconds
                setTimeout(() => errorDiv.remove(), 30000);
            }
            
            // Optimistic update: rename node in DOM immediately
            if (message.command === 'optimisticRename') {
                console.log('[WebView] Optimistic rename:', message.oldName, '->', message.newName);
                // Find node by path and update text
                const nodes = document.querySelectorAll('.story-node');
                for (const node of nodes) {
                    if (node.getAttribute('data-path') === message.nodePath) {
                        // Update node name in DOM
                        const oldText = node.textContent;
                        const newText = oldText.replace(message.oldName, message.newName);
                        node.textContent = newText;
                        // Update data attribute
                        node.setAttribute('data-node-name', message.newName);
                        console.log('[WebView] Updated node text:', oldText, '->', newText);
                        
                        // Update selected node if this is the selected node
                        if (window.selectedNode && window.selectedNode.path === message.nodePath) {
                            window.selectedNode.name = message.newName;
                            sessionStorage.setItem('selectedNode', JSON.stringify(window.selectedNode));
                        }
                        break;
                    }
                }
            }
            
            // Revert rename on error
            if (message.command === 'revertRename') {
                console.log('[WebView] Reverting rename to:', message.oldName);
                const nodes = document.querySelectorAll('.story-node');
                for (const node of nodes) {
                    if (node.getAttribute('data-path') === message.nodePath) {
                        // Revert node name in DOM
                        const currentText = node.textContent;
                        const revertedText = currentText.replace(/[^"]+$/, message.oldName);
                        node.textContent = revertedText;
                        // Revert data attribute
                        node.setAttribute('data-node-name', message.oldName);
                        console.log('[WebView] Reverted node text to:', message.oldName);
                        
                        // Update selected node if this is the selected node
                        if (window.selectedNode && window.selectedNode.path === message.nodePath) {
                            window.selectedNode.name = message.oldName;
                            sessionStorage.setItem('selectedNode', JSON.stringify(window.selectedNode));
                        }
                        break;
                    }
                }
            }
            
            // Update submit button tooltip based on backend behavior analysis
            if (message.command === 'updateSubmitTooltip') {
                console.log('[WebView] updateSubmitTooltip:', message.behavior, 'for', message.nodeName);
                var btnSubmit = document.getElementById('btn-submit');
                if (btnSubmit && window.selectedNode && window.selectedNode.name === message.nodeName) {
                    var tooltipText = window.behaviorToTooltipText(message.behavior);
                    btnSubmit.setAttribute('title', tooltipText + ': ' + message.nodeName);
                    console.log('[WebView] Updated tooltip to:', tooltipText + ': ' + message.nodeName);
                }
            }
        });
    </script>
</body>
</html>`;
  }
}

module.exports = BotPanel;
