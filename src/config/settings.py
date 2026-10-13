"""Environment-backed settings for PS-033.

Secrets are not hard-coded. API token policies map SHA-256 token digests to
service capabilities, never raw bearer tokens.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

SERVICE_PORTS = {"latency": 8443, "connectivity": 8444, "routing": 8445}
SERVICE_ENDPOINT_PATHS = {
    "latency": "/v1/diagnostics/latency",
    "connectivity": "/v1/diagnostics/connectivity",
    "routing": "/v1/diagnostics/routing",
}


def _csv(name: str, default: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in os.getenv(name, default).split(",") if x.strip())


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def token_policies() -> dict[str, tuple[str, ...]]:
    raw = os.getenv("PS033_TOKEN_POLICIES_JSON", "{}")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("PS033_TOKEN_POLICIES_JSON must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("PS033_TOKEN_POLICIES_JSON must be an object")
    policies: dict[str, tuple[str, ...]] = {}
    for digest, services in value.items():
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ValueError("Token policy keys must be 64-character SHA-256 hex digests")
        if not isinstance(services, list) or not all(isinstance(s, str) for s in services):
            raise ValueError("Each token policy must contain a list of service names")
        unknown = set(services) - set(SERVICE_PORTS)
        if unknown:
            raise ValueError(f"Unknown services in token policy: {sorted(unknown)}")
        policies[digest.lower()] = tuple(sorted(set(services)))
    return policies


@dataclass(frozen=True)
class Settings:
    domain: str = os.getenv("PS033_DOMAIN", "ps033.test").strip(".").lower()
    dns_resolver: str = os.getenv("PS033_DNS_RESOLVER", "127.0.0.1")
    dns_port: int = int(os.getenv("PS033_DNS_PORT", "5353"))
    dns_timeout: float = float(os.getenv("PS033_DNS_TIMEOUT", "2.0"))
    dns_require_ad: bool = _bool("PS033_DNS_REQUIRE_AD", True)
    tls_ca: str = os.getenv("PS033_TLS_CA", "config/certs/ca.crt")
    allowed_ips: tuple[str, ...] = _csv("PS033_ALLOWED_IPS", "127.0.0.1,::1")
    allowed_targets: tuple[str, ...] = _csv("PS033_ALLOWED_TARGETS", "lab-target.ps033.test")
    http_timeout: float = float(os.getenv("PS033_HTTP_TIMEOUT", "5.0"))
    cache_ttl_cap: int = int(os.getenv("PS033_CACHE_TTL_CAP", "60"))
    log_level: str = os.getenv("PS033_LOG_LEVEL", "INFO").upper()
    token_policies: dict[str, tuple[str, ...]] | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.dns_port <= 65535:
            raise ValueError("PS033_DNS_PORT must be in 1..65535")
        if self.dns_timeout <= 0 or self.http_timeout <= 0:
            raise ValueError("Timeout settings must be positive")
        object.__setattr__(self, "token_policies", token_policies())

    def owner_name(self, service: str) -> str:
        if service not in SERVICE_PORTS:
            raise ValueError(f"Unknown service: {service}")
        return f"{service}.{self.domain}."

    def ca_path(self) -> Path:
        path = Path(self.tls_ca)
        return path if path.is_absolute() else PROJECT_ROOT / path


def get_settings() -> Settings:
    """Build fresh settings so tests and process environment changes are visible."""
    return Settings()
