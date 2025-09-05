"""only used when debug mode"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RequestSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    method: Optional[str] = Field(None)
    url: str = Field(...)
    headers: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(...)
    body: Dict[str, Any] = Field(default_factory=dict)


class ResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    status_code: Optional[int] = Field(None)
    headers: Dict[str, Any] = Field(default_factory=dict)
    body: Dict[str, Any] = Field(default_factory=dict)


class EventSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    user_id: str = Field(...)
    endpoint: str = Field(...)
    latency_ms: int = Field(default=0)
    request: RequestSchema = Field(...)
    response: ResponseSchema = Field(...)


class EventsSchema(BaseModel):
    events: List[EventSchema]


REQUIRED_KEYS_EVENT = {"user_id", "session_id", "endpoint", "request", "response"}
REQUIRED_KEYS_REQUEST = {"url", "timestamp", "headers", "body"}
REQUIRED_KEYS_RESPONSE = {"headers", "body"}
