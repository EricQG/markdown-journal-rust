# Copilot Sync MCP Server - Quick Reference

## 🚀 Quick Start (3 steps)

### 1. Install
```bash
cd /home/eric/markdown-journal-rust/mcp-server-copilot-sync
pip3 install -e .
```

### 2. Configure
```bash
# Add to ~/.bashrc
export GITHUB_TOKEN="ghp_your_token_here"
export SYNC_REPO_OWNER="your-github-username"
export SYNC_REPO_NAME="copilot-sync"
export SYNC_LOCAL_DB_PATH="/path/to/session-store.db"  # optional override

source ~/.bashrc
```

### 3. Use in VS Code
Add to VS Code settings:
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

## 📋 MCP Tools

| Tool | Description | Example |
|------|-------------|---------|
| `copilot-sync-push` | Push local sessions to GitHub | `/mcp/copilot-sync:copilot-sync-push` |
| `copilot-sync-pull` | Pull sessions from GitHub | `/mcp/copilot-sync:copilot-sync-pull` |
| `copilot-sync-status` | Check sync status | `/mcp/copilot-sync:copilot-sync-status` |

## 🔧 Command Line Usage

### Test local DB detection
```bash
python3 scripts/demo.py
```

### Check sync status
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from mcp_server_copilot_sync.config import SyncConfig
from mcp_server_copilot_sync.sync import CopilotSync

config = SyncConfig.from_env()
sync = CopilotSync(config)
print(sync.get_sync_status())
"
```

### Push sessions manually
```bash
python3 -c "
import sys, os
sys.path.insert(0, 'src')
os.environ['GITHUB_TOKEN'] = 'ghp_token'
os.environ['SYNC_REPO_OWNER'] = 'username'
os.environ['SYNC_REPO_NAME'] = 'repo'
from mcp_server_copilot_sync.config import SyncConfig
from mcp_server_copilot_sync.sync import CopilotSync

config = SyncConfig.from_env()
sync = CopilotSync(config)
result = sync.push_to_github()
print(result['message'])
"
```

## 📁 Project Structure

```
mcp-server-copilot-sync/
├── pyproject.toml              # Project configuration
├── README.md                   # Full documentation
├── USAGE.md                    # Detailed usage guide
├── config.example.json         # Example configuration
├── .gitignore                  # Git ignore rules
├── src/
│   └── mcp_server_copilot_sync/
│       ├── __init__.py         # Package init
│       ├── __main__.py         # CLI entry point
│       ├── server.py           # MCP server implementation
│       ├── config.py           # Configuration management
│       └── sync.py             # Sync logic
├── scripts/
│   ├── demo.py                 # Demo/test script
│   ├── install.sh              # Installation script
│   └── setup.sh                # Configuration setup
└── tests/
    └── test_sync.py            # Unit tests
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "GITHUB_TOKEN is not set" | Set `export GITHUB_TOKEN="ghp_..."` in ~/.bashrc |
| "No local session-store.db found" | Verify Copilot Chat is enabled in VS Code |
| "GitHub API error: 404" | Check repo exists and token has `repo` scope |
| MCP server not loading | Check VS Code Output > MCP Server for errors |

## 📊 Session Store Locations

### Linux
```bash
# VS Code Insiders
~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db

# VS Code Stable
~/.vscode-server/data/User/globalStorage/github.copilot-chat/session-store.db
```

### Windows
```
%APPDATA%\Code\User\globalStorage\github.copilot-chat\session-store.db
%APPDATA%\Code - Insiders\User\globalStorage\github.copilot-chat\session-store.db
```

## 🔗 Integration

### With export-copilot-session.py
```bash
# After pulling sessions, export to markdown
./bin/export-copilot-session.sh 2026-05-14
```

### With Claude Code
Add to `.claude/commands/commit.md`:
```markdown
3. Push Copilot sessions: `/mcp/copilot-sync:copilot-sync-push`
```

## 📖 Documentation

- **README.md** - Full project documentation
- **USAGE.md** - Detailed usage guide with examples
- **config.example.json** - Example configuration file

## ⚠️ Security

- Never commit `GITHUB_TOKEN` to version control
- Use environment variables for secrets
- Regularly rotate your GitHub Personal Access Token
- The session database may contain sensitive data
