/**
 * Prevent Production File Writes
 * 
 * Safeguard to ensure tests never write to production files.
 * This module checks if WORKING_AREA is set and points to a temp directory
 * when tests are running.
 * 
 * Usage: require this at the top of test files that create PanelView instances
 */

const path = require('path');
const os = require('os');

// Get the repo root (assuming tests are in test/ subdirectory)
const repoRoot = path.resolve(__dirname, '../..');

/**
 * Check if a path is within the production repo
 */
function isProductionPath(filePath) {
    if (!filePath) return false;
    const normalized = path.resolve(filePath);
    return normalized.startsWith(repoRoot);
}

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
 * Verify WORKING_AREA is set to a temp directory in tests
 * This should be called before creating PanelView instances
 */
function verifyTestWorkspace() {
    const workingArea = process.env.WORKING_AREA;
    
    if (!workingArea) {
        throw new Error(
            `\n` +
            `╔════════════════════════════════════════════════════════════════╗\n` +
            `║  TEST SAFETY VIOLATION: WORKING_AREA not set!                  ║\n` +
            `╚════════════════════════════════════════════════════════════════╝\n\n` +
            `  Tests MUST set WORKING_AREA to a temp directory before creating\n` +
            `  PanelView instances to prevent writing to production files.\n\n` +
            `  Example:\n` +
            `    const tempWorkspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'test-'));\n` +
            `    process.env.WORKING_AREA = tempWorkspaceDir;\n` +
            `    const panelView = new PanelView(botPath);\n\n`
        );
    }
    
    if (!isTempPath(workingArea)) {
        throw new Error(
            `\n` +
            `╔════════════════════════════════════════════════════════════════╗\n` +
            `║  TEST SAFETY VIOLATION: WORKING_AREA points to production!    ║\n` +
            `╚════════════════════════════════════════════════════════════════╝\n\n` +
            `  WORKING_AREA is set to: ${workingArea}\n` +
            `  This appears to be a production path, not a temp directory!\n\n` +
            `  Tests MUST use a temp directory to prevent writing to production files.\n\n` +
            `  Example:\n` +
            `    const tempWorkspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'test-'));\n` +
            `    process.env.WORKING_AREA = tempWorkspaceDir;\n` +
            `    const panelView = new PanelView(botPath);\n\n`
        );
    }
}

module.exports = {
    verifyTestWorkspace,
    isProductionPath,
    isTempPath
};
