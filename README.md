# PS-033 — DNS-Based Discovery of Diagnostic Services

PS-033 is a controlled laboratory prototype for discovering diagnostic services through DNS SVCB records, requiring DNSSEC validation through a trusted validating resolver, validating endpoint metadata, and invoking simulated diagnostic APIs over HTTPS with bearer-token authentication and per-service authorization.

## Services
- `latency`: deterministic simulated latency result (not a measured RTT).
- `connectivity`: allow-listed deterministic result (sends no packets).
- `routing`: simulated route hops (does not run traceroute).

## Quick start
1. Python 3.10+; create and activate a virtual environment.
2. `pip install -r requirements.txt`
3. `cp .env.example .env`
4. `python scripts/bootstrap_lab.py`
5. `python scripts/generate_lab_certs.py`
6. Configure and start the signed BIND zone and trusted Unbound resolver; see `docs/deployment.md`.
7. Start API and use CLI commands documented in `docs/deployment.md`.
8. Run `./scripts/run_tests.sh`.

DNSSEC is not considered valid merely because a DNS query succeeds or RRSIG data exists. The CLI trusts the configured validating resolver and requires its AD signal by default. Never set validation to permissive mode to make a demonstration pass.

## Repository map
`src/` application; `tests/` automated checks; `scripts/` lab setup and test helpers; `config/` DNS templates; `docs/` design/deployment/protocol notes; `reports/` report and generated test evidence. Generated keys, certificates, `.env`, and signed-zone artifacts are not committed.

## Protocol status and template
DNS-AID is currently an Internet-Draft, not an RFC. This lab reuses SVCB/DNSSEC concepts and clearly labels the diagnostic naming and invocation flow as a project-specific extension. `Proposed-structure-hackathon.pdf` is preserved unchanged and its section ordering is reflected in the report. The supplied template itself is titled for a different project; adapt team/project metadata before submission.

See `src/README.md`, `docs/protocol-review.md`, `docs/architecture.md`, `docs/deployment.md`, and `docs/demo-script.md`.
