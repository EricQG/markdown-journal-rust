# MCP Server for Copilot Chat Sync

> Sync GitHub Copilot Chat sessions between your local Windows machine and remote Linux server via a private GitHub repository.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [VS Code MCP Configuration](#vs-code-mcp-configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Integration with Export Script](#integration-with-export-script)
- [Session Store Database Location](#session-store-database-location)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)
- [License](#license)

## Overview

This MCP (Model Context Protocol) server provides tools to synchronize GitHub Copilot Chat sessions between multiple machines. It stores session data in a private GitHub repository, enabling seamless sync between your local development environment and remote servers.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Push** | Upload local Copilot Chat sessions to a private GitHub repository |
| **Pull** | Download sessions from GitHub to your local machine |
| **Status** | Check sync status between local and remote sessions |
| **Backup** | Automatic backup before overwriting local database |
| **Cross-platform** | Works on Windows, Linux, and macOS |

## Architecture

```
+-------------------+         +------------------+         +-------------------+
|  Local Windows    |         |  Private GitHub  |         |  Remote Linux     |
|  VS Code +        |<------->|  Repository      |<------->|  VS Code +        |
|  Copilot Chat     |  Push   |  (session-store  |  Pull   |  Copilot Chat     |
|                   |         |   .db)           |         |                   |
+-------------------+         +------------------+         +-------------------+
```

## Prerequisites

- **Python 3.10+** with `pip` or `uv` package manager
- **GitHub account** with a private repository
- **GitHub Personal Access Token** with `repo` scope (fine-grained recommended)
- **VS Code** with GitHub Copilot extension installed
- **Network access** to `api.github.com`

## Installation

### 1. Install the MCP server

```bash
cd mcp-server-copilot-sync
pip install -e .
```

Or using uv:

```bash
uv pip install -e .
```

### 2. Verify installation

```bash
python -m mcp_server_copilot_sync --help
```

## Configuration

### Environment Variables

Set the following environment variables before running the MCP server:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | - | GitHub Personal Access Token with `repo` scope |
| `SYNC_REPO_OWNER` | Yes | - | GitHub username or organization name |
| `SYNC_REPO_NAME` | Yes | - | Name of the private repository |
| `SYNC_BRANCH` | No | `main` | Branch to sync against |
| `SYNC_DB_FILE_PATH` | No | `session-store.db` | Filename for the local database copy |
| `SYNC_LOCAL_DB_PATH` | No | Auto-detected | Full path to the local Copilot Chat session-store.db |
| `SYNC_BACKUP_DIR` | No | `$HOME/copilot-sync-backups` | Directory for backup files |

### Setting Environment Variables

**Linux/macOS (bash/zsh):**

```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_your_personal_access_token"
export SYNC_REPO_OWNER="your-github-username"
export SYNC_REPO_NAME="your-private-repo-name"
export SYNC_BRANCH="main"
export SYNC_BACKUP_DIR="$HOME/copilot-sync-backups"
```

**Windows (PowerShell - $PROFILE):**

```powershell
$env:GITHUB_TOKEN = "ghp_your_personal_access_token"
$env:SYNC_REPO_OWNER = "your-github-username"
$env:SYNC_REPO_NAME = "your-private-repo-name"
```

**Windows (Command Prompt - setx):**

```cmd
setx GITHUB_TOKEN "ghp_your_personal_access_token"
setx SYNC_REPO_OWNER "your-github-username"
setx SYNC_REPO_NAME "your-private-repo-name"
```

### Creating a GitHub Repository

```bash
# Create a new private repository on GitHub
# Recommended name: copilot-sync or copilot-sessions
gh repo create copilot-sync --private --clone
cd copilot-sync
git checkout -b main
```

## VS Code MCP Configuration

Add the MCP server to your VS Code Copilot Chat settings.

### For VS Code Insiders (Linux/Remote)

Edit `~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/settings.json`:

```json
{
  "mcp.servers": {
    "copilot-sync": {
      "command": "python3",
      "args": ["-m", "mcp_server_copilot_sync"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}",
        "SYNC_REPO_OWNER": "${env:SYNC_REPO_OWNER}",
        "SYNC_REPO_NAME": "${env:SYNC_REPO_NAME}"
      }
    }
  }
}
```

### For Local VS Code (Windows)

Edit `%APPDATA%\Code\User\globalStorage\github.copilot-chat\settings.json`:

```json
{
  "mcp.servers": {
    "copilot-sync": {
      "command": "python",
      "args": ["-m", "mcp_server_copilot_sync"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}",
        "SYNC_REPO_OWNER": "${env:SYNC_REPO_OWNER}",
        "SYNC_REPO_NAME": "${env:SYNC_REPO_NAME}",
        "SYNC_LOCAL_DB_PATH": "C:\\Users\\YOUR_NAME\\AppData\\Roaming\\Code\\User\\globalStorage\\github.copilot-chat\\session-store.db"
      }
    }
  }
}
```

### For VS Code Stable

Edit `%APPDATA%\Code\User\globalStorage\github.copilot-chat\settings.json` (Windows)
or `~/.vscode/data/User/globalStorage/github.copilot-chat/settings.json` (Linux)

## Usage

### Using MCP Tools in Copilot Chat

Once configured, use these tools directly in Copilot Chat:

#### Push sessions to GitHub

Upload your local Copilot Chat sessions to the GitHub repository:

```
/mcp/copilot-sync:copilot-sync-push
```

With optional date filter:

```
/mcp/copilot-sync:copilot-sync-push(date="2026-05-14")
```

#### Pull sessions from GitHub

Download sessions from GitHub to your local machine:

```
/mcp/copilot-sync:copilot-sync-pull
```

With option to replace local database:

```
/mcp/copilot-sync:copilot-sync-pull(replace_local=true)
```

> **Warning:** Setting `replace_local=true` will replace your local session-store.db with the remote version. A backup is automatically created before replacement.

#### Check sync status

View the current sync status between local and remote sessions:

```
/mcp/copilot-sync:copilot-sync-status
```

### Using with Claude Code

Integrate sync into your Claude Code workflow. Add to your `.claude/commands/commit.md`:

```markdown
1. Run the `journal-field-completer` agent on today's file.
2. Run the `daily-summary` agent for today's file.
3. Push Copilot sessions: `/mcp/copilot-sync:copilot-sync-push`
4. Commit and push.
```

## API Reference

### Tool: `copilot-sync-push`

Push local Copilot Chat sessions to GitHub.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | No | All dates | Filter sessions by date (YYYY-MM-DD) |

**Success Response:**

```json
{
  "success": true,
  "message": "Successfully pushed 7 sessions to GitHub",
  "details": {
    "sessions_pushed": 7,
    "repo": "EricQG/copilot-sync",
    "branch": "main",
    "file_size_bytes": 45678,
    "timestamp": "2026-05-14T10:30:00Z"
  }
}
```

**Error Response:**

```json
{
  "success": false,
  "error": "Failed to push to GitHub",
  "details": {
    "status_code": 403,
    "message": "Resource not accessible by personal access token"
  }
}
```

### Tool: `copilot-sync-pull`

Pull Copilot Chat sessions from GitHub.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `replace_local` | boolean | No | `false` | Replace local database with remote version |

**Success Response (without replace):**

```json
{
  "success": true,
  "message": "Successfully pulled 7 sessions from GitHub",
  "details": {
    "sessions_count": 7,
    "repo": "EricQG/copilot-sync",
    "branch": "main",
    "file_size_bytes": 45678,
    "timestamp": "2026-05-14T10:35:00Z",
    "backup_created": false
  }
}
```

**Success Response (with replace):**

```json
{
  "success": true,
  "message": "Successfully pulled and replaced local database",
  "details": {
    "sessions_count": 7,
    "repo": "EricQG/copilot-sync",
    "branch": "main",
    "file_size_bytes": 45678,
    "timestamp": "2026-05-14T10:35:00Z",
    "backup_created": true,
    "backup_path": "/home/user/copilot-sync-backups/session-store-20260514-103500.db"
  }
}
```

### Tool: `copilot-sync-status`

Check the current sync status.

**Success Response:**

```json
{
  "success": true,
  "message": "Sync status retrieved successfully",
  "details": {
    "local_db_exists": true,
    "local_db_path": "/home/user/.vscode-server-insiders/.../session-store.db",
    "local_db_size_bytes": 42000,
    "remote_db_exists": true,
    "remote_db_size_bytes": 45678,
    "last_push": "2026-05-14T10:30:00Z",
    "last_pull": "2026-05-13T15:20:00Z",
    "is_in_sync": false,
    "sessions_count": 7
  }
}
```

## Integration with Export Script

The synced sessions can be exported to markdown format using the companion export script:

```bash
# After pulling sessions, export them to markdown
./bin/export-copilot-session.sh 2026-05-14
```

This converts the SQLite session database into readable markdown files organized by date.

## Session Store Database Location

The MCP server auto-detects the Copilot Chat session-store.db location. Manual override via `SYNC_LOCAL_DB_PATH` is available.

### Windows (Local)

| Edition | Path |
|---------|------|
| VS Code Stable | `%APPDATA%\Code\User\globalStorage\github.copilot-chat\session-store.db` |
| VS Code Insiders | `%APPDATA%\Code - Insiders\User\globalStorage\github.copilot-chat\session-store.db` |

### Linux (Remote Server)

| Edition | Path |
|---------|------|
| VS Code Server | `~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db` |
| VS Code Stable Server | `~/.vscode-server/data/User/globalStorage/github.copilot-chat/session-store.db` |

### macOS

| Edition | Path |
|---------|------|
| VS Code Stable | `~/Library/Application Support/Code/User/globalStorage/github.copilot-chat/session-store.db` |
| VS Code Insiders | `~/Library/Application Support/Code - Insiders/User/globalStorage/github.copilot-chat/session-store.db` |

## Troubleshooting

### Common Issues

#### 1. Authentication Failed (403 Error)

**Error:** `Resource not accessible by personal access token`

**Solution:**
- Ensure your token has the `repo` scope (for classic PAT) or `Contents` permission (for fine-grained PAT)
- Generate a new token at: https://github.com/settings/tokens
- For fine-grained tokens, grant `Contents` read and write access to the repository

#### 2. No Local Database Found

**Error:** `Local database not found at: /path/to/session-store.db`

**Solution:**
- Verify Copilot Chat is enabled and has been used in VS Code
- Check the database exists at the expected location
- Use `copilot-sync-status` to verify the detected path
- Set `SYNC_LOCAL_DB_PATH` explicitly if auto-detection fails

#### 3. Sync Fails with Network Error

**Error:** `Failed to connect to GitHub API`

**Solution:**
- Check network connectivity: `curl -I https://api.github.com`
- Verify proxy settings if behind a corporate firewall
- Check GitHub status: https://www.githubstatus.com/

#### 4. Repository Not Found (404 Error)

**Error:** `Repository not found`

**Solution:**
- Verify `SYNC_REPO_OWNER` and `SYNC_REPO_NAME` are correct
- Ensure the repository exists and is private
- Check that your token has access to the repository

#### 5. MCP Server Not Loading in VS Code

**Solution:**
- Verify Python path is correct: `which python3` (Linux) or `where python` (Windows)
- Check dependencies are installed: `pip list | grep -i mcp`
- Review VS Code output logs: `View > Output > MCP Server`
- Restart VS Code after changing settings

#### 6. Backup Directory Creation Failed

**Solution:**
- Ensure the backup directory path is writable
- Create the directory manually: `mkdir -p $SYNC_BACKUP_DIR`

### Debugging

#### Enable Verbose Logging

Add to your VS Code settings:

```json
{
  "mcp.verbose": true
}
```

#### Check MCP Server Logs

1. Open VS Code
2. Go to `View > Output`
3. Select `MCP Server` from the dropdown
4. Look for error messages or warnings

#### Test Configuration Manually

```bash
# Test GitHub API access
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/$SYNC_REPO_OWNER/$SYNC_REPO_NAME

# Test database access
python3 -c "import sqlite3; conn = sqlite3.connect('$SYNC_LOCAL_DB_PATH'); print(conn.execute('SELECT count(*) FROM sessions').fetchone())"
```

### Error Code Reference

| Status Code | Meaning | Solution |
|-------------|---------|----------|
| 401 | Unauthorized | Check GITHUB_TOKEN validity |
| 403 | Forbidden | Check token scopes/permissions |
| 404 | Not Found | Verify repo owner/name |
| 422 | Validation Error | Check branch name exists |
| 500 | Server Error | Check GitHub status page |
| 503 | Service Unavailable | Retry after GitHub maintenance |

## Project Structure

```
mcp-server-copilot-sync/
├── pyproject.toml              # Project configuration (build, dependencies, entry points)
├── README.md                   # This file
├── test_mcp_server.py          # Integration test script
├── src/
│   └── mcp_server_copilot_sync/
│       ├── __init__.py         # Package initialization, exports main()
│       ├── __main__.py         # CLI entry point for python -m
│       ├── server.py           # MCP server implementation with tool definitions
│       ├── config.py           # Configuration management (SyncConfig dataclass)
│       └── sync.py             # Core sync logic (CopilotSync class)
├── scripts/
│   ├── install.sh              # Automated installation script
│   └── setup.sh                # Configuration setup helper
└── tests/
    ├── __init__.py
    └── test_autoresearch_codex.py
```

### Key Files

| File | Purpose |
|------|---------|
| `src/mcp_server_copilot_sync/server.py` | Defines MCP tools: `copilot-sync-push`, `copilot-sync-pull`, `copilot-sync-status` |
| `src/mcp_server_copilot_sync/config.py` | `SyncConfig` dataclass with `from_env()` and `from_file()` methods |
| `src/mcp_server_copilot_sync/sync.py` | `CopilotSync` class with `push_to_github()`, `pull_from_github()`, `get_sync_status()` |
| `pyproject.toml` | Build system (setuptools), dependencies (mcp, requests), entry point |

## Security Notes

- **Never commit your `GITHUB_TOKEN`** to version control or share it publicly
- Use environment variables or a secure secret management solution
- The session database may contain sensitive conversation data
- Consider encrypting the database before uploading to GitHub
- Regularly rotate your GitHub Personal Access Token
- Use fine-grained tokens with minimum required permissions
- The private repository should be named to not reveal its purpose if concerned about metadata

### Token Best Practices

1. Use **fine-grained personal access tokens** instead of classic tokens
2. Set an **expiration date** on your token
3. Grant access to **only the specific repository** you need
4. Revoke unused tokens regularly
5. Monitor token usage in GitHub settings

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
