#!/usr/bin/env bash
# Export today's Copilot Chat sessions as a markdown summary for journal inclusion.
#
# Usage:
#   ./bin/export-copilot-session.sh [date]
#     date: YYYY-MM-DD (default: today)
#
# Output: prints markdown to stdout
#
# Dependencies: sqlite3, python3

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

exec python3 "$SCRIPT_DIR/export-copilot-session.py" "$@"