"""
Entangled Model Context Protocol (MCP) Server.
Exposes tools for Agent Telepathy, Shared Brain, Task Delegation, and Concurrency Locks.
"""

import sys
import json
from mcp.server.mcpserver import MCPServer
from .engine import EntangledEngine

def create_entangled_server(db_path: str = None) -> MCPServer:
    """Factory creating and configuring the Entangled MCPServer."""
    server = MCPServer("Entangled_MCP", dependencies=["mcp"])
    engine = EntangledEngine(db_path) if db_path else EntangledEngine()

    @server.tool()
    def entangled_announce(agent_id: str, client_type: str, current_workspace: str = "", active_task: str = "") -> str:
        """
        [ENTANGLED] Announces or heartbeats this agent CLI in the shared swarm.
        Example: entangled_announce(agent_id='antigravity-gemini', client_type='antigravity-cli', current_workspace='/path', active_task='Refactor')
        """
        engine.announce_or_heartbeat(
            agent_id=agent_id,
            client_type=client_type,
            current_workspace=current_workspace,
            active_task=active_task
        )
        return f"⚛️ [ENTANGLED SWARM] Agent '{agent_id}' ({client_type}) is now entangled. Workspace: {current_workspace or 'unspecified'}."

    @server.tool()
    def entangled_get_swarm() -> str:
        """
        [ENTANGLED] Discovers all active agent CLIs in the entangled swarm, their client type,
        current workspace, last heartbeat, and active task. Use this to see who else is working.
        """
        nodes = engine.get_swarm_nodes()
        if not nodes:
            return "⚛️ [ENTANGLED SWARM] No active agent nodes registered yet."

        output = f"⚛️ [ENTANGLED SWARM PRESENCE] Active Agent Nodes ({len(nodes)} total):\n\n"
        for n in nodes:
            output += f"- **{n['agent_id']}** ({n['client_type']})\n"
            output += f"  • Workspace: `{n['current_workspace'] or 'N/A'}`\n"
            output += f"  • Active Task: {n['active_task'] or 'Idle'}\n"
            output += f"  • Status: `{n['status']}` | Last Seen: {n['last_seen']}\n"
        return output

    @server.tool()
    def entangled_broadcast_knowledge(topic: str, content: str, title: str = "", tags: str = "", author_agent: str = "agent", workspace: str = "") -> str:
        """
        [ENTANGLED] Shares knowledge, findings, bug root-causes, or architecture decisions across ALL agent CLIs.
        Once broadcasted, Opencode, Antigravity, Claude Code, or DeepSeek can read and leverage it.
        """
        kid = engine.broadcast_knowledge(
            topic=topic,
            content=content,
            title=title or topic,
            tags=tags,
            author_agent=author_agent,
            workspace=workspace
        )
        return f"🧠 [SHARED BRAIN] Knowledge record #{kid} stored under topic '{topic}' by '{author_agent}'. Accessible by all entangled agents."

    @server.tool()
    def entangled_query_knowledge(query: str = "", topic: str = "", tag: str = "", limit: int = 10) -> str:
        """
        [ENTANGLED] Searches shared knowledge across all agent sessions by topic, tag, or keyword.
        Use this before tackling a task to check if another agent CLI has already investigated or solved it.
        """
        items = engine.query_knowledge(query=query, topic=topic, tag=tag, limit=limit)
        if not items:
            return f"🧠 [SHARED BRAIN] No shared knowledge found matching query='{query}', topic='{topic}', tag='{tag}'."

        output = f"🧠 [SHARED BRAIN] Found {len(items)} knowledge record(s):\n\n"
        for item in items:
            output += f"### #{item['id']} {item['title']} (Topic: {item['topic']})\n"
            output += f"- **Author:** `{item['author_agent']}` | Workspace: `{item['workspace']}` | Tags: `{item['tags']}` | Date: {item['created_at']}\n"
            output += f"- **Content:**\n{item['content']}\n\n---\n"
        return output

    @server.tool()
    def entangled_send_message(target_agent: str, action: str, message: str, payload_json: str = "{}", sender_agent: str = "agent", priority: str = "normal") -> str:
        """
        [ENTANGLED] Sends an asynchronous direct message or task delegation to another agent CLI (or 'all').
        Example: Antigravity sends an action_request to 'opencode' to run a backend test.
        """
        try:
            payload = json.loads(payload_json) if payload_json else {}
        except:
            payload = {"raw": payload_json}

        res = engine.send_message(
            target_agent=target_agent,
            action=action,
            message=message,
            payload=payload,
            sender_agent=sender_agent,
            priority=priority
        )
        return f"✉️ [INTER-AGENT TELEPATHY] Message #{res['message_id']} [Trace: {res['trace_id']}] dispatched to '{target_agent}' (Action: '{action}', Priority: '{priority}')."

    @server.tool()
    def entangled_check_inbox(agent_id: str, unread_only: bool = True, mark_as_read: bool = True, limit: int = 10) -> str:
        """
        [ENTANGLED] Checks the inbox for incoming messages or instructions sent to this agent CLI.
        Call this at the beginning of a session or task to see if another agent requested work.
        """
        messages = engine.check_inbox(agent_id=agent_id, unread_only=unread_only, mark_as_read=mark_as_read, limit=limit)
        if not messages:
            return f"📬 [INBOX for '{agent_id}'] No {'unread ' if unread_only else ''}messages."

        output = f"📬 [INBOX for '{agent_id}'] Found {len(messages)} message(s):\n\n"
        for m in messages:
            output += f"- **[#{m['id']}] From:** `{m['sender_agent']}` ➔ `{m['target_agent']}` | Priority: `{m['priority'].upper()}` | Action: `{m['action']}`\n"
            output += f"  • Created: {m['created_at']} | Status: `{m['status']}`\n"
            output += f"  • Message: {m['message']}\n"
            if m.get('payload_json') and m['payload_json'] != '{}':
                output += f"  • Payload: `{m['payload_json']}`\n"
            output += "\n"
        return output

    @server.tool()
    def entangled_acquire_lock(resource_path: str, agent_id: str, task_description: str, ttl_seconds: int = 1800) -> str:
        """
        [ENTANGLED] Acquires an exclusive mutex lock on a file, directory, or critical task.
        Prevents multiple agent CLIs from editing the same file concurrently and causing merge conflicts.
        Locks automatically expire after ttl_seconds (default 30 minutes).
        """
        res = engine.acquire_lock(
            resource_path=resource_path,
            agent_id=agent_id,
            task_description=task_description,
            ttl_seconds=ttl_seconds
        )
        if res["status"] in ("acquired", "renewed"):
            return f"🔒 [MUTEX LOCK ACQUIRED] '{resource_path}' is locked by '{agent_id}' for task: '{task_description}'. Expires at: {res['expires_at']}."
        else:
            return f"🚨 [MUTEX LOCK REJECTED] '{resource_path}' is ALREADY locked by '{res['locked_by']}' ({res['client_type']}) for task: '{res['task_description']}'. Expires at: {res['expires_at']}."

    @server.tool()
    def entangled_release_lock(resource_path: str, agent_id: str) -> str:
        """
        [ENTANGLED] Releases an exclusive lock once an agent CLI has finished modifying a resource.
        """
        res = engine.release_lock(resource_path=resource_path, agent_id=agent_id)
        if res["status"] == "released":
            return f"🔓 [MUTEX LOCK RELEASED] '{resource_path}' has been unlocked by '{agent_id}'."
        elif res["status"] == "not_locked":
            return f"ℹ️ [MUTEX] '{resource_path}' was not locked."
        else:
            return f"🚨 [MUTEX] Cannot release '{resource_path}'. Locked by '{res.get('locked_by')}'. Permission denied."

    @server.tool()
    def entangled_list_locks() -> str:
        """
        [ENTANGLED] Lists all currently active resource locks across the entire workspace.
        """
        locks = engine.list_locks()
        if not locks:
            return "🔓 [MUTEX LOCKS] All resources are currently unlocked and free."

        output = f"🔒 [ACTIVE MUTEX LOCKS] ({len(locks)} locked resources):\n\n"
        for l in locks:
            output += f"- **Resource:** `{l['resource_path']}`\n"
            output += f"  • Locked by: `{l['locked_by_agent']}` ({l['client_type']})\n"
            output += f"  • Task: {l['task_description']}\n"
            output += f"  • Acquired: {l['acquired_at']} | Expires: {l['expires_at']}\n"
        return output

    @server.tool()
    def entangled_get_activity_feed(limit: int = 15) -> str:
        """
        [ENTANGLED] Retrieves the unified chronological activity feed of what all agents in the swarm have done.
        """
        events = engine.get_activity_feed(limit=limit)
        if not events:
            return "📜 [SWARM ACTIVITY] No recent activity recorded."

        output = f"📜 [SWARM ACTIVITY FEED] (Latest {len(events)} events):\n\n"
        for e in events:
            output += f"- `[{e['created_at']}]` **{e['agent_id']}** ({e['action']}): {e['summary']}\n"
        return output

    # MCP Resources
    @server.resource("mcp://entangled/swarm-status")
    def get_resource_swarm_status() -> str:
        nodes = engine.get_swarm_nodes()
        locks = engine.list_locks()
        return json.dumps({"active_nodes": nodes, "active_locks": locks}, indent=2)

    @server.resource("mcp://entangled/activity-feed")
    def get_resource_activity_feed() -> str:
        events = engine.get_activity_feed(limit=30)
        return json.dumps(events, indent=2)

    return server
