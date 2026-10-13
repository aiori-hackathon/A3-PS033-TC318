#!/usr/bin/env python3
"""Create ignored local credentials and certificate files for a single-machine lab."""
from __future__ import annotations
import argparse
import hashlib
import json
import secrets
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.generate_lab_certs import main as generate_certs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Rotate the API token and local CA/certificates")
    args = parser.parse_args()
    env_path = ROOT / ".env"
    if env_path.exists() and not args.force:
        print(".env already exists; it was left unchanged. Pass --force to rotate the lab credentials.")
        return 0
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    policies = {digest: ["latency", "connectivity", "routing"]}
    env_path.write_text(
        "# Local lab secrets; this file is ignored by git.\n"
        "PS033_DOMAIN=ps033.test\nPS033_DNS_RESOLVER=127.0.0.1\nPS033_DNS_PORT=5353\n"
        "PS033_DNS_TIMEOUT=2.0\nPS033_DNS_REQUIRE_AD=true\n"
        "PS033_TLS_CA=config/certs/ca.crt\n"
        f"PS033_TOKEN_POLICIES_JSON='{json.dumps(policies, separators=(',', ':'))}'\n"
        "PS033_ALLOWED_IPS=127.0.0.1,::1\nPS033_ALLOWED_TARGETS=lab-target.ps033.test\n"
        "PS033_LOG_LEVEL=INFO\nPS033_HTTP_TIMEOUT=5.0\nPS033_CACHE_TTL_CAP=60\n"
        f"PS033_BEARER_TOKEN={token}\n",
        encoding="utf-8",
    )
    env_path.chmod(0o600)
    cert_args = ["--force"] if args.force else []
    # Reuse the checked-in generator without importing certificate internals here.
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_lab_certs.py"), *cert_args], check=True)
    print("\nCreated .env with a random bearer token and SHA-256-only server policy.")
    print("The bearer token is stored only in ignored .env; do not commit or share it.")
    print("Next: scripts/prepare_dnssec.sh, then docker compose up --build -d")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
