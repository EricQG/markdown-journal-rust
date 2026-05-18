"""Sync logic for Copilot Chat sessions."""

import os
import sqlite3
import shutil
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests


class CopilotSync:
    """Handles syncing Copilot Chat sessions between local and GitHub."""

    def __init__(self, config):
        """Initialize with a SyncConfig object."""
        self.config = config
        self.github_api_url = f"https://api.github.com/repos/{config.repo_owner}/{config.repo_name}"

    def find_local_db(self) -> Optional[str]:
        """Find the local session-store.db file."""
        for path in self.config.local_db_paths:
            if os.path.exists(path):
                return path
        return None

    def default_local_db_path(self) -> Optional[str]:
        """Return the preferred local DB path, even if it does not exist yet."""
        return self.config.local_db_paths[0] if self.config.local_db_paths else None

    def get_session_count(self, db_path: str) -> int:
        """Get the number of sessions in the database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    def push_to_github(self, date: Optional[str] = None) -> dict:
        """Push local session-store.db to GitHub."""
        result = {
            "success": False,
            "message": "",
            "sessions_count": 0,
            "timestamp": datetime.now().isoformat(),
        }

        # Validate config
        errors = self.config.validate()
        if errors:
            result["message"] = f"Configuration error: {'; '.join(errors)}"
            return result

        # Find local DB
        local_db = self.find_local_db()
        if not local_db:
            result["message"] = "No local session-store.db found"
            return result

        # Get session count
        result["sessions_count"] = self.get_session_count(local_db)

        # Read file
        try:
            with open(local_db, "rb") as f:
                content = f.read()
        except Exception as e:
            result["message"] = f"Failed to read local DB: {e}"
            return result

        # Backup if configured
        if self.config.backup_dir:
            backup_path = Path(self.config.backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            backup_file = backup_path / f"session-store-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
            shutil.copy2(local_db, backup_file)

        # Upload to GitHub
        try:
            url = f"{self.github_api_url}/contents/{self.config.db_file_path}"
            headers = {
                "Authorization": f"token {self.config.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # Get current SHA if file exists
            sha = None
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json().get("sha")
            elif response.status_code not in [404]:
                result["message"] = f"GitHub API error while reading current file: {response.status_code} - {response.text}"
                return result

            # Prepare commit message
            commit_date = date or datetime.now().strftime("%Y-%m-%d")
            commit_message = f"Sync Copilot sessions: {result['sessions_count']} sessions ({commit_date})"

            # Upload file (GitHub API expects base64-encoded content)
            payload = {
                "message": commit_message,
                "content": base64.b64encode(content).decode("utf-8"),
                "branch": self.config.branch,
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                result["success"] = True
                result["message"] = f"Successfully pushed {result['sessions_count']} sessions to GitHub"
            else:
                result["message"] = f"GitHub API error: {response.status_code} - {response.text}"

        except Exception as e:
            result["message"] = f"Failed to push to GitHub: {e}"

        return result

    def pull_from_github(self, replace_local: bool = True) -> dict:
        """Pull session-store.db from GitHub."""
        result = {
            "success": False,
            "message": "",
            "sessions_count": 0,
            "timestamp": datetime.now().isoformat(),
        }

        # Validate config
        errors = self.config.validate()
        if errors:
            result["message"] = f"Configuration error: {'; '.join(errors)}"
            return result

        # Download from GitHub
        try:
            url = f"{self.github_api_url}/contents/{self.config.db_file_path}"
            headers = {
                "Authorization": f"token {self.config.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                result["message"] = f"GitHub API error: {response.status_code} - {response.text}"
                return result

            data = response.json()
            content = base64.b64decode(data["content"])
            result["sessions_count"] = self._count_sessions_in_memory(content)

        except Exception as e:
            result["message"] = f"Failed to download from GitHub: {e}"
            return result

        # Find local DB path
        local_db = self.find_local_db() or self.default_local_db_path()
        if not local_db:
            result["message"] = "No configured local session-store.db path to update"
            return result

        # Backup existing local DB if replacing
        if replace_local and os.path.exists(local_db):
            backup_path = Path(local_db).parent / f"session-store-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
            shutil.copy2(local_db, backup_path)

        # Write downloaded content
        try:
            Path(local_db).parent.mkdir(parents=True, exist_ok=True)
            with open(local_db, "wb") as f:
                f.write(content)
            result["success"] = True
            result["message"] = f"Successfully pulled {result['sessions_count']} sessions from GitHub"
        except Exception as e:
            result["message"] = f"Failed to write local DB: {e}"

        return result

    def _count_sessions_in_memory(self, db_content: bytes) -> int:
        """Count sessions in a temporary copy of the database."""
        import tempfile
        try:
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                tmp.write(db_content)
                tmp_path = tmp.name
            
            conn = sqlite3.connect(tmp_path)
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            conn.close()
            os.unlink(tmp_path)
            return count
        except Exception:
            return 0

    def get_sync_status(self) -> dict:
        """Get current sync status."""
        result = {
            "local_db": None,
            "local_sessions": 0,
            "github_available": False,
            "last_sync": None,
            "github_sha": None,
            "github_size": None,
        }

        # Check local DB
        local_db = self.find_local_db()
        if local_db:
            result["local_db"] = local_db
            result["local_sessions"] = self.get_session_count(local_db)

        # Check GitHub
        if self.config.repo_owner and self.config.repo_name and self.config.github_token:
            try:
                url = f"{self.github_api_url}/contents/{self.config.db_file_path}"
                headers = {
                    "Authorization": f"token {self.config.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    result["github_available"] = True
                    data = response.json()
                    result["github_sha"] = data.get("sha")
                    result["github_size"] = data.get("size")
                    result["last_sync"] = data.get("commit", {}).get("commit", {}).get("committer", {}).get("date")
            except Exception:
                pass

        return result
