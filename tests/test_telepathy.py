"""
Automated Test Suite for Entangled Engine.
Tests concurrency, knowledge persistence, messaging, and mutex locking.
"""

import os
import tempfile
from entangled.engine import EntangledEngine

def test_entangled_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_entangled.db")
        engine = EntangledEngine(db_path=test_db)

        # 1. Announce / Heartbeat
        res1 = engine.announce_or_heartbeat("antigravity-gemini", "antigravity-cli", "/workspace", "Frontend Task")
        assert res1["status"] == "ok"
        nodes = engine.get_swarm_nodes()
        assert len(nodes) == 1
        assert nodes[0]["agent_id"] == "antigravity-gemini"

        # 2. Knowledge Broadcast & Retrieval
        kid = engine.broadcast_knowledge("arch-decision", "Using SQLite WAL with 5s timeout", "SQLite WAL ADR", "db,wal", "antigravity-gemini")
        assert kid > 0
        items = engine.query_knowledge(topic="arch-decision")
        assert len(items) == 1
        assert items[0]["title"] == "SQLite WAL ADR"

        # 3. Inter-Agent Direct Messaging
        msg = engine.send_message("opencode-claude", "review_code", "Please audit the latest commit", {"commit": "HEAD"}, "antigravity-gemini", "high")
        assert msg["status"] == "sent"

        inbox = engine.check_inbox("opencode-claude", unread_only=True)
        assert len(inbox) == 1
        assert inbox[0]["sender_agent"] == "antigravity-gemini"
        assert inbox[0]["action"] == "review_code"

        # Check marked as read
        inbox_empty = engine.check_inbox("opencode-claude", unread_only=True)
        assert len(inbox_empty) == 0

        # 4. Mutex Locking & Conflict Prevention
        lock1 = engine.acquire_lock("src/index.ts", "antigravity-gemini", "antigravity-cli", "Refactoring", 60)
        assert lock1["status"] == "acquired"

        # Second agent tries to lock same file -> should be rejected
        lock2 = engine.acquire_lock("src/index.ts", "opencode-claude", "opencode-cli", "Conflicting edit", 60)
        assert lock2["status"] == "locked_by_other"
        assert lock2["locked_by"] == "antigravity-gemini"

        # Release lock
        rel = engine.release_lock("src/index.ts", "antigravity-gemini")
        assert rel["status"] == "released"

        # Now second agent can acquire
        lock3 = engine.acquire_lock("src/index.ts", "opencode-claude", "opencode-cli", "Now allowed", 60)
        assert lock3["status"] == "acquired"

        # 5. Activity Feed
        feed = engine.get_activity_feed(limit=10)
        assert len(feed) >= 5

if __name__ == "__main__":
    test_entangled_lifecycle()
    print("✅ All Entangled unit tests passed successfully!")
