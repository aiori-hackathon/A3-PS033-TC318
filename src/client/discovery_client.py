"""High-level PS-033 DNS discovery and protected invocation workflow."""
from __future__ import annotations

import os
from typing import Any

import httpx

from src.common.errors import ServiceUnavailable
from src.config.settings import SERVICE_ENDPOINT_PATHS, get_settings
from src.discovery.resolver import DNSServiceResolver, DiscoveryResult
from src.client.transport import DNSPinnedHTTPTransport


class DiagnosticClient:
    def __init__(self, resolver: DNSServiceResolver | None = None) -> None:
        self.settings = get_settings()
        self.resolver = resolver or DNSServiceResolver()

    def discover(self, service: str, *, bypass_cache: bool = False) -> DiscoveryResult:
        return self.resolver.discover(service, bypass_cache=bypass_cache)

    def invoke(self, service: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        token = os.getenv("PS033_BEARER_TOKEN", "").strip()
        if not token:
            raise ServiceUnavailable("PS033_BEARER_TOKEN is not configured. Run scripts/bootstrap_lab.py and load the generated .env.")
        result = self.discover(service)
        url = result.metadata.url
        transport = DNSPinnedHTTPTransport(
            ca_file=str(self.settings.ca_path()),
            address_map={result.metadata.target_name: result.addresses},
        )
        try:
            with httpx.Client(
                transport=transport,
                timeout=self.settings.http_timeout,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                response = client.post(
                    url,
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                    json=payload or {},
                )
                if 300 <= response.status_code < 400:
                    raise ServiceUnavailable("Service redirects are blocked by client policy")
                if response.status_code in (401, 403):
                    raise ServiceUnavailable(f"Service rejected authentication/authorization (HTTP {response.status_code})")
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise ServiceUnavailable("Service returned an unexpected response format")
                return data
        except ServiceUnavailable:
            raise
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError, httpx.RequestError, ValueError) as exc:
            raise ServiceUnavailable(f"Diagnostic service invocation failed: {type(exc).__name__}") from exc
        finally:
            transport.close()
