# Deployment and Operations

## Local Python setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python scripts/bootstrap_lab.py
python scripts/generate_lab_certs.py
```

The generated bearer token is a lab credential. Keep `.env` private. The server stores token digests in policy configuration, not plaintext tokens.

## DNSSEC lab setup

Install BIND 9 and its utilities (`bind9`, `bind9-utils`) plus Unbound. Run `./scripts/prepare_dnssec.sh` from the project root. It generates local signing keys and a signed zone. Configure the validating resolver with the generated trust anchor as described in `config/dns/unbound.conf`; inspect its syntax against the installed Unbound version before starting it. The authoritative server must serve `ps033.test.signed`, and Unbound must validate that zone against the lab trust anchor. The client points at the validating resolver on `127.0.0.1:5353` by default. Never configure the authoritative server itself as the validating resolver.

The repository intentionally does not include generated signed zones, trust anchors, certificates, or private keys. They are created locally by scripts.

## Start API

```bash
uvicorn src.services.app:app --host 127.0.0.1 --port 8443 --ssl-certfile config/certs/server.crt --ssl-keyfile config/certs/server.key
```

For a single-process demonstration, the API can expose all three routes. In multi-container mode, set `SERVICE_KIND=latency|connectivity|routing` and use the matching port. Ensure the certificate SANs cover the service target names (or configure a matching local certificate) before invoking through DNS.

## CLI

```bash
python -m src.client.main list
python -m src.client.main discover latency
python -m src.client.main discover connectivity
python -m src.client.main discover routing
python -m src.client.main diagnose latency
python -m src.client.main diagnose connectivity --target lab-target.ps033.test
python -m src.client.main diagnose routing --target lab-target.ps033.test
```

## Tests and shutdown

```bash
python scripts/run_tests.sh
```

Stop local processes with Ctrl+C. Stop containers with `docker compose down`. Do not use the prototype against systems without explicit authorization.
