# PS-033 source package

All Python application code lives here:

- `client/`: CLI and secure invocation transport.
- `discovery/`: DNS resolver, SVCB metadata parser, and DNSSEC validation-state handling.
- `dns/`: notes for the BIND/Unbound deployment; zone templates live in root `config/dns/`.
- `security/`: bearer-token authentication and per-service authorization.
- `services/`: FastAPI routes for simulated latency, connectivity, and routing diagnostics.
- `common/`: Pydantic schemas and typed application errors.
- `config/`: environment-backed configuration.

Run commands from the project root. DNS discovery requires a trusted validating resolver configured for the lab trust anchor; the client requires the AD bit by default. A DNS query succeeding, or an RRSIG being present, is not by itself proof of validation.

The DNS-AID Internet-Draft describes AI-agent discovery and does not define this diagnostic API workflow. PS-033 reuses SVCB/DNSSEC concepts and explicitly labels its service names and invocation process as a lab extension. See `docs/protocol-review.md`.

See `docs/deployment.md` for install, DNSSEC setup, certificate setup, startup, CLI, test, and shutdown commands.
