#!/bin/bash
# Bump version, rebuild, and reinstall the Bot Panel extension
# Usage: ./panel_bump_and_install.sh [patch|minor|major]
# Default: patch (0.1.0 -> 0.1.1)

set -e  # Exit on error

# Default values
BUMP_TYPE="patch"

# Parse arguments
for arg in "$@"; do
    case $arg in
        patch|minor|major)
            BUMP_TYPE="$arg"
            ;;
        *)
            echo "Usage: $0 [patch|minor|major] [--no-reload]"
            exit 1
            ;;
    esac
done

# Navigate to panel directory using relative paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGILE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"  # Get workspace root (two levels up from src/panel)
PANEL_DIR="$AGILE_DIR/src/panel"
cd "$PANEL_DIR"

echo -e "\033[0;36m================================\033[0m"
echo -e "\033[0;36mBot Panel Version Bump\033[0m"
echo -e "\033[0;36m================================\033[0m"
echo ""

# Read current version from package.json
PACKAGE_JSON_PATH="$PANEL_DIR/package.json"
CURRENT_VERSION=$(node -p "require('$PACKAGE_JSON_PATH').version")
echo -e "\033[0;33mCurrent version: $CURRENT_VERSION\033[0m"

# Parse version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Bump version based on type
case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo -e "\033[0;32mNew version:     $NEW_VERSION\033[0m"
echo ""

# Update package.json
echo -e "\033[0;36m[1/6] Updating package.json...\033[0m"
sed -i.bak "s/\"version\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" package.json
rm -f package.json.bak

echo -e "\033[0;32mVersion updated: $CURRENT_VERSION -> $NEW_VERSION\033[0m"

# Give filesystem time to sync
sleep 0.2
echo -e "\033[0;32m      Done: package.json updated\033[0m"

# Package extension
echo -e "\033[0;36m[2/6] Packaging extension...\033[0m"
# Remove old vsix files first
rm -f "$PANEL_DIR"/bot-panel-*.vsix
npx @vscode/vsce package --allow-missing-repository --allow-star-activation > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "\033[0;31m      ERROR: Packaging failed!\033[0m"
    exit 1
fi
# Verify the file was created
sleep 0.5
echo -e "\033[0;32m      Done: Extension packaged: bot-panel-$NEW_VERSION.vsix\033[0m"

# Uninstall old extension
echo -e "\033[0;36m[3/6] Uninstalling old extension...\033[0m"
code --uninstall-extension agilebot.bot-panel > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "\033[0;33m      Warning: Uninstall warning (may not be installed)\033[0m"
else
    echo -e "\033[0;32m      Done: Old extension uninstalled\033[0m"
fi

# Install new extension
echo -e "\033[0;36m[4/6] Installing new extension...\033[0m"
VSIX_PATH="$PANEL_DIR/bot-panel-$NEW_VERSION.vsix"
if [ ! -f "$VSIX_PATH" ]; then
    echo -e "\033[0;31m      ERROR: VSIX file not found: $VSIX_PATH\033[0m"
    exit 1
fi
code --install-extension "$VSIX_PATH" --force > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "\033[0;31m      ERROR: Installation failed!\033[0m"
    exit 1
fi
echo -e "\033[0;32m      Done: Extension v$NEW_VERSION installed\033[0m"

echo ""
echo -e "\033[0;36m================================\033[0m"
echo -e "\033[0;32mSUCCESS!\033[0m"
echo -e "\033[0;36m================================\033[0m"
echo ""
echo -e "\033[0;32mExtension upgraded: $CURRENT_VERSION -> $NEW_VERSION\033[0m"
echo ""

echo -e "\033[0;32mExtension installed successfully!\033[0m"
echo -e "\033[0;36mThe extension may activate automatically, or you can reload when ready:\033[0m"
echo -e "\033[0;33m  Ctrl+Shift+P -> Developer: Reload Window\033[0m"
echo ""
