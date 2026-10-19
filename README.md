<div align="center">

# ⚛️ Entangled-MCP
### Instant Quantum Entanglement for Heterogeneous AI Agent CLIs

[![License: MIT](https://img.shields.io/badge/License-MIT-0B1220?style=for-the-badge&logoColor=white)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-0B1220?style=for-the-badge&logo=python&logoColor=38BDF8)](https://python.org)
[![MCP Protocol: 2026 Ready](https://img.shields.io/badge/MCP-2026_Standard-0B1220?style=for-the-badge&logo=connectwise&logoColor=F59E0B)](https://modelcontextprotocol.io)
[![Zero-Daemon: SQLite WAL](https://img.shields.io/badge/Engine-Zero--Daemon_WAL-0B1220?style=for-the-badge&logo=sqlite&logoColor=10B981)](README.md)
[![Swarm: Heterogeneous CLIs](https://img.shields.io/badge/Swarm-Antigravity_%7C_Opencode_%7C_Claude-0B1220?style=for-the-badge&logoColor=EC4899)](README.md)
[![Architecture: PSTACK](https://img.shields.io/badge/PSTACK-Mandate_6_Compliant-0B1220?style=for-the-badge&logoColor=8B5CF6)](https://github.com/sinergiefek)

**The sovereign, zero-daemon inter-agent nervous system.**  
Connect **Claude Code, Antigravity CLI, Opencode, Cursor, and DeepSeek** into a single synchronized hive-mind with shared memory, inter-agent messaging, and codebase-aware mutex locks.

[Key Features](#-key-features) • [Architecture](#-architecture) • [Quickstart](#-quickstart) • [Tools Reference](#-tools-reference) • [Examples](#-client-configurations)

---

</div>

## 🌌 The Problem: Isolated AI Islands

Modern developers frequently run different AI coding agents across multiple terminal sessions:
- **Claude Code** for complex refactoring and reasoning.
- **Antigravity CLI (Gemini 3 Flash)** for high-speed frontend and multimodal design.
- **Opencode / DeepSeek CLI** for test-driven validation, security audits, and backend engineering.

However, each agent operates as an **isolated island**:
- ❌ **Amnesia Across Terminals:** Agent B has no idea what Agent A just modified or discovered.
- ❌ **Merge Conflicts & Clobbering:** Two agents editing the same file concurrently corrupt code.
- ❌ **No Direct Task Delegation:** You have to manually copy-paste prompt outputs from one CLI to another.
- ❌ **Bloated Infrastructure:** Existing multi-agent frameworks require heavy Redis, Kafka, or Docker servers just to pass a simple message.

---

## ⚛️ The Solution: Entangled-MCP

**Entangled-MCP** bridges all your AI agent CLIs using the **Model Context Protocol (MCP)** and a high-performance **SQLite Write-Ahead Logging (WAL)** shared-state bus.

```
 ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
 │   Antigravity CLI    │   │     Opencode CLI     │   │     Claude Code      │
 │  (Frontend Builder)  │   │   (Backend / DBRE)   │   │  (Adversarial QA)    │
 └──────────┬───────────┘   └──────────┬───────────┘   └──────────┬───────────┘
            │                          │                          │
            │ (stdio / MCP JSON-RPC)   │ (stdio / MCP JSON-RPC)   │ (stdio / MCP)
            ▼                          ▼                          ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                              ENTANGLED-MCP                                 │
 │                       Universal Telepathic Gateway                         │
 └─────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      ┌───────────────────────────┐         ┌───────────────────────────┐
      │   Shared Knowledge Bus    │         │     Concurrency Mutex     │
      │   - Cross-CLI Findings    │         │  - File-Level Locks (TTL) │
      │   - Architecture Decisions│         │  - Task Collision Defense │
      │   - Real-Time Swarm State │         │  - Inbox/Outbox Messages  │
      └───────────────────────────┘         └───────────────────────────┘
                    ▲                                     ▲
                    └──────────────────┬──────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │ SQLite WAL Mode Engine      │
                        │ Sub-millisecond latency     │
                        │ Zero external daemon        │
                        └─────────────────────────────┘
```

---

## ✨ Key Features

### 1. 📬 Inter-Agent Direct Messaging (Agent Inbox/Outbox)
Agents can send direct, asynchronous messages or task requests to specific peers (or broadcast to all).
> *Antigravity finishes building an API client ➔ sends a message to Opencode requesting an automated test run.*

### 2. 🧠 The Shared Brain (Knowledge Bus)
When an agent diagnoses an elusive bug or settles an architectural decision, it broadcasts the finding to the collective knowledge bus. Other agents can query this knowledge immediately without human re-prompting.

### 3. 🔒 Codebase-Aware Concurrency (Resource Mutex Locks)
Avoid disastrous file clobbering! Agents acquire exclusive locks with automatic Time-To-Live (TTL) expiration before modifying sensitive source files. If Agent A holds a lock on `auth.py`, Agent B is warned and politely waits.

### 4. ⚡ 100% Native MCP (Zero Shell Hacks)
Unlike competing tools that inject brittle shell wrappers (`setup-claude-hooks.sh`), Entangled is **100% native MCP tools**. It works out of the box with any MCP client—Claude, Gemini, Cursor, Windsurf, or custom scripts.

### 5. 🪶 Zero-Daemon / Near-Zero Footprint
Powered by SQLite WAL mode. No Redis server. No Kafka broker. No cloud fees. Runs directly on your developer workstation with sub-millisecond local queries.

---

## 🚀 Quickstart

### Installation

```bash
git clone https://github.com/sinergiefek/entangled-mcp.git
cd entangled-mcp
pip install -e .
```

Or run directly without installation using `python -m entangled.cli`.

---

## 🔌 Client Configurations

Add Entangled-MCP to your favorite agent configuration files:

### 1. Claude Code CLI
Add to `~/.claude/mcp.json` or run:
```bash
claude mcp add entangled-mcp python -m entangled.cli
```

### 2. Opencode CLI
Add to `~/.config/opencode/opencode.json`:
```json
{
  "mcp": {
    "servers": {
      "entangled-mcp": {
        "type": "local",
        "command": ["python", "-m", "entangled.cli"]
      }
    }
  }
}
```

### 3. Antigravity CLI / Gemini CLI
Add to `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "entangled-mcp": {
      "command": "python",
      "args": ["-m", "entangled.cli"],
      "disabled": false
    }
  }
}
```

### 4. Cursor / Windsurf / Codex
Add to your project's `.cursor/mcp.json` or global MCP settings:
```json
{
  "mcpServers": {
    "entangled-mcp": {
      "command": "python",
      "args": ["-m", "entangled.cli"]
    }
  }
}
```

---

## 🛠️ Tools Reference

| Tool Name | Parameters | Description |
|---|---|---|
| `entangled_announce` | `agent_id, client_type, current_workspace, active_task` | Registers agent presence and updates heartbeat in the swarm. |
| `entangled_get_swarm` | *None* | Discovers all active agents, workspaces, and current assignments. |
| `entangled_broadcast_knowledge` | `topic, content, title, tags, author_agent, workspace` | Publishes a finding, architecture decision, or bug fix to the shared brain. |
| `entangled_query_knowledge` | `query, topic, tag, limit` | Searches the shared brain across past and current agent sessions. |
| `entangled_send_message` | `target_agent, action, message, payload_json, priority` | Dispatches an asynchronous message or task delegation to another agent. |
| `entangled_check_inbox` | `agent_id, unread_only, mark_as_read, limit` | Checks inbox for incoming instructions or notifications. |
| `entangled_acquire_lock` | `resource_path, agent_id, task_description, ttl_seconds` | Acquires an exclusive mutex lock on a file or module. |
| `entangled_release_lock` | `resource_path, agent_id` | Releases a previously acquired mutex lock. |
| `entangled_list_locks` | *None* | Lists all currently active and unexpired resource locks. |
| `entangled_get_activity_feed` | `limit` | Returns the unified chronological timeline of all swarm actions. |

---

## 🔄 Real-World Workflow Example (The Adversarial Review Loop)

1. **Terminal 1 (Antigravity CLI):**
   ```text
   > "Antigravity, announce yourself to the swarm and start refactoring the Login component."
   ```
   *Antigravity acquires lock on `Login.tsx`, writes modern responsive code, and releases the lock.*
   *Antigravity sends a message:* `"opencode: please audit git diff for security and type safety."*

2. **Terminal 2 (Opencode CLI / Claude Code):**
   ```text
   > "Check inbox and audit the latest work from Antigravity."
   ```
   *Opencode checks inbox, reads Antigravity's request, audits the changes, runs tests, and broadcasts the pass report to the shared brain!*

---

## 🧪 Testing

Run the automated test suite locally:

```bash
python tests/test_telepathy.py
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

<div align="center">

Crafted with 💖 by **[Sinergi Mitra Visitama](https://github.com/sinergiefek)**  
*Scale, License, and Automate.*

</div>
