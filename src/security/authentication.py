"""Bearer token verification without storing or logging raw tokens."""
from __future__ import annotations

import hashlib
import hmac
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.settings import get_settings
from src.security.authorization import Principal, can_invoke

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="PS033Bearer")


def authenticate_token(token: str) -> Principal | None:
    """Return a principal when SHA-256(token) matches a configured token digest."""
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    for expected_digest, services in (get_settings().token_policies or {}).items():
        if hmac.compare_digest(digest, expected_digest):
            return Principal(subject=f"token:{expected_digest[:12]}", allowed_services=frozenset(services))
    return None


def get_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "authentication_required", "message": "A valid bearer token is required."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    principal = authenticate_token(credentials.credentials)
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "The bearer token is invalid."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return principal


def require_service_access(service: str):
    def dependency(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
        if not can_invoke(principal, service):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "forbidden", "message": f"Token is not authorized for {service}."},
            )
        return principal
    return dependency
