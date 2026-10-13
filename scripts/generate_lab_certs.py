#!/usr/bin/env python3
"""Generate a private local CA and HTTPS certificate for the PS-033 lab only."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "config" / "certs"
HOSTS = [
    "latency-api.ps033.test", "connectivity-api.ps033.test", "routing-api.ps033.test",
    "latency.ps033.test", "connectivity.ps033.test", "routing.ps033.test", "localhost",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace existing lab certificate files")
    args = parser.parse_args()
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    ca_key_path, ca_cert_path = CERT_DIR / "ca.key", CERT_DIR / "ca.crt"
    server_key_path, server_cert_path = CERT_DIR / "server.key", CERT_DIR / "server.crt"
    paths = [ca_key_path, ca_cert_path, server_key_path, server_cert_path]
    if all(p.exists() for p in paths) and not args.force:
        print("Lab CA and server certificate already exist; pass --force to rotate them.")
        return 0

    now = datetime.now(timezone.utc)
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "PS-033 Local Development CA")])
    ca_cert = (
        x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
        .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=False, key_cert_sign=True, crl_sign=True,
            encipher_only=False, decipher_only=False), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    server_key = ec.generate_private_key(ec.SECP256R1())
    server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "latency-api.ps033.test")])
    san = [x509.DNSName(host) for host in HOSTS]
    san.extend([x509.IPAddress(__import__("ipaddress").ip_address("127.0.0.1")), x509.IPAddress(__import__("ipaddress").ip_address("::1"))])
    server_cert = (
        x509.CertificateBuilder().subject_name(server_name).issuer_name(ca_cert.subject)
        .public_key(server_key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=397))
        .add_extension(x509.SubjectAlternativeName(san), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
            data_encipherment=False, key_agreement=True, key_cert_sign=False, crl_sign=False,
            encipher_only=False, decipher_only=False), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    ca_key_path.write_bytes(ca_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    ca_cert_path.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    server_key_path.write_bytes(server_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    server_cert_path.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    os.chmod(ca_key_path, 0o600); os.chmod(server_key_path, 0o600)
    print(f"Created lab-only CA and TLS certificate under {CERT_DIR}.")
    print("Trust config/certs/ca.crt on the PS-033 client; do not use these certificates outside the lab.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
