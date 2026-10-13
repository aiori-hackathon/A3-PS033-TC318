"""DNSSEC-aware DNS resolver using an explicitly trusted validating resolver."""
from __future__ import annotations

import ipaddress
import time
from dataclasses import dataclass

import dns.flags
import dns.message
import dns.name
import dns.query
import dns.rcode
import dns.rdatatype
import dns.exception

from src.common.errors import DNSSECValidationError, DiscoveryError, EndpointPolicyError
from src.config.settings import SERVICE_PORTS, get_settings
from src.discovery.metadata import ServiceMetadata, parse_svcb_rdata, validate_target_ip
from src.discovery.validator import ValidationStatus, classify_dns_response


@dataclass(frozen=True)
class DiscoveryResult:
    metadata: ServiceMetadata
    addresses: tuple[str, ...]
    dnssec_status: str
    ttl_remaining: int


class DNSServiceResolver:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, tuple[float, DiscoveryResult]] = {}

    def _query(self, name: str, rdtype: str):
        query = dns.message.make_query(name, rdtype, use_edns=0, want_dnssec=True)
        try:
            response = dns.query.udp(
                query,
                self.settings.dns_resolver,
                timeout=self.settings.dns_timeout,
                port=self.settings.dns_port,
            )
            if response.flags & dns.flags.TC:
                response = dns.query.tcp(
                    query,
                    self.settings.dns_resolver,
                    timeout=self.settings.dns_timeout,
                    port=self.settings.dns_port,
                )
        except (OSError, dns.exception.DNSException) as exc:
            raise DiscoveryError(f"DNS query to the configured resolver failed: {type(exc).__name__}") from exc

        validation = classify_dns_response(response)
        if self.settings.dns_require_ad and validation.status != ValidationStatus.SECURE:
            raise DNSSECValidationError(
                validation.status.value,
                f"DNSSEC policy rejected {name} {rdtype}: {validation.reason}",
            )
        return response, validation

    def discover(self, service: str, *, bypass_cache: bool = False) -> DiscoveryResult:
        if service not in SERVICE_PORTS:
            raise DiscoveryError(f"Unknown service '{service}'. Choose latency, connectivity, or routing.")
        now = time.monotonic()
        cached = self._cache.get(service)
        if not bypass_cache and cached and cached[0] > now:
            expiry, result = cached
            return DiscoveryResult(result.metadata, result.addresses, result.dnssec_status, max(0, int(expiry - now)))

        owner = self.settings.owner_name(service)
        response, validation = self._query(owner, "SVCB")
        if response.rcode() != dns.rcode.NOERROR:
            raise DiscoveryError(f"DNS lookup for {owner} failed with {dns.rcode.to_text(response.rcode())}")
        rrset = next((rrset for rrset in response.answer if rrset.rdtype == dns.rdatatype.SVCB), None)
        if rrset is None or not len(rrset):
            raise DiscoveryError(f"No SVCB service record found for {owner}")

        allowed_ports = set(SERVICE_PORTS.values())
        metadata = parse_svcb_rdata(
            rrset[0], service=service, owner_name=owner,
            allowed_domain=self.settings.domain,
            allowed_ports=allowed_ports,
            ttl=min(rrset.ttl, self.settings.cache_ttl_cap),
        )
        a_response, a_validation = self._query(metadata.target_name + ".", "A")
        if a_response.rcode() != dns.rcode.NOERROR:
            raise DiscoveryError(f"DNS address lookup for {metadata.target_name} failed")
        a_rrset = next((rrset for rrset in a_response.answer if rrset.rdtype == dns.rdatatype.A), None)
        if a_rrset is None:
            raise DiscoveryError(f"No A record found for SVCB target {metadata.target_name}")
        addresses: list[str] = []
        for rdata in a_rrset:
            address = validate_target_ip(rdata.address, self.settings.allowed_ips)
            if address not in addresses:
                addresses.append(address)
        if not addresses:
            raise EndpointPolicyError("SVCB target did not resolve to an approved address")
        ttl = min(metadata.ttl, int(a_rrset.ttl), self.settings.cache_ttl_cap)
        result = DiscoveryResult(metadata, tuple(addresses), validation.status.value, max(0, ttl))
        self._cache[service] = (time.monotonic() + ttl, result)
        return result
