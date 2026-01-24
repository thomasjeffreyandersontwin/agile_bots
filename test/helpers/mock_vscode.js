/**
 * Mock vscode module for panel tests
 */

module.exports = {
    Uri: {
        file: (path) => ({ fsPath: path, toString: () => path }),
        joinPath: (base, ...paths) => {
            const path = require('path');
            let result = base.fsPath || base.toString() || '';
            for (const p of paths) {
                result = path.join(result, p);
            }
            return { fsPath: result, toString: () => result };
        }
    },
    ViewColumn: {
        One: 1,
        Two: 2
    },
    Range: class Range {
        constructor(startLine, startChar, endLine, endChar) {
            this.start = { line: startLine, character: startChar };
            this.end = { line: endLine, character: endChar };
        }
    },
    window: {
        showErrorMessage: () => Promise.resolve(),
        showInformationMessage: () => Promise.resolve(),
        showTextDocument: () => Promise.resolve(),
        createOutputChannel: () => ({
            appendLine: () => {},
            show: () => {}
        }),
        createWebviewPanel: () => ({
            webview: {
                asWebviewUri: (uri) => uri,
                postMessage: () => {}
            },
            onDidDispose: () => ({ dispose: () => {} }),
            reveal: () => {}
        })
    },
    workspace: {
        workspaceFolders: [],
        openTextDocument: () => Promise.resolve({
            getText: () => '',
            lineCount: 0
        })
    },
    commands: {
        registerCommand: () => ({ dispose: () => {} }),
        executeCommand: () => Promise.resolve()
    }
};
