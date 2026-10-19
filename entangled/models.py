"""
Pydantic Data Models for Entangled-MCP.
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class AgentNode(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier (e.g. 'antigravity-gemini', 'opencode-claude')")
    client_type: str = Field(..., description="CLI or Host environment (e.g. 'claude-code', 'antigravity-cli')")
    current_workspace: Optional[str] = Field(default="", description="Absolute path of the workspace the agent is operating on")
    active_task: Optional[str] = Field(default="Idle", description="Current task description")
    status: Literal["active", "idle", "busy", "offline"] = Field(default="active")
    last_seen: str = Field(..., description="ISO 8601 UTC timestamp of last heartbeat")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeNode(BaseModel):
    id: Optional[int] = None
    topic: str = Field(..., description="High-level category (e.g. 'architecture', 'database', 'bug-fix')")
    title: str = Field(..., description="Brief informative title")
    content: str = Field(..., description="Full markdown fact, decision record, or finding")
    tags: Optional[str] = Field(default="", description="Comma-separated tags")
    author_agent: str = Field(..., description="Agent who produced this knowledge")
    workspace: Optional[str] = Field(default="")
    created_at: str
    updated_at: str

class AgentMessage(BaseModel):
    id: Optional[int] = None
    trace_id: str
    sender_agent: str
    target_agent: str
    message_type: Literal["notification", "action_request", "review_request", "alert"] = "notification"
    action: str
    message: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    status: Literal["unread", "read", "acknowledged", "processed"] = "unread"
    created_at: str
    read_at: Optional[str] = None

class ResourceLock(BaseModel):
    resource_path: str = Field(..., description="File or task identifier being locked")
    locked_by_agent: str
    client_type: str
    task_description: str
    acquired_at: str
    expires_at: str
