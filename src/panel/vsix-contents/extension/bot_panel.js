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
      let botDirectory = process.env.BOT_DIRECTORY || path.join(workspaceRoot, 'agile_bots', 'bots', 'story_bot');
      // Ensure bot directory is absolute
      if (!path.isAbsolute(botDirectory)) {
        botDirectory = path.join(workspaceRoot, botDirectory);
      }
      console.log(`[BotPanel] Bot directory: ${botDirectory}`);
      
      // Initialize singleton CLI (only initializes once, safe to call multiple times)
      console.log("[BotPanel] Initializing singleton CLI");
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:43',message:'Before initializeCLI',data:{workspaceRoot,botDirectory},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      PanelView.initializeCLI(workspaceRoot, botDirectory, this.logFilePath);
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:43',message:'After initializeCLI',data:{},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
      // #endregion
      console.log("[BotPanel] CLI initialized successfully");
      
      // Initialize BotView (uses singleton CLI)
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
            this._update().catch(err => console.error(`[BotPanel] Refresh error: ${err.message}`));
            return;
          case "openFile":
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
                vscode.window.showErrorMessage(`Failed to clear scope: ${error.message}`);
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
                  this._displayError(errorMsg + '\n\nStack:\n' + err.stack);
                  throw err; // Re-throw to crash the panel as requested
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
                  this._displayError(errorMsg + '\n\nStack:\n' + err.stack);
                  throw err; // Re-throw to crash the panel as requested
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
          case "navigateToBehavior":
            if (message.behaviorName) {
              const cmd = `${message.behaviorName}.clarify`;
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
            this._botView?.execute('submit')
              .then(() => {
                vscode.window.showInformationMessage('Instructions submitted to chat!');
              })
              .catch((error) => {
                vscode.window.showErrorMessage(`Submit failed: ${error.message}`);
              });
            return;
          case "saveClarifyAnswers":
            if (message.answers) {
              this._log(`[BotPanel] saveClarifyAnswers -> ${JSON.stringify(message.answers)}`);
              const answersJson = JSON.stringify(message.answers).replace(/'/g, "\\'");
              const cmd = `clarify --answers '${answersJson}'`;
              this._botView?.execute(cmd)
                .then(() => {
                  this._log(`[BotPanel] saveClarifyAnswers success`);
                  return this._update();
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
              const cmd = `clarify --evidence_provided '${evidenceJson}'`;
              this._botView?.execute(cmd)
                .then(() => {
                  this._log(`[BotPanel] saveClarifyEvidence success`);
                  return this._update();
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
              // Load existing decisions, update one, and save all
              this._botView?.execute('status')
                .then((statusResult) => {
                  const currentBehavior = statusResult.behavior;
                  // Build decisions object with just this one decision
                  const decisions = {};
                  decisions[message.criteriaKey] = message.selectedOption;
                  const decisionsJson = JSON.stringify(decisions).replace(/'/g, "\\'");
                  const cmd = `${currentBehavior}.strategy --decisions '${decisionsJson}'`;
                  return this._botView?.execute(cmd);
                })
                .then(() => {
                  this._log(`[BotPanel] saveStrategyDecision success`);
                  return this._update();
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
              this._botView?.execute('status')
                .then((statusResult) => {
                  const currentBehavior = statusResult.behavior;
                  const cmd = `${currentBehavior}.strategy --assumptions '${assumptionsJson}'`;
                  return this._botView?.execute(cmd);
                })
                .then(() => {
                  this._log(`[BotPanel] saveStrategyAssumptions success`);
                  return this._update();
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

    // Clean up singleton CLI (safe since BotPanel is singleton)
    console.log("[BotPanel] Cleaning up singleton CLI");
    PanelView.cleanupSharedCLI();

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
      
      // Initialize BotView if needed (uses singleton CLI)
      if (!this._botView) {
        console.log("[BotPanel] Creating BotView");
        this._log('[BotPanel] Creating BotView');
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/cc11718e-e210-436d-8aa6-f3e81dc3fdfc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'bot_panel.js:394',message:'Before new BotView()',data:{panelVersion:this._panelVersion,hasWebview:!!webview,hasExtensionUri:!!this._extensionUri},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
        // #endregion
        try {
          this._botView = new BotView(this._panelVersion, webview, this._extensionUri);
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
      this._panel.webview.html = html;
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
      vscode.window.showErrorMessage(`Bot Panel Update Error: ${err.message}`);
      this._panel.webview.html = this._getWebviewContent(`
        <div style="padding: 20px; color: var(--vscode-errorForeground);">
          <h2>Error Loading Bot Panel</h2>
          <p>${this._escapeHtml(err.message)}</p>
          <p>Stack: ${this._escapeHtml(err.stack || 'No stack trace')}</p>
          <p>Please ensure Python is installed and the bot CLI is available.</p>
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
        }
        .collapsible-section.expanded .expand-icon {
            transform: rotate(90deg);
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
        console.log('[WebView] vscode API acquired:', !!vscode);
        console.log('[WebView] vscode.postMessage available:', typeof vscode.postMessage);
        
        function toggleSection(sectionId) {
            const content = document.getElementById(sectionId);
            if (content) {
                const section = content.closest('.collapsible-section');
                const isExpanded = section && section.classList.contains('expanded');
                
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
                if (header && section) {
                    section.classList.toggle('expanded', !isExpanded);
                    // Keep icon as ▸ always - CSS rotation handles the visual state
                    const icon = header.querySelector('.expand-icon');
                    if (icon) {
                        icon.textContent = '▸';
                    }
                }
            }
        }
        
        function toggleCollapse(elementId) {
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
            }
        }
        
        function openFile(filePath) {
            vscode.postMessage({
                command: 'openFile',
                filePath: filePath
            });
        }
        
        function updateFilter(filterValue) {
            console.log('[WebView] updateFilter called with:', filterValue);
            const message = {
                command: 'updateFilter',
                filter: filterValue
            };
            console.log('[WebView] Sending message:', message);
            vscode.postMessage(message);
            console.log('[WebView] postMessage sent');
        }
        
        // Test if updateFilter is defined
        console.log('[WebView] updateFilter function exists:', typeof updateFilter);
        
        function clearScopeFilter() {
            vscode.postMessage({
                command: 'clearScopeFilter'
            });
        }
        
        function executeNavigationCommand(command) {
            console.log('[WebView] executeNavigationCommand click ->', command);
            vscode.postMessage({
                command: 'executeNavigationCommand',
                commandText: command
            });
        }
        
        function navigateToBehavior(behaviorName) {
            console.log('[WebView] navigateToBehavior click ->', behaviorName);
            vscode.postMessage({
                command: 'navigateToBehavior',
                behaviorName: behaviorName
            });
        }
        
        function navigateToAction(behaviorName, actionName) {
            console.log('[WebView] navigateToAction click ->', behaviorName, actionName);
            vscode.postMessage({
                command: 'navigateToAction',
                behaviorName: behaviorName,
                actionName: actionName
            });
        }
        
        function navigateAndExecute(behaviorName, actionName, operationName) {
            console.log('[WebView] navigateAndExecute click ->', behaviorName, actionName, operationName);
            vscode.postMessage({
                command: 'navigateAndExecute',
                behaviorName: behaviorName,
                actionName: actionName,
                operationName: operationName
            });
        }
        
        function submitToChat() {
            vscode.postMessage({
                command: 'sendToChat'
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
        
        function switchBot(botName) {
            console.log('[WebView] switchBot called with:', botName);
            vscode.postMessage({
                command: 'switchBot',
                botName: botName
            });
        }
        
        // Save functions for guardrails
        function saveClarifyAnswers() {
            console.log('[WebView] saveClarifyAnswers triggered');
            const answers = {};
            const answerElements = document.querySelectorAll('[id^="clarify-answer-"]');
            const questionElements = document.querySelectorAll('.input-header');
            
            answerElements.forEach((textarea, idx) => {
                const question = questionElements[idx]?.textContent?.trim();
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
        }
        
        function saveClarifyEvidence() {
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
        }
        
        function saveStrategyDecision(criteriaKey, selectedOption) {
            console.log('[WebView] saveStrategyDecision triggered:', criteriaKey, selectedOption);
            vscode.postMessage({
                command: 'saveStrategyDecision',
                criteriaKey: criteriaKey,
                selectedOption: selectedOption
            });
        }
        
        function saveStrategyAssumptions() {
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
        }
        
        // Listen for messages from extension host (e.g. error displays)
        window.addEventListener('message', event => {
            const message = event.data;
            console.log('[WebView] Received message from extension:', message);
            
            if (message.command === 'displayError') {
                // Display error prominently in the panel
                const errorDiv = document.createElement('div');
                errorDiv.style.cssText = 'position: fixed; top: 10px; left: 10px; right: 10px; z-index: 10000; background: #f44336; color: white; padding: 16px; border-radius: 4px; font-family: monospace; font-size: 12px; white-space: pre-wrap; max-height: 80vh; overflow-y: auto;';
                errorDiv.textContent = '[ERROR] ' + message.error;
                
                // Add close button
                const closeBtn = document.createElement('button');
                closeBtn.textContent = 'Close';
                closeBtn.style.cssText = 'background: white; color: #f44336; border: none; padding: 8px 16px; margin-top: 12px; cursor: pointer; border-radius: 3px; font-weight: bold;';
                closeBtn.onclick = () => errorDiv.remove();
                errorDiv.appendChild(closeBtn);
                
                document.body.appendChild(errorDiv);
                
                // Auto-remove after 30 seconds
                setTimeout(() => errorDiv.remove(), 30000);
            }
        });
    </script>
</body>
</html>`;
  }
}

module.exports = BotPanel;
