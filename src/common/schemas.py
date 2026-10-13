"""Pydantic schemas shared across diagnostic services."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID = Field(default_factory=uuid4)
    target: str | None = Field(default=None, min_length=1, max_length=253)


class DiagnosticResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: Literal["latency", "connectivity", "routing"]
    status: Literal["ok", "simulated"] = "simulated"
    request_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mode: Literal["simulated"] = "simulated"
    details: dict[str, Any]


class ErrorEnvelope(BaseModel):
    error: dict[str, Any]
