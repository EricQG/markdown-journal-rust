#!/usr/bin/env python3
"""Demo script for Copilot Sync MCP server.

This script demonstrates how to use the sync functionality without the MCP server.
It can be used for testing and debugging.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp_server_copilot_sync.config import SyncConfig
from mcp_server_copilot_sync.sync import CopilotSync


def print_header(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_local_detection():
    """Demonstrate local database detection."""
    print_header("Local Database Detection")
    
    config = SyncConfig.from_env()
    sync = CopilotSync(config)
    
    # Find local DB
    local_db = sync.find_local_db()
    if local_db:
        print(f"✅ Found local database: {local_db}")
        
        # Get session count
        session_count = sync.get_session_count(local_db)
        print(f"✅ Sessions in local DB: {session_count}")
        
        # Show database info
        import sqlite3
        conn = sqlite3.connect(local_db)
        cursor = conn.cursor()
        
        # Get session dates
        cursor.execute("SELECT date(created_at) as session_date, COUNT(*) as count FROM sessions GROUP BY date(created_at) ORDER BY session_date DESC LIMIT 10")
        dates = cursor.fetchall()
        
        if dates:
            print("\n📅 Recent session dates:")
            for date, count in dates:
                print(f"   {date}: {count} sessions")
        
        # Get agent names
        cursor.execute("SELECT DISTINCT agent_name FROM sessions WHERE agent_name != '' LIMIT 5")
        agents = [row[0] for row in cursor.fetchall()]
        
        if agents:
            print(f"\n🤖 Agents used: {', '.join(agents)}")
        
        conn.close()
    else:
        print("❌ No local database found")
        print("\nExpected locations:")
        for path in config.local_db_paths:
            exists = "✅" if os.path.exists(path) else "❌"
            print(f"   {exists} {path}")


def demo_sync_status():
    """Demonstrate sync status check."""
    print_header("Sync Status")
    
    config = SyncConfig.from_env()
    
    # Validate config
    errors = config.validate()
    if errors:
        print("⚠️  Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease set the following environment variables:")
        print("   export GITHUB_TOKEN='your_token'")
        print("   export SYNC_REPO_OWNER='your_username'")
        print("   export SYNC_REPO_NAME='your_repo'")
        return
    
    print("✅ Configuration valid")
    print(f"   Repository: {config.repo_owner}/{config.repo_name}")
    print(f"   Branch: {config.branch}")
    
    sync = CopilotSync(config)
    status = sync.get_sync_status()
    
    print(f"\n📊 Sync Status:")
    print(f"   Local DB: {status.get('local_db', 'Not found')}")
    print(f"   Local sessions: {status.get('local_sessions', 0)}")
    print(f"   GitHub available: {status.get('github_available', False)}")
    
    if status.get('last_sync'):
        print(f"   Last sync: {status.get('last_sync')}")


def demo_push_pull():
    """Demonstrate push and pull operations."""
    print_header("Push/Pull Operations")
    
    config = SyncConfig.from_env()
    
    # Validate config
    errors = config.validate()
    if errors:
        print("⚠️  Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\nCannot proceed without valid configuration.")
        return
    
    sync = CopilotSync(config)
    
    # Demo push
    print("📤 Testing push...")
    result = sync.push_to_github()
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    print(f"   Sessions: {result['sessions_count']}")
    
    # Demo pull
    print("\n📥 Testing pull...")
    result = sync.pull_from_github(replace_local=False)
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    print(f"   Sessions: {result['sessions_count']}")


def main():
    """Run all demos."""
    print("🚀 Copilot Sync MCP Server - Demo")
    print("=" * 60)
    
    # Demo local detection
    demo_local_detection()
    
    # Demo sync status
    demo_sync_status()
    
    # Demo push/pull (requires config)
    if os.environ.get('GITHUB_TOKEN'):
        demo_push_pull()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("\n📖 For more information, see README.md and USAGE.md")


if __name__ == "__main__":
    main()
