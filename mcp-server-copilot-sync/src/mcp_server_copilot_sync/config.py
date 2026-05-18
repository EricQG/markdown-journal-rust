"""Configuration management for the Copilot sync MCP server."""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


def _split_paths(value: str) -> list[str]:
    return [os.path.expandvars(os.path.expanduser(path.strip())) for path in value.split(os.pathsep) if path.strip()]


@dataclass
class SyncConfig:
    """Configuration for Copilot session sync."""
    github_token: str = ""
    repo_owner: str = ""
    repo_name: str = ""
    branch: str = "main"
    db_file_path: str = "session-store.db"
    local_db_paths: list[str] = field(default_factory=list)
    backup_dir: Optional[str] = None

    @classmethod
    def from_env(cls) -> "SyncConfig":
        """Load configuration from environment variables."""
        local_db_paths = [
            os.path.expanduser("~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db"),
            os.path.expanduser("~/.vscode-server/data/User/globalStorage/github.copilot-chat/session-store.db"),
            os.path.expanduser("~/.config/Code/User/globalStorage/github.copilot-chat/session-store.db"),
            os.path.expanduser("~/.config/Code - Insiders/User/globalStorage/github.copilot-chat/session-store.db"),
        ]

        appdata = os.environ.get("APPDATA")
        if appdata:
            local_db_paths.extend([
                str(Path(appdata) / "Code" / "User" / "globalStorage" / "github.copilot-chat" / "session-store.db"),
                str(Path(appdata) / "Code - Insiders" / "User" / "globalStorage" / "github.copilot-chat" / "session-store.db"),
            ])

        explicit_path = os.environ.get("SYNC_LOCAL_DB_PATH")
        if explicit_path:
            local_db_paths.insert(0, os.path.expandvars(os.path.expanduser(explicit_path)))

        explicit_paths = os.environ.get("SYNC_LOCAL_DB_PATHS")
        if explicit_paths:
            local_db_paths = _split_paths(explicit_paths) + local_db_paths

        return cls(
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            repo_owner=os.environ.get("SYNC_REPO_OWNER", ""),
            repo_name=os.environ.get("SYNC_REPO_NAME", ""),
            branch=os.environ.get("SYNC_BRANCH", "main"),
            db_file_path=os.environ.get("SYNC_DB_FILE_PATH", "session-store.db"),
            local_db_paths=list(dict.fromkeys(local_db_paths)),
            backup_dir=os.environ.get("SYNC_BACKUP_DIR"),
        )

    @classmethod
    def from_file(cls, config_path: str) -> "SyncConfig":
        """Load configuration from a JSON file."""
        path = Path(config_path)
        if not path.exists():
            return cls()
        
        with open(path) as f:
            data = json.load(f)
        
        return cls(
            github_token=data.get("github_token", ""),
            repo_owner=data.get("repo_owner", ""),
            repo_name=data.get("repo_name", ""),
            branch=data.get("branch", "main"),
            db_file_path=data.get("db_file_path", "session-store.db"),
            local_db_paths=data.get("local_db_paths", []),
            backup_dir=data.get("backup_dir"),
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "github_token": self.github_token,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "branch": self.branch,
            "db_file_path": self.db_file_path,
            "local_db_paths": self.local_db_paths,
            "backup_dir": self.backup_dir,
        }

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        if not self.github_token:
            errors.append("GITHUB_TOKEN is not set")
        if not self.repo_owner:
            errors.append("SYNC_REPO_OWNER is not set")
        if not self.repo_name:
            errors.append("SYNC_REPO_NAME is not set")
        return errors
