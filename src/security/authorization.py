"""Server-side authorization policy for diagnostic operations."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    subject: str
    allowed_services: frozenset[str]


def can_invoke(principal: Principal, service: str) -> bool:
    return service in principal.allowed_services
