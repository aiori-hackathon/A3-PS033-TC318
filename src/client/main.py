"""Command-line interface for PS-033 discovery and invocation."""
from __future__ import annotations

import argparse
import json
import sys
import uuid

from src.common.errors import PS033Error
from src.config.settings import SERVICE_PORTS
from src.client.discovery_client import DiagnosticClient


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ps033", description="DNSSEC-protected discovery of lab diagnostic services")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List supported diagnostic service names")
    for action in ("discover", "diagnose"):
        command = sub.add_parser(action, help=f"{'Discover' if action == 'discover' else 'Discover and invoke'} a service")
        command.add_argument("service", choices=sorted(SERVICE_PORTS))
        command.add_argument("--no-cache", action="store_true", help="Bypass this process's discovery cache")
        if action == "diagnose":
            command.add_argument("--target", default=None, help="Optional allow-listed lab target (simulation only)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "list":
        print("Supported services:")
        for service in sorted(SERVICE_PORTS):
            print(f"  {service}")
        return 0
    client = DiagnosticClient()
    try:
        if args.command == "discover":
            result = client.discover(args.service, bypass_cache=args.no_cache)
            print(json.dumps({
                "service": args.service,
                "dnssec_status": result.dnssec_status,
                "owner_name": result.metadata.owner_name,
                "target_name": result.metadata.target_name,
                "addresses": result.addresses,
                "port": result.metadata.port,
                "alpn": result.metadata.alpn,
                "endpoint": result.metadata.url,
                "ttl_remaining_seconds": result.ttl_remaining,
            }, indent=2))
            return 0
        payload = {"request_id": str(uuid.uuid4())}
        if args.target:
            payload["target"] = args.target
        result = client.invoke(args.service, payload)
        print(json.dumps(result, indent=2, default=str))
        return 0
    except PS033Error as exc:
        print(json.dumps({"error": {"code": exc.code, "message": str(exc)}}), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
