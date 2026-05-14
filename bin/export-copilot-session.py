#!/usr/bin/env python3
"""
Export today's Copilot Chat sessions as a markdown summary for journal inclusion.

Usage:
  ./bin/export-copilot-session.py [date]
    date: YYYY-MM-DD (default: today)

Output: prints markdown to stdout

Dependencies: sqlite3 CLI must be available on PATH.
"""

import json
import os
import subprocess
import sys
from datetime import date as Date


def find_session_db() -> str | None:
    """Locate the Copilot session store database."""
    candidates = [
        os.environ.get("SESSION_DB"),
        os.path.expanduser(
            "~/.vscode-server-insiders/data/User/globalStorage/github.copilot-chat/session-store.db"
        ),
        os.path.expanduser(
            "~/.config/Code - Insiders/User/globalStorage/github.copilot-chat/session-store.db"
        ),
        os.path.expanduser(
            "~/.vscode-server/data/User/globalStorage/github.copilot-chat/session-store.db"
        ),
        os.path.expanduser(
            "~/.config/Code/User/globalStorage/github.copilot-chat/session-store.db"
        ),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def query_json(db_path: str, sql: str) -> list[dict]:
    """Run SQL on the session store and return parsed JSON."""
    result = subprocess.run(
        ["sqlite3", db_path, "-json", sql],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def query_turns(db_path: str, session_id: str, limit: int = 10) -> list[tuple]:
    """Get conversation turns for a session."""
    sql = (
        "SELECT turn_index, user_message, substr(assistant_response, 1, 200) "
        "FROM turns WHERE session_id = ? ORDER BY turn_index ASC LIMIT ?"
    )
    result = subprocess.run(
        ["sqlite3", db_path, "-separator", "|", sql],
        input=f"{session_id}\n{limit}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    if not result.stdout.strip():
        return []
    rows = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("|", 2)
        if len(parts) == 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def truncate(text: str, max_len: int = 150) -> str:
    return text if len(text) <= max_len else text[:max_len] + "..."


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else str(Date.today())

    db_path = find_session_db()
    if not db_path:
        print("⚠️  Copilot session store not found.", file=sys.stderr)
        print("   Session tracking may be disabled.", file=sys.stderr)
        return

    # Query sessions
    sql = f"""
    SELECT s.id,
           coalesce(s.summary,'') as summary,
           coalesce(s.agent_name,'') as agent_name,
           coalesce(s.repository,'') as repository,
           coalesce(s.branch,'') as branch,
           s.created_at,
           s.updated_at,
           coalesce((SELECT COUNT(*) FROM turns t WHERE t.session_id=s.id),0) as turn_count,
           coalesce((SELECT GROUP_CONCAT(sf.file_path,'|') FROM (SELECT DISTINCT file_path FROM session_files WHERE session_id=s.id) sf),'') as files
    FROM sessions s
    WHERE date(s.created_at)=date('{target_date}')
    ORDER BY s.created_at ASC;
    """
    sessions = query_json(db_path, sql)

    if not sessions:
        return

    print("## Copilot Chat Activity")
    print()
    print(f"_Sessions from {target_date}_")
    print()

    for s in sessions:
        sid = (s.get("id") or "")[:8]
        summary = (s.get("summary") or "").strip() or "Untitled session"
        agent = (s.get("agent_name") or "").strip() or "default"
        repo = (s.get("repository") or "").strip()
        branch = (s.get("branch") or "").strip()
        turn_count = s.get("turn_count", 0)
        files_str = (s.get("files") or "").strip()
        created = (s.get("created_at") or "")[:16].replace("T", " ")

        print(f"### Session {sid} ({agent})")
        print(f"- **Time:** {created}")
        print(f"- **Summary:** {summary}")
        print(f"- **Turns:** {turn_count}")
        if repo:
            print(f"- **Repo:** {repo} ({branch})")
        if files_str:
            files_list = [f.strip() for f in files_str.split("|") if f.strip()]
            if files_list:
                display = files_list[:5]
                if len(files_list) > 5:
                    display.append(f"... +{len(files_list) - 5} more")
                print(f"- **Files:** " + " ".join(display))
        print()

        # Get turns
        turns = query_turns(db_path, s["id"])
        if turns:
            print("  <details>")
            print("  <summary>Conversation turns</summary>")
            print()
            for idx, user_msg, asst_resp in turns:
                print(f"  **Turn {idx}** — User: {truncate(user_msg)}")
                print(f"  _Copilot: {truncate(asst_resp)}_")
                print()
            print("  </details>")
            print()


if __name__ == "__main__":
    main()