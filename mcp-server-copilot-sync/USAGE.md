# Copilot Sync MCP Server - Usage Guide

## Quick Start

### 1. Install the MCP Server

```bash
cd /home/eric/markdown-journal-rust/mcp-server-copilot-sync
pip3 install -e .
```

### 2. Set Up Environment Variables

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# GitHub Personal Access Token (with repo scope)
export GITHUB_TOKEN="ghp_your_token_here"

# Repository details
export SYNC_REPO_OWNER="your-github-username"
export SYNC_REPO_NAME="copilot-sync"

# Optional settings
export SYNC_BRANCH="main"
export SYNC_DB_FILE_PATH="session-store.db"
export SYNC_LOCAL_DB_PATH="/path/to/session-store.db"
export SYNC_BACKUP_DIR="$HOME/copilot-sync-backups"
```

Then reload:

```bash
source ~/.bashrc
```

### 3. Create a Private GitHub Repository

```bash
# Create a new private repository on GitHub
# Name it: copilot-sync (or whatever you set in SYNC_REPO_NAME)
```

### 4. Configure VS Code MCP

Add to your VS Code settings (`~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/settings.json`):

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

### 5. Use in Copilot Chat

Once configured, you can use these tools in Copilot Chat:

#### Push sessions to GitHub

```
/mcp/copilot-sync:copilot-sync-push
```

Or with a specific date:

```
/mcp/copilot-sync:copilot-sync-push(date="2026-05-14")
```

#### Pull sessions from GitHub

```
/mcp/copilot-sync:copilot-sync-pull(replace_local=true)
```

#### Check sync status

```
/mcp/copilot-sync:copilot-sync-status
```

## Detailed Usage

### Push Sessions

Pushes your local `session-store.db` to the GitHub repository.

**When to use:**
- Before switching to a different machine
- As part of your end-of-day workflow
- After important Copilot Chat sessions

**Example:**

```
Please push my Copilot Chat sessions to GitHub.
```

The server will:
1. Find your local `session-store.db`
2. Count the sessions
3. Upload the database to GitHub
4. Create a commit with the session count and date

**Response:**

```json
{
  "success": true,
  "message": "Successfully pushed 7 sessions to GitHub",
  "sessions_count": 7,
  "timestamp": "2026-05-14T15:30:00"
}
```

### Pull Sessions

Pulls the latest `session-store.db` from GitHub to your local machine.

**When to use:**
- After switching to a different machine
- To restore sessions from a backup
- To sync sessions from your Windows machine to Linux

**Example:**

```
Please pull my Copilot Chat sessions from GitHub.
```

The server will:
1. Download the database from GitHub
2. Create a backup of your local database (if it exists)
3. Replace the local database with the pulled version
4. Count the sessions

**Response:**

```json
{
  "success": true,
  "message": "Successfully pulled 7 sessions from GitHub",
  "sessions_count": 7,
  "timestamp": "2026-05-14T15:35:00"
}
```

### Check Sync Status

Shows the current state of your local and GitHub sessions.

**When to use:**
- Before pushing or pulling
- To verify the sync is working
- To check session counts

**Example:**

```
What's my Copilot sync status?
```

**Response:**

```json
{
  "local_db": "/home/eric/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db",
  "local_sessions": 7,
  "github_available": true,
  "last_sync": "2026-05-14T15:30:00"
}
```

## Integration with Daily Workflow

### Using with Claude Code

Add to your `.claude/commands/commit.md`:

```markdown
1. Run the `journal-field-completer` agent on today's file.
2. Run the `daily-summary` agent for today's file.
3. Push Copilot sessions: `/mcp/copilot-sync:copilot-sync-push`
4. Export sessions to markdown: `./bin/export-copilot-session.sh`
5. Append export output to today's journal file.
6. Commit and push.
```

### Using with Shell Scripts

Add to your end-of-day script:

```bash
#!/bin/bash
# End-of-day sync script

# Push sessions to GitHub
python3 -c "
import os, sys
sys.path.insert(0, '/home/eric/markdown-journal-rust/mcp-server-copilot-sync/src')
from mcp_server_copilot_sync.config import SyncConfig
from mcp_server_copilot_sync.sync import CopilotSync

config = SyncConfig.from_env()
sync = CopilotSync(config)
result = sync.push_to_github()
print(result['message'])
"

# Export sessions to markdown
./bin/export-copilot-session.sh >> journal/$(date +%Y)/$(date +%m)/$(date +%Y-%m-%d).md

# Commit and push
git add -A
git commit -m "journal: $(date +%Y-%m-%d)"
git push
```

## Troubleshooting

### Common Issues

#### 1. "GITHUB_TOKEN is not set"

**Solution:** Set the environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Or add it to your shell profile (`~/.bashrc` or `~/.zshrc`).

#### 2. "No local session-store.db found"

**Solution:** Verify the database exists:

```bash
ls -la ~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db
```

If it doesn't exist, enable Copilot Chat in VS Code and have a conversation.

#### 3. "GitHub API error: 404"

**Solution:** Verify the repository exists and is accessible:

```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/$SYNC_REPO_OWNER/$SYNC_REPO_NAME
```

#### 4. "Authentication Failed"

**Solution:** Ensure your token has the `repo` scope:
1. Go to https://github.com/settings/tokens
2. Find your token
3. Ensure `repo` scope is checked
4. Regenerate the token if needed

#### 5. MCP Server Not Loading in VS Code

**Solution:** Check the VS Code output:
1. Open Output panel (`View > Output`)
2. Select "MCP Server" from the dropdown
3. Look for errors

Common fixes:
- Verify Python path is correct
- Check that all dependencies are installed
- Restart VS Code

### Debugging

Enable verbose logging in VS Code:

```json
{
  "mcp.verbose": true
}
```

Test the server from the command line:

```bash
cd /home/eric/markdown-journal-rust/mcp-server-copilot-sync
PYTHONPATH=src python3 tests/test_sync.py
```

Check configuration:

```bash
python3 -c "
import os, sys
sys.path.insert(0, 'src')
from mcp_server_copilot_sync.config import SyncConfig
config = SyncConfig.from_env()
print(config.to_dict())
"
```

## Session Store Database Locations

### Linux (Remote Server)

```bash
# VS Code Insiders
~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db

# VS Code Stable
~/.vscode-server/data/User/globalStorage/github.copilot-chat/session-store.db

# VS Code Insiders (config path)
~/.config/Code - Insiders/User/globalStorage/github.copilot-chat/session-store.db
```

### Windows (Local Machine)

```
# VS Code Insiders
%APPDATA%\Code - Insiders\User\globalStorage\github.copilot-chat\session-store.db

# VS Code Stable
%APPDATA%\Code\User\globalStorage\github.copilot-chat\session-store.db
```

## Security Notes

- **Never commit your `GITHUB_TOKEN`** to version control
- Use environment variables or secure secret management
- The session database may contain sensitive conversation data
- Consider encrypting the database before uploading to GitHub
- Regularly rotate your GitHub Personal Access Token

## Advanced Usage

### Custom Database Path

If your database is in a non-standard location:

```bash
export SYNC_DB_PATH="/custom/path/to/session-store.db"
```

### Multiple Repositories

You can configure multiple repositories by creating multiple MCP server instances:

```json
{
  "mcp.servers": {
    "copilot-sync-work": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": {
        "GITHUB_TOKEN": "${env:WORK_GITHUB_TOKEN}",
        "SYNC_REPO_OWNER": "${env:WORK_REPO_OWNER}",
        "SYNC_REPO_NAME": "${env:WORK_REPO_NAME}"
      }
    },
    "copilot-sync-personal": {
      "command": "python3",
      "args": ["/path/to/server.py"],
      "env": {
        "GITHUB_TOKEN": "${env:PERSONAL_GITHUB_TOKEN}",
        "SYNC_REPO_OWNER": "${env:PERSONAL_REPO_OWNER}",
        "SYNC_REPO_NAME": "${env:PERSONAL_REPO_NAME}"
      }
    }
  }
}
```

### Backup Management

The server automatically creates backups when pulling:

```bash
# Backups are stored in:
$HOME/copilot-sync-backups/

# Backup file format:
session-store-backup-YYYYMMDD-HHMMSS.db
```

To clean up old backups:

```bash
# Remove backups older than 30 days
find $HOME/copilot-sync-backups -name "session-store-backup-*.db" -mtime +30 -delete
```
