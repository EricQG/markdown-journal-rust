#!/usr/bin/env bash
# Install script for Copilot Sync MCP server
# This script installs the MCP server and its dependencies

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📦 Installing Copilot Sync MCP Server"
echo "======================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Python 3.10+ is required. Found: Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command -v pip3 &>/dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Install the package
echo ""
echo "🔧 Installing package..."
cd "$PROJECT_DIR"
pip3 install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Run: ./scripts/setup.sh"
echo "  2. Configure your GitHub token and repository"
echo "  3. Add the MCP server to your VS Code settings"
echo ""
echo "📖 For more information, see README.md"
