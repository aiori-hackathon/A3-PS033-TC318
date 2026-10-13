"""Helpers shared by diagnostic API routers."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from src.config.settings import get_settings

logger = logging.getLogger("ps033.services")


def validate_lab_target(target: str | None) -> str:
    settings = get_settings()
    chosen = (target or settings.allowed_targets[0]).rstrip(".").lower()
    allowed = {item.rstrip(".").lower() for item in settings.allowed_targets}
    if chosen not in allowed:
        # Do not log arbitrary attacker-controlled target strings.
        logger.warning("Blocked disallowed diagnostic target")
        raise HTTPException(status_code=422, detail={"code": "target_not_allowed", "message": "Target is not on the configured lab allow-list."})
    return chosen


def timestamp() -> datetime:
    return datetime.now(timezone.utc)
