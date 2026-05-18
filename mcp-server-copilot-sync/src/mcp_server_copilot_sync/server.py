#!/usr/bin/env python3
"""MCP server for syncing GitHub Copilot Chat sessions."""

import sys
import json
from typing import Optional, Dict, Any

# Try to import MCP
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from mcp_server_copilot_sync.config import SyncConfig
from mcp_server_copilot_sync.sync import CopilotSync


class CopilotSyncServer:
    """MCP server for Copilot session sync."""

    def __init__(self, config: SyncConfig):
        self.config = config
        self.sync = CopilotSync(config)

    def push_sessions(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Push local sessions to GitHub."""
        return self.sync.push_to_github(date)

    def pull_sessions(self, replace_local: bool = True) -> Dict[str, Any]:
        """Pull sessions from GitHub."""
        return self.sync.pull_from_github(replace_local)

    def get_status(self) -> Dict[str, Any]:
        """Get sync status."""
        return self.sync.get_sync_status()


def main():
    """Main entry point for the MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP library not installed. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)

    # Load configuration
    config = SyncConfig.from_env()

    # Validate
    errors = config.validate()
    if errors:
        print(f"Configuration errors: {'; '.join(errors)}", file=sys.stderr)
        print("Please set GITHUB_TOKEN, SYNC_REPO_OWNER, and SYNC_REPO_NAME environment variables.", file=sys.stderr)
        sys.exit(1)

    # Create server
    server = CopilotSyncServer(config)

    app = FastMCP("copilot-sync")

    @app.tool(name="copilot-sync-push")
    def push_sessions(date: Optional[str] = None) -> str:
        """Push local Copilot Chat sessions to GitHub repository.
        
        Args:
            date: Optional date string (YYYY-MM-DD) for commit message. Defaults to today.
        
        Returns:
            Sync result with success status, message, and session count.
        """
        result = server.push_sessions(date)
        return json.dumps(result, indent=2)

    @app.tool(name="copilot-sync-pull")
    def pull_sessions(replace_local: bool = True) -> str:
        """Pull Copilot Chat sessions from GitHub repository to local machine.
        
        Args:
            replace_local: If True, replace the local session-store.db. If False, save as backup.
        
        Returns:
            Sync result with success status, message, and session count.
        """
        result = server.pull_sessions(replace_local)
        return json.dumps(result, indent=2)

    @app.tool(name="copilot-sync-status")
    def get_sync_status() -> str:
        """Get current sync status including local and GitHub session counts.
        
        Returns:
            Status information about local and GitHub sessions.
        """
        status = server.get_status()
        return json.dumps(status, indent=2)

    # Run the server
    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
