from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Envelope(BaseModel):
    version: str = "1.0"
    ok: bool
    type: str = Field("result", description="result|error")
    command: Optional[str] = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    data: Any = None
    meta: Dict[str, Any] = {}


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
