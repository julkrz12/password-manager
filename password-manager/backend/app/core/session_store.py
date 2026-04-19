import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional
from .config import settings


@dataclass
class Session:
    user_id: int
    key: bytes
    expires_at: float


_sessions: Dict[str, Session] = {}


def create_session(user_id: int, key: bytes) -> str:
    token = uuid.uuid4().hex
    expires_at = time.time() + settings.session_ttl_minutes * 60
    _sessions[token] = Session(user_id=user_id, key=key, expires_at=expires_at)
    return token


def get_session(token: str) -> Optional[Session]:
    s = _sessions.get(token)
    if not s:
        return None
    if time.time() > s.expires_at:
        _sessions.pop(token, None)
        return None
    return s


def delete_session(token: str) -> None:
    _sessions.pop(token, None)
