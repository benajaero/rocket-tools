"""Session memory for contextual engineering conversations."""

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ToolExecution:
    tool_name: str
    params: dict
    result: dict
    timestamp: float = field(default_factory=time.time)


@dataclass
class SessionMemory:
    session_id: str
    mission_type: str = "general"
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    parameters: dict[str, dict] = field(default_factory=dict)
    history: list[ToolExecution] = field(default_factory=list)

    def merge(self, new_params: dict, tool_name: str) -> dict:
        defaults = self.parameters.get(tool_name, {})
        merged = {**defaults, **{k: v for k, v in new_params.items() if v is not None}}
        self.parameters[tool_name] = merged
        self.last_accessed = time.time()
        return merged

    def record(self, tool_name: str, params: dict, result: dict):
        self.history.append(ToolExecution(tool_name, params, result))
        self.last_accessed = time.time()


class SessionStore:
    def __init__(self, ttl_seconds: float = 86400):
        self._sessions: dict[str, SessionMemory] = {}
        self._ttl = ttl_seconds

    def create(self, mission_type: str = "general") -> str:
        sid = str(uuid.uuid4())[:8]
        self._sessions[sid] = SessionMemory(session_id=sid, mission_type=mission_type)
        return sid

    def get(self, sid: str) -> SessionMemory:
        self._cleanup()
        if sid not in self._sessions:
            return SessionMemory(session_id=sid)
        return self._sessions[sid]

    def _cleanup(self):
        now = time.time()
        expired = [
            sid for sid, mem in self._sessions.items() if now - mem.last_accessed > self._ttl
        ]
        for sid in expired:
            del self._sessions[sid]


_store = SessionStore()


def get_store() -> SessionStore:
    return _store
