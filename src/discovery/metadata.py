"""SVCB metadata parser and strict endpoint allow-list validation.

This parses standard SVCB priority, TargetName, ALPN and port fields. The owner
name convention and service-to-route mapping are explicitly PS-033 lab extensions.
"""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Any

import dns.name
from dns.rdtypes.svcbbase import ParamKey

from src.common.errors import EndpointPolicyError, MetadataError
from src.config.settings import SERVICE_PORTS

_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)


@dataclass(frozen=True)
class ServiceMetadata:
    service: str
    owner_name: str
    target_name: str
    port: int
    alpn: tuple[str, ...]
    ttl: int

    @property
    def endpoint_path(self) -> str:
        return f"/v1/diagnostics/{self.service}"

    @property
    def url(self) -> str:
        return f"https://{self.target_name}:{self.port}{self.endpoint_path}"


def validate_hostname(hostname: str, allowed_domain: str) -> str:
    host = hostname.rstrip(".").lower()
    if not host or len(host) > 253 or "_" in host:
        raise MetadataError("TargetName is not a valid service hostname")
    labels = host.split(".")
    if any(not _HOST_LABEL.fullmatch(label) for label in labels):
        raise MetadataError("TargetName contains an invalid DNS label")
    domain = allowed_domain.rstrip(".").lower()
    if host != domain and not host.endswith("." + domain):
        raise EndpointPolicyError("TargetName is outside the configured laboratory DNS zone")
    try:
        dns.name.from_text(host + ".", origin=dns.name.root)
    except Exception as exc:
        raise MetadataError("TargetName is not a valid DNS name") from exc
    return host


def parse_svcb_rdata(
    rdata: Any,
    *,
    service: str,
    owner_name: str,
    allowed_domain: str,
    allowed_ports: set[int] | frozenset[int] | None = None,
    ttl: int = 60,
) -> ServiceMetadata:
    if service not in SERVICE_PORTS:
        raise MetadataError(f"Unsupported diagnostic service: {service}")
    if getattr(rdata, "priority", None) in (None, 0):
        raise MetadataError("SVCB AliasMode is not supported by this lab client")
    try:
        target = validate_hostname(str(rdata.target), allowed_domain)
        params = rdata.params
        alpn_param = params.get(ParamKey.ALPN)
        port_param = params.get(ParamKey.PORT)
        if alpn_param is None or port_param is None:
            raise MetadataError("SVCB record must include ALPN and port parameters")
        alpns = tuple(value.decode("ascii") for value in alpn_param.ids)
        port = int(port_param.port)
    except MetadataError:
        raise
    except (AttributeError, ValueError, UnicodeError, TypeError) as exc:
        raise MetadataError("Malformed or unsupported SVCB parameters") from exc

    if not alpns or alpns != ("http/1.1",):
        raise MetadataError("Only the explicitly configured http/1.1 ALPN is supported")
    permitted_ports = set(allowed_ports or SERVICE_PORTS.values())
    if port not in permitted_ports:
        raise EndpointPolicyError("SVCB port is not in the configured allowed-port set")
    if port != SERVICE_PORTS[service]:
        # An endpoint update may change TargetName, but the lab does not allow an
        # unreviewed service-to-port swap between independent services.
        raise EndpointPolicyError("SVCB port does not match the requested service policy")
    return ServiceMetadata(
        service=service,
        owner_name=owner_name.rstrip(".").lower(),
        target_name=target,
        port=port,
        alpn=alpns,
        ttl=max(0, min(int(ttl), 86400)),
    )


def validate_target_ip(address: str, allowed_ips: tuple[str, ...]) -> str:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError as exc:
        raise EndpointPolicyError("DNS A/AAAA record returned an invalid IP address") from exc
    permitted = {ipaddress.ip_address(item) for item in allowed_ips}
    if parsed not in permitted:
        raise EndpointPolicyError(f"Resolved endpoint IP {parsed} is not in PS033_ALLOWED_IPS")
    return str(parsed)
