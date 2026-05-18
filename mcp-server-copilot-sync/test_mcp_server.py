#!/usr/bin/env python3
"""Test script for MCP Server Copilot Sync."""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp_server_copilot_sync.config import SyncConfig
from mcp_server_copilot_sync.sync import CopilotSync


def test_config():
    """Test configuration loading."""
    print("🧪 Testing configuration...")
    
    # Test from env
    config = SyncConfig.from_env()
    print(f"  ✅ Config loaded from environment")
    print(f"     - Repo: {config.repo_owner}/{config.repo_name}")
    print(f"     - Branch: {config.branch}")
    
    # Test validation
    errors = config.validate()
    if errors:
        print(f"  ⚠️  Validation errors: {errors}")
        return None
    else:
        print(f"  ✅ Configuration is valid")
        return config


def test_local_db_detection(config: SyncConfig):
    """Test local database detection."""
    print("\n🧪 Testing local database detection...")
    
    sync = CopilotSync(config)
    local_db = sync.find_local_db()
    
    if local_db:
        print(f"  ✅ Found local database: {local_db}")
        
        # Get session count
        session_count = sync.get_session_count(local_db)
        print(f"  ✅ Sessions in local DB: {session_count}")
        
        return local_db, session_count
    else:
        print("  ❌ No local database found")
        return None, 0


def test_sync_status(config: SyncConfig):
    """Test sync status check."""
    print("\n🧪 Testing sync status...")
    
    sync = CopilotSync(config)
    status = sync.get_sync_status()
    
    print(f"  Local DB: {status.get('local_db', 'Not found')}")
    print(f"  Local sessions: {status.get('local_sessions', 0)}")
    print(f"  GitHub available: {status.get('github_available', False)}")
    
    return status


def test_push_pull(config: SyncConfig):
    """Test push and pull operations."""
    print("\n🧪 Testing push/pull operations...")
    
    sync = CopilotSync(config)
    
    # Test push
    print("📤 Testing push...")
    result = sync.push_to_github()
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    print(f"   Sessions: {result['sessions_count']}")
    
    # Test pull
    print("\n📥 Testing pull...")
    result = sync.pull_from_github(replace_local=False)
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    print(f"   Sessions: {result['sessions_count']}")


def main():
    """Run all tests."""
    print("🚀 MCP Server Copilot Sync - Test Suite")
    print("=" * 60)
    
    # Test config
    config = test_config()
    if not config:
        print("\n❌ Configuration test failed. Please check your environment variables.")
        return
    
    # Test local DB detection
    test_local_db_detection(config)
    
    # Test sync status
    test_sync_status(config)
    
    # Test push/pull (requires GitHub config)
    if os.environ.get('GITHUB_TOKEN'):
        test_push_pull(config)
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\n📖 For more information, see README.md and USAGE.md")


if __name__ == "__main__":
    main()
