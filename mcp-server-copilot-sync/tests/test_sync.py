#!/usr/bin/env python3
"""Test script for Copilot Sync functionality."""

import os
import sys
import sqlite3
import tempfile
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


def test_backup_creation(config: SyncConfig):
    """Test backup creation."""
    print("\n🧪 Testing backup creation...")
    
    if not config.backup_dir:
        print("  ⏭️  Skipping backup test (no backup directory configured)")
        return
    
    local_db = Path(config.local_db_paths[0]) if config.local_db_paths else None
    if not local_db or not local_db.exists():
        print("  ⏭️  Skipping backup test (no local DB)")
        return
    
    try:
        # Create backup
        backup_path = Path(config.backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        backup_file = backup_path / f"test-backup-{os.getpid()}.db"
        
        import shutil
        shutil.copy2(str(local_db), str(backup_file))
        print(f"  ✅ Backup created: {backup_file}")
        
        # Clean up
        backup_file.unlink()
        print(f"  ✅ Backup cleaned up")
        
    except Exception as e:
        print(f"  ❌ Backup test failed: {e}")


def main():
    """Run all tests."""
    print("🚀 Running Copilot Sync Tests")
    print("=" * 50)
    
    # Test configuration
    config = test_config()
    
    # Test local DB detection
    local_db, session_count = test_local_db_detection(config)
    
    # Test sync status
    status = test_sync_status(config)
    
    # Test backup creation
    test_backup_creation(config)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
