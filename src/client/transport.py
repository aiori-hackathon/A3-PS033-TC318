"""HTTPX transport that pins TCP resolution to DNSSEC-validated A records.

TLS still uses the SVCB TargetName as the origin/SNI and verifies its hostname
against the local CA. Only the TCP destination is pinned, preventing a second
untrusted OS-resolver lookup between discovery and invocation.
"""
from __future__ import annotations

import ipaddress
import socket
import ssl
from typing import Iterable

import httpcore
import httpx
from httpcore._backends.sync import SyncStream


class PinnedSyncBackend(httpcore.SyncBackend):
    def __init__(self, address_map: dict[str, tuple[str, ...]]) -> None:
        self.address_map = {host.rstrip(".").lower(): addresses for host, addresses in address_map.items()}

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        normalized = host.decode("ascii") if isinstance(host, bytes) else str(host)
        normalized = normalized.rstrip(".").lower()
        addresses = self.address_map.get(normalized)
        if not addresses:
            raise httpcore.ConnectError("Host has no DNSSEC-validated address pin")
        errors: list[OSError] = []
        for address in addresses:
            # Never dial an address other than the already-validated pin supplied
            # by DNSServiceResolver; validation against the policy occurs upstream.
            ipaddress.ip_address(address)
            try:
                sock = socket.create_connection((address, port), timeout=timeout, source_address=(local_address, 0) if local_address else None)
                if socket_options:
                    for option in socket_options:
                        sock.setsockopt(*option)
                return SyncStream(sock)
            except OSError as exc:
                errors.append(exc)
        raise httpcore.ConnectError(f"All validated endpoint addresses failed: {type(errors[-1]).__name__ if errors else 'unknown error'}")

    def connect_unix_socket(self, path, timeout=None, socket_options=None):
        raise httpcore.ConnectError("Unix sockets are not allowed for DNS-discovered endpoints")


class DNSPinnedHTTPTransport(httpx.HTTPTransport):
    """HTTPX transport with a constrained TCP backend and normal TLS checks."""

    def __init__(self, *, ca_file: str, address_map: dict[str, tuple[str, ...]]) -> None:
        context = ssl.create_default_context(cafile=ca_file)
        super().__init__(verify=context, trust_env=False, retries=0)
        # HTTPX exposes no public network_backend parameter. Replace only the
        # underlying httpcore pool to preserve URL hostname/SNI verification.
        self._pool.close()
        self._pool = httpcore.ConnectionPool(
            ssl_context=context,
            network_backend=PinnedSyncBackend(address_map),
            max_connections=10,
            max_keepalive_connections=2,
            keepalive_expiry=5.0,
            retries=0,
        )
