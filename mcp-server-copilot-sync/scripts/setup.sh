#!/usr/bin/env bash
# Setup script for Copilot Sync MCP server
# This script configures the environment variables and creates necessary files

set -euo pipefail

echo "🔧 Setting up Copilot Sync MCP Server"
echo "======================================"
echo ""

# Check if GITHUB_TOKEN is set
if [ -z "${GITHUB_TOKEN:-}" ]; then
    echo "❌ GITHUB_TOKEN environment variable is not set"
    echo ""
    echo "Please generate a GitHub Personal Access Token with 'repo' scope:"
    echo "  https://github.com/settings/tokens"
    echo ""
    echo "Then run:"
    echo "  export GITHUB_TOKEN='ghp_your_token_here'"
    echo "  ./scripts/setup.sh"
    exit 1
fi

# Get repo owner and name from user
echo "📝 Enter your GitHub repository details:"
echo ""

if [ -z "${SYNC_REPO_OWNER:-}" ]; then
    read -p "GitHub username/organization: " SYNC_REPO_OWNER
fi

if [ -z "${SYNC_REPO_NAME:-}" ]; then
    read -p "Repository name (e.g., copilot-sync): " SYNC_REPO_NAME
fi

# Create configuration directory
CONFIG_DIR="$HOME/.config/copilot-sync"
mkdir -p "$CONFIG_DIR"

# Create configuration file
cat > "$CONFIG_DIR/config.json" << EOF
{
    "github_token": "$GITHUB_TOKEN",
    "repo_owner": "$SYNC_REPO_OWNER",
    "repo_name": "$SYNC_REPO_NAME",
    "branch": "main",
    "db_file_path": "session-store.db",
    "backup_dir": "$HOME/copilot-sync-backups"
}
EOF

echo ""
echo "✅ Configuration saved to $CONFIG_DIR/config.json"
echo ""

# Add environment variables to shell profile
SHELL_PROFILE=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
else
    SHELL_PROFILE="$HOME/.bashrc"
    touch "$SHELL_PROFILE"
fi

# Check if already configured
if grep -q "SYNC_REPO_OWNER" "$SHELL_PROFILE" 2>/dev/null; then
    echo "⚠️  Environment variables already configured in $SHELL_PROFILE"
else
    # Add environment variables to shell profile
    cat >> "$SHELL_PROFILE" << 'EOF'

# Copilot Sync MCP Server Configuration
export GITHUB_TOKEN="your_github_token_here"
export SYNC_REPO_OWNER="your_github_username"
export SYNC_REPO_NAME="your_repo_name"
export SYNC_BRANCH="main"
export SYNC_DB_FILE_PATH="session-store.db"
export SYNC_BACKUP_DIR="$HOME/copilot-sync-backups"
EOF

    echo "✅ Environment variables added to $SHELL_PROFILE"
    echo ""
    echo "⚠️  Please update the values in $SHELL_PROFILE with your actual token and repo details"
fi

echo ""
echo "📋 Next steps:"
echo "  1. Update $SHELL_PROFILE with your actual GitHub token and repo details"
echo "  2. Run: source $SHELL_PROFILE"
echo "  3. Verify configuration: python -c 'from mcp_server_copilot_sync.config import SyncConfig; print(SyncConfig.from_env().to_dict())'"
echo "  4. Test sync: python -m mcp_server_copilot_sync.server"
echo ""
echo "📖 For more information, see README.md"
