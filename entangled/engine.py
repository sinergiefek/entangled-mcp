"""
Entangled Core Engine: SQLite WAL Multi-Process Coordination Layer.
Zero-Daemon, Zero-Network-Dependency, Sub-millisecond Concurrency.
"""

import os
import sys
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

# Default database stored in user's home or local environment
DEFAULT_DB_DIR = os.path.expanduser("~/.entangled")
DEFAULT_DB_PATH = os.environ.get("ENTANGLED_DB_PATH", os.path.join(DEFAULT_DB_DIR, "entangled.db"))


@contextmanager
def get_db(db_path: str = DEFAULT_DB_PATH):
    """
    Context manager providing safe SQLite connections configured with WAL mode
    and busy_timeout to support seamless concurrent access across distinct CLI processes.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def utc_now_iso() -> str:
    """Returns the current UTC timestamp formatted as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class EntangledEngine:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        """Initializes relational tables and performance indexes for swarm coordination."""
        with get_db(self.db_path) as conn:
            # 1. Swarm Agent Nodes
            conn.execute("""
            CREATE TABLE IF NOT EXISTS swarm_nodes (
                agent_id TEXT PRIMARY KEY,
                client_type TEXT NOT NULL,
                current_workspace TEXT,
                active_task TEXT,
                status TEXT DEFAULT 'active',
                last_seen TIMESTAMP NOT NULL,
                metadata_json TEXT DEFAULT '{}'
            );
            """)

            # 2. Shared Knowledge Bus
            conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_bus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                tags TEXT,
                author_agent TEXT NOT NULL,
                workspace TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entangled_topic ON knowledge_bus(topic);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entangled_tags ON knowledge_bus(tags);")

            # 3. Inter-Agent Messages
            conn.execute("""
            CREATE TABLE IF NOT EXISTS inter_agent_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                sender_agent TEXT NOT NULL,
                target_agent TEXT NOT NULL,
                message_type TEXT DEFAULT 'notification',
                action TEXT NOT NULL,
                message TEXT NOT NULL,
                payload_json TEXT DEFAULT '{}',
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'unread',
                created_at TIMESTAMP NOT NULL,
                read_at TIMESTAMP
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entangled_msg_target ON inter_agent_messages(target_agent, status);")

            # 4. Resource Mutex Locks
            conn.execute("""
            CREATE TABLE IF NOT EXISTS resource_locks (
                resource_path TEXT PRIMARY KEY,
                locked_by_agent TEXT NOT NULL,
                client_type TEXT,
                task_description TEXT,
                acquired_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL
            );
            """)

            # 5. Chronological Swarm Activity Feed
            conn.execute("""
            CREATE TABLE IF NOT EXISTS swarm_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                action TEXT NOT NULL,
                summary TEXT NOT NULL,
                workspace TEXT,
                created_at TIMESTAMP NOT NULL
            );
            """)

    def announce_or_heartbeat(self, agent_id: str, client_type: str, current_workspace: str = "", active_task: str = "", status: str = "active", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Registers or refreshes an agent CLI node in the entangled swarm."""
        now = utc_now_iso()
        meta_str = json.dumps(metadata or {})
        with get_db(self.db_path) as conn:
            conn.execute("""
            INSERT INTO swarm_nodes (agent_id, client_type, current_workspace, active_task, status, last_seen, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                client_type=excluded.client_type,
                current_workspace=COALESCE(NULLIF(excluded.current_workspace, ''), swarm_nodes.current_workspace),
                active_task=COALESCE(NULLIF(excluded.active_task, ''), swarm_nodes.active_task),
                status=excluded.status,
                last_seen=excluded.last_seen,
                metadata_json=excluded.metadata_json;
            """, (agent_id, client_type, current_workspace, active_task, status, now, meta_str))

            conn.execute("""
            INSERT INTO swarm_activity (agent_id, action, summary, workspace, created_at)
            VALUES (?, 'HEARTBEAT', ?, ?, ?);
            """, (agent_id, f"Presence recorded on {client_type}. Task: {active_task or 'idle'}", current_workspace, now))

        return {"status": "ok", "agent_id": agent_id, "timestamp": now}

    def get_swarm_nodes(self) -> List[Dict[str, Any]]:
        """Returns all registered agent nodes and their latest presence states."""
        with get_db(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM swarm_nodes ORDER BY last_seen DESC;").fetchall()
            return [dict(r) for r in rows]

    def broadcast_knowledge(self, topic: str, content: str, title: str = "", tags: str = "", author_agent: str = "agent", workspace: str = "") -> int:
        """Publishes shared knowledge into the entangled bus."""
        now = utc_now_iso()
        with get_db(self.db_path) as conn:
            cur = conn.execute("""
            INSERT INTO knowledge_bus (topic, title, content, tags, author_agent, workspace, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (topic, title or topic, content, tags, author_agent, workspace, now, now))
            kid = cur.lastrowid

            conn.execute("""
            INSERT INTO swarm_activity (agent_id, action, summary, workspace, created_at)
            VALUES (?, 'BROADCAST_KNOWLEDGE', ?, ?, ?);
            """, (author_agent, f"Knowledge #{kid} broadcasted under '{topic}': {title or content[:60]}", workspace, now))

            return kid

    def query_knowledge(self, query: str = "", topic: str = "", tag: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Searches shared knowledge by topic, tag, or full-text keywords."""
        sql = "SELECT * FROM knowledge_bus WHERE 1=1"
        params = []
        if topic:
            sql += " AND topic LIKE ?"
            params.append(f"%{topic}%")
        if tag:
            sql += " AND tags LIKE ?"
            params.append(f"%{tag}%")
        if query:
            sql += " AND (title LIKE ? OR content LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with get_db(self.db_path) as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def send_message(self, target_agent: str, action: str, message: str, payload: Dict[str, Any] = None, sender_agent: str = "agent", priority: str = "normal", message_type: str = "notification") -> Dict[str, Any]:
        """Dispatches an asynchronous message or task delegation to a target agent or 'all'."""
        now = utc_now_iso()
        trace_id = str(uuid.uuid4())[:8]
        payload_str = json.dumps(payload or {})

        with get_db(self.db_path) as conn:
            cur = conn.execute("""
            INSERT INTO inter_agent_messages (trace_id, sender_agent, target_agent, message_type, action, message, payload_json, priority, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'unread', ?);
            """, (trace_id, sender_agent, target_agent, message_type, action, message, payload_str, priority, now))
            msg_id = cur.lastrowid

            conn.execute("""
            INSERT INTO swarm_activity (agent_id, action, summary, workspace, created_at)
            VALUES (?, 'SEND_MESSAGE', ?, '', ?);
            """, (sender_agent, f"Dispatched [{priority.upper()}] message #{msg_id} (action: {action}) to '{target_agent}'", now))

            return {"message_id": msg_id, "trace_id": trace_id, "status": "sent", "created_at": now}

    def check_inbox(self, agent_id: str, unread_only: bool = True, mark_as_read: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves pending messages addressed to this agent or to 'all'."""
        sql = "SELECT * FROM inter_agent_messages WHERE (target_agent = ? OR target_agent = 'all')"
        params = [agent_id]
        if unread_only:
            sql += " AND status = 'unread'"

        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with get_db(self.db_path) as conn:
            rows = conn.execute(sql, params).fetchall()
            results = [dict(r) for r in rows]

            if mark_as_read and results:
                ids = [r["id"] for r in results]
                placeholders = ",".join("?" for _ in ids)
                now = utc_now_iso()
                conn.execute(f"""
                UPDATE inter_agent_messages 
                SET status = 'read', read_at = ?
                WHERE id IN ({placeholders}) AND status = 'unread';
                """, [now] + ids)

            return results

    def acquire_lock(self, resource_path: str, agent_id: str, client_type: str = "agent-cli", task_description: str = "", ttl_seconds: int = 1800) -> Dict[str, Any]:
        """
        Acquires an exclusive mutex lock on a file or task to prevent concurrent modifications.
        Automatically evicts expired locks.
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        expires_at = datetime.fromtimestamp(now.timestamp() + ttl_seconds, tz=timezone.utc).isoformat()

        with get_db(self.db_path) as conn:
            conn.execute("DELETE FROM resource_locks WHERE expires_at < ?;", (now_iso,))
            existing = conn.execute("SELECT * FROM resource_locks WHERE resource_path = ?;", (resource_path,)).fetchone()
            if existing:
                if existing["locked_by_agent"] == agent_id:
                    conn.execute("UPDATE resource_locks SET expires_at = ?, task_description = ? WHERE resource_path = ?;", (expires_at, task_description or existing["task_description"], resource_path))
                    return {"status": "renewed", "resource_path": resource_path, "locked_by": agent_id, "expires_at": expires_at}
                else:
                    return {
                        "status": "locked_by_other",
                        "resource_path": resource_path,
                        "locked_by": existing["locked_by_agent"],
                        "client_type": existing["client_type"],
                        "task_description": existing["task_description"],
                        "expires_at": existing["expires_at"]
                    }

            conn.execute("""
            INSERT INTO resource_locks (resource_path, locked_by_agent, client_type, task_description, acquired_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (resource_path, agent_id, client_type, task_description, now_iso, expires_at))

            conn.execute("""
            INSERT INTO swarm_activity (agent_id, action, summary, workspace, created_at)
            VALUES (?, 'ACQUIRE_LOCK', ?, '', ?);
            """, (agent_id, f"Acquired mutex lock on '{resource_path}' for task: {task_description}", now_iso))

            return {"status": "acquired", "resource_path": resource_path, "locked_by": agent_id, "expires_at": expires_at}

    def release_lock(self, resource_path: str, agent_id: str) -> Dict[str, Any]:
        """Releases an active mutex lock."""
        now_iso = utc_now_iso()
        with get_db(self.db_path) as conn:
            existing = conn.execute("SELECT * FROM resource_locks WHERE resource_path = ?;", (resource_path,)).fetchone()
            if not existing:
                return {"status": "not_locked", "resource_path": resource_path}

            if existing["locked_by_agent"] != agent_id and agent_id not in ("admin", "pipi", "root"):
                return {"status": "permission_denied", "resource_path": resource_path, "locked_by": existing["locked_by_agent"]}

            conn.execute("DELETE FROM resource_locks WHERE resource_path = ?;", (resource_path,))
            conn.execute("""
            INSERT INTO swarm_activity (agent_id, action, summary, workspace, created_at)
            VALUES (?, 'RELEASE_LOCK', ?, '', ?);
            """, (agent_id, f"Released lock on '{resource_path}'", now_iso))

            return {"status": "released", "resource_path": resource_path}

    def list_locks(self) -> List[Dict[str, Any]]:
        """Lists all active and unexpired mutex locks."""
        now_iso = utc_now_iso()
        with get_db(self.db_path) as conn:
            conn.execute("DELETE FROM resource_locks WHERE expires_at < ?;", (now_iso,))
            rows = conn.execute("SELECT * FROM resource_locks ORDER BY acquired_at DESC;").fetchall()
            return [dict(r) for r in rows]

    def get_activity_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves chronological activity entries across the entire swarm."""
        with get_db(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM swarm_activity ORDER BY id DESC LIMIT ?;", (limit,)).fetchall()
            return [dict(r) for r in rows]
