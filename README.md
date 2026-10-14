# TrustDiag — DNS-Based Discovery of Diagnostic Services

**Hackathon Project:** PS-033  
**Team Code:** A3-PS033-TC318  
**Team Name:** Team rocks  
**Students:** Sudhakar A; Thanush Priyan R  
**Project Guide:** Dr. E. Bijolin Edwin, M.E., Ph.D.

> **Project status:** TrustDiag is a research and prototype project. This README describes the intended solution and a recommended development workflow. Treat a feature as implemented only when its code, configuration, and corresponding tests are present in this repository and have been run successfully. Example endpoints and request payloads below are proposed interface examples, not a guarantee that the current code already exposes them.

## Table of Contents

- [1. Overview](#1-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Proposed Solution](#3-proposed-solution)
- [4. Project Objectives](#4-project-objectives)
- [5. Scope](#5-scope)
- [6. Key Features](#6-key-features)
- [7. Security Model](#7-security-model)
- [8. Diagnostic Services](#8-diagnostic-services)
- [9. Intended Components and Technologies](#9-intended-components-and-technologies)
- [10. Repository Structure](#10-repository-structure)
- [11. Requirements](#11-requirements)
- [12. Development Setup](#12-development-setup)
- [13. Configuration](#13-configuration)
- [14. DNS Discovery and DNSSEC Validation](#14-dns-discovery-and-dnssec-validation)
- [15. Service Invocation Examples](#15-service-invocation-examples)
- [16. Testing and Evaluation](#16-testing-and-evaluation)
- [17. Expected Results and Metrics](#17-expected-results-and-metrics)
- [18. Error Handling and Audit Logging](#18-error-handling-and-audit-logging)
- [19. Safety, Privacy, and Limitations](#19-safety-privacy-and-limitations)
- [20. Development Roadmap](#20-development-roadmap)
- [21. Troubleshooting](#21-troubleshooting)
- [22. References](#22-references)
- [23. Team](#23-team)

## 1. Overview

TrustDiag is a trust-aware service-discovery and invocation prototype for network diagnostic services. It aims to let a client discover diagnostic endpoints through DNS, validate the DNS information and service metadata, connect to the selected endpoint over HTTPS, authenticate the client, and invoke only the diagnostic operations that the server authorizes.

The prototype focuses on three diagnostic capabilities:

1. **Latency diagnosis** — measure the response time to an approved diagnostic endpoint.
2. **Connectivity diagnosis** — check the reachability of a permitted destination or service.
3. **Routing diagnosis** — collect routing or path information where the environment supports it; use explicitly labelled simulation only when real diagnostics cannot be performed.

TrustDiag combines independent security controls. DNSSEC validates signed DNS data. Metadata validation checks the service information. HTTPS/TLS validates the connected server and protects communication. Authentication identifies the client, while authorization decides which operations the client may perform.

## 2. Problem Statement

Diagnostic applications often depend on service addresses configured manually in code or configuration files. When service locations change, clients can use outdated endpoints or require manual updates. Discovering a service through DNS alone also does not automatically establish that every returned endpoint is safe to use or that a requesting client is allowed to invoke it.

The project addresses these issues:

- Static endpoint configuration can become stale when a service moves or is replaced.
- DNS information must be validated according to the trust policy before it is relied on.
- A valid DNSSEC response does not independently authenticate the HTTPS API server.
- Service metadata may be malformed, inconsistent, unsupported, or unsuitable for the requested operation.
- A discovered service must not automatically be accessible to every client.
- Diagnostic operations can be misused if targets and request parameters are not restricted.
- Failures need clear results and audit records to support troubleshooting and security evaluation.

## 3. Proposed Solution

TrustDiag proposes a client–server workflow with the following stages:

1. The client receives a request to use a named diagnostic capability.
2. The discovery component queries DNS for the service information using the record format selected for the project requirements.
3. DNSSEC status is checked using a correctly configured validating resolver or an equivalent validation implementation and trust configuration.
4. The client validates the returned service metadata, service identity, endpoint format, permitted protocol, and any integrity digest required by the selected specification.
5. The client selects an eligible endpoint and creates an HTTPS connection.
6. TLS certificate and hostname verification confirm the connected server's identity according to the configured trust policy.
7. The client submits the diagnostic request with its credential.
8. The server authenticates the client and separately checks whether the requested operation and target are authorized.
9. The diagnostic service runs the permitted check and returns a structured result.
10. The system records relevant discovery, validation, authorization, and diagnostic events without logging secrets.

For protected operations, mandatory validation failures must stop the request. An unavailable or indeterminate DNSSEC result must not silently be treated as valid when policy requires successful DNSSEC validation.

## 4. Project Objectives

- Discover diagnostic service endpoints using DNS rather than relying only on hardcoded addresses.
- Apply DNSSEC validation according to the configured lab trust model.
- Validate the structure and consistency of service metadata.
- Verify server identity through HTTPS/TLS.
- Authenticate clients and enforce server-side authorization.
- Provide latency, connectivity, and routing diagnostic capabilities within an approved lab scope.
- Reject untrusted discovery data and unauthorized diagnostic requests.
- Produce structured responses and security audit records.
- Evaluate the design with repeatable functional, integration, and security tests.

## 5. Scope

### Included

- A controlled lab DNS zone and DNSSEC validation configuration.
- DNS-based discovery of the three planned diagnostic services.
- A Python discovery client.
- Diagnostic API services, preferably implemented with FastAPI for the prototype.
- HTTPS/TLS verification.
- Bearer-token authentication for the initial lab implementation.
- Server-side authorization and target allowlisting.
- Structured results, safe errors, and audit logging.
- Automated tests and a report of measured results.

### Not included in the initial prototype

- Unrestricted scanning of public networks or third-party systems.
- Production-grade identity management or enterprise single sign-on.
- A claim that DNSSEC alone secures an API or authorizes a caller.
- Automatic DNS updates without an explicitly configured update mechanism.
- Claims of universal protection against all network attacks.
- Blockchain, AI, or other additional systems that are not necessary to validate the core research question.

## 6. Key Features

| Feature | Intended behaviour |
|---|---|
| DNS-based discovery | Resolve a logical service name to supported service information. |
| DNSSEC trust check | Distinguish valid, bogus, insecure, and indeterminate outcomes as supported by the validating resolver and policy. |
| Metadata validation | Reject missing, malformed, inconsistent, or unsupported fields. |
| Endpoint validation | Enforce approved hostnames, ports, protocols, and endpoint rules. |
| HTTPS/TLS verification | Validate the certificate chain and hostname; do not disable verification to bypass errors. |
| Client authentication | Require a configured credential for protected requests. |
| Authorization | Decide permissions on the server for each requested action. |
| Target allowlist | Restrict diagnostics to explicitly approved targets. |
| Structured responses | Return machine-readable statuses and relevant timing/error details. |
| Audit logging | Record security decisions and operation outcomes without secrets. |
| Automated testing | Exercise success paths and expected security failures. |

## 7. Security Model

TrustDiag treats service discovery, server identity, client identity, and operation permission as separate checks.

| Control | What it establishes | What it does not establish by itself |
|---|---|---|
| DNSSEC validation | The authenticity and integrity of signed DNS data relative to a configured trust chain. | That the API implementation is safe, that the connected server is the intended TLS identity, or that a client has permission. |
| Metadata validation | That discovery information conforms to the application's expected schema and policy. | That the source is trusted unless the relevant trust checks also pass. |
| HTTPS/TLS | Protection of transport and verification of the server identity against certificate and hostname rules. | Permission for a user to invoke a diagnostic operation. |
| Authentication | The identity associated with the presented client credential. | Permission to execute every operation. |
| Authorization | Whether that authenticated client may perform the specific operation on the requested target. | The correctness of a diagnostic result or the integrity of DNS records. |
| Audit logging | Evidence of selected events and decisions for review. | Prevention of every attack or proof that an event not logged never occurred. |

### Fail-closed rule

If a mandatory security check fails, the protected invocation must be rejected. Examples include bogus DNSSEC data, a forbidden endpoint, a TLS hostname mismatch, an invalid token, a denied operation, or an unapproved target. An implementation must not continue merely to make a demo appear successful.

### Credential handling

- Keep bearer tokens and private keys out of source code and version control.
- Store local secrets in an untracked environment file or an approved secret manager.
- Do not place authentication secrets in DNS records or public service metadata.
- Never log authorization headers, tokens, private keys, or complete secret configuration values.
- Use separate lab-only certificates and credentials; do not reuse them for production services.

## 8. Diagnostic Services

### 8.1 Latency diagnosis

The latency service measures response time to an approved endpoint using the method configured for the lab. Results should identify the service and target, provide a measurement and timestamp, and describe success or failure. Measurement units and method should be stated in the result or accompanying documentation.

### 8.2 Connectivity diagnosis

The connectivity service checks whether an approved destination or service is reachable. The response should distinguish at least `reachable`, `unreachable`, and `error`. Timeouts, DNS errors, policy denials, and other failures should not be represented as successful connectivity.

### 8.3 Routing diagnosis

The routing service collects routing or path information only where the host environment and permissions allow it. Some routers do not respond to traceroute probes, so a partial path is not necessarily evidence of a broken route. If the prototype uses a simulated path, the response and the UI must label it as simulated.

### Proposed response shape

The exact response schema must be finalized alongside the implementation. A recommended common shape is:

```json
{
  "service": "latency",
  "status": "success",
  "target": "lab-target-01",
  "result": {
    "response_time_ms": 24.0
  },
  "simulated": false,
  "timestamp": "<ISO-8601 timestamp>"
}
```

The example value is illustrative and is not a measured result from this project. Error responses should include a stable error code and a safe explanatory message without leaking tokens, secrets, stack traces, or internal infrastructure details.

## 9. Intended Components and Technologies

| Component | Intended technology | Responsibility |
|---|---|---|
| Authoritative DNS | BIND 9 | Hosts the controlled lab zone and signed DNS data. |
| DNSSEC validation | Unbound or another correctly configured validating resolver; alternatively a validated client approach where appropriate | Supplies meaningful validation status and trust-anchor configuration. |
| Discovery client | Python 3.10+ and `dnspython` | Queries DNS and processes discovery information. |
| Diagnostic APIs | FastAPI and Uvicorn | Exposes the planned diagnostic operations. |
| HTTPS/TLS | TLS certificates trusted by the lab client | Verifies endpoint identity and protects traffic. |
| Authentication | Bearer token for the initial lab | Identifies clients presenting configured credentials. |
| Authorization | Server-side policy checks | Limits operations and targets per client. |
| Tests | `pytest` and `httpx` where suitable | Automates unit and integration checks. |
| Configuration | Environment variables and non-secret configuration files | Separates local configuration from source code. |

Technology choices may be adjusted to match the exact hackathon requirements and the DNS-AID or other discovery specification revision selected by the team. The final implementation must document that revision and the exact fields or record types it supports.

## 10. Repository Structure

The structure below is a recommended organization. Keep the README synchronized with the actual repository as modules are implemented.

```text
.
├── README.md
├── Proposed-structure-hackathon.pdf
├── .gitignore
├── .env.example
├── requirements.txt
├── config/
│   ├── dns/
│   └── certs/                 # Lab certificates; private keys must not be committed
├── scripts/
│   └── bootstrap_lab.py       # Optional helper if present in this repository
├── src/
│   ├── README.md
│   ├── client/                # CLI or client entry point
│   ├── discovery/             # DNS lookup, metadata parsing and validation
│   ├── dns/                   # DNS test-zone or resolver-related files
│   ├── services/              # Latency, connectivity and routing APIs
│   ├── security/              # TLS configuration, authentication and authorization
│   └── common/                # Shared schemas, errors and utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
└── docs/
    ├── test-plan.md
    └── evaluation.md
```

Do not create empty folders solely to match this illustration if the repository uses a different layout. The actual entry points, configuration files, and test commands should be documented here once they exist.

## 11. Requirements

### Software

- Python 3.10 or newer is recommended for the Python components.
- BIND 9 or another suitable authoritative DNS implementation for the lab zone.
- A DNSSEC-validating resolver with an explicitly configured trust model for the private lab zone.
- Python packages selected by the code, such as `dnspython`, `fastapi`, `uvicorn`, `httpx`, and `pytest`.
- Git for version control.
- OpenSSL or an equivalent certificate tool if the team manages lab TLS certificates manually.

### Lab and networking

- A host or virtual machines on a controlled network where the client can reach the DNS resolver and diagnostic service endpoints.
- A local DNS zone and addresses reserved for the lab.
- A lab certificate chain trusted by the client, with certificate subject alternative names matching the test hostnames.
- Permission to run any operating-system diagnostic commands used by the routing or connectivity service.

Exact package versions should be pinned in the project's dependency file after compatibility testing. Do not claim compatibility with an untested version combination.

## 12. Development Setup

These are development instructions for the intended stack. The exact commands may need adjustment if the repository's entry points or dependency files differ.

### 12.1 Clone or open the repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd <REPOSITORY-DIRECTORY>
```

If the repository is already on the machine, open its root directory instead of cloning it again.

### 12.2 Create a Python virtual environment

Linux, Kali Linux, macOS, or WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install dependencies from the repository when a pinned dependency file is present:

```bash
python -m pip install -r requirements.txt
```

If the repository has not created `requirements.txt` yet, install only the packages required by the implemented modules and then record tested versions in that file. A starting set for the intended Python components may be:

```bash
python -m pip install dnspython fastapi "uvicorn[standard]" httpx pytest
```

### 12.3 Prepare lab secrets and certificates

If the repository includes `scripts/bootstrap_lab.py`, review the script and run it from the repository root:

```bash
python scripts/bootstrap_lab.py
```

Use `--force` only when you intentionally want the script to regenerate existing lab artifacts and understand which files will be overwritten:

```bash
python scripts/bootstrap_lab.py --force
```

The helper may create lab-only certificates and a local `.env` file, depending on its current implementation. Inspect its output rather than assuming every generated file or value. Trust the lab CA only on the intended lab clients. Never reuse lab certificates outside the controlled environment.

### 12.4 Configure DNS

Configure the authoritative DNS zone and DNSSEC signing for the names used by the project. Configure a validating resolver with the correct trust anchor for the private zone. Merely signing a zone does not guarantee that a client has validated the response. Use the DNS names, record types, and metadata fields selected by the project specification.

### 12.5 Start the services and client

The exact start commands must match the actual Python module names and DNS configuration in the repository. A FastAPI service is commonly launched with Uvicorn, but replace the example module path with the real application entry point:

```bash
uvicorn <python_module>:app --host 127.0.0.1 --port 8000
```

Do not expose the API to an untrusted network until access controls, TLS, target restrictions, and firewall rules have been checked. Document the verified startup command and expected output when the implementation is finalized.

## 13. Configuration

Configuration should be provided through environment variables or non-secret configuration files. The names below are recommendations; align them with the actual code.

| Setting | Purpose | Example or guidance |
|---|---|---|
| `TRUSTDIAG_DNS_RESOLVER` | Resolver used by the discovery client | Address of the configured lab resolver. |
| `TRUSTDIAG_DNS_ZONE` | Lab discovery zone | A reserved internal/test zone controlled by the team. |
| `TRUSTDIAG_REQUIRE_DNSSEC` | Whether protected discovery requires successful validation | Enable for the security evaluation. |
| `TRUSTDIAG_CA_CERT` | Path to the CA certificate trusted by the lab client | Path to a public certificate file, not a private key. |
| `TRUSTDIAG_BEARER_TOKEN` | Local lab credential, if used by the implementation | Store in `.env` or another secret store; never commit it. |
| `TRUSTDIAG_ALLOWED_TARGETS` | Approved diagnostic targets | Use a restricted, explicit list. |
| `TRUSTDIAG_LOG_LEVEL` | Logging verbosity | Use a suitable level for the environment. |

These variables are a configuration design suggestion, not a statement that every variable is already implemented. The final code should validate missing or invalid configuration on startup and should not quietly weaken security settings.

### Environment file handling

Use `.env.example` to document variable names with blank or harmless sample values. Keep `.env`, private keys, tokens, and machine-specific secrets out of Git. Review `.gitignore` before committing, including previously tracked secret files.

## 14. DNS Discovery and DNSSEC Validation

### Discovery rules

- Use the exact service name and record format defined by the project's chosen specification or requirements.
- Validate the service metadata against a documented schema.
- Reject endpoints outside the configured host, scheme, port, or target policy.
- Do not execute arbitrary commands or diagnostic operations based solely on metadata obtained from DNS.
- Do not put credentials or private information in DNS records.
- Respect DNS TTLs and caching semantics when testing endpoint updates.

### DNSSEC rules

- Use a validating resolver or a properly implemented validation process with a known trust anchor.
- Distinguish successful validation from bogus, insecure, and indeterminate outcomes according to resolver behaviour and project policy.
- When DNSSEC is mandatory, stop protected invocation if validation fails or cannot be established.
- Include tests for invalid signatures or an otherwise invalid chain of trust in the controlled lab.
- Document how the lab trust anchor is installed and how the client determines the validation status.

### Specification compatibility

The project should pin the exact revision of any DNS-AID Internet-Draft or other discovery proposal it implements. Internet-Drafts can change and are not automatically Internet Standards. The README and report should identify the revision tested, the record types and fields actually supported, and any deliberate deviations. Do not describe an illustrative metadata format as standards-compliant without checking it against that revision.

## 15. Service Invocation Examples

The following examples illustrate the intended request pattern. Endpoint paths and payloads are **proposed examples only** until they match the implemented API.

### Example: health check

```bash
curl --cacert config/certs/ca.crt https://localhost:8000/health
```

Use a hostname present in the certificate's subject alternative names. Do not use `curl -k` or disable TLS verification to work around a certificate error in the security evaluation.

### Example: request latency diagnosis

```bash
curl --cacert config/certs/ca.crt \
  -H "Authorization: Bearer ${TRUSTDIAG_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -X POST https://localhost:8000/v1/diagnostics/latency \
  -d '{"target_id":"lab-target-01"}'
```

The `target_id` should refer to an approved target configured in the lab; it must not be a free-form URL that allows the caller to make the server connect to arbitrary destinations.

### Example: request connectivity diagnosis

```bash
curl --cacert config/certs/ca.crt \
  -H "Authorization: Bearer ${TRUSTDIAG_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -X POST https://localhost:8000/v1/diagnostics/connectivity \
  -d '{"target_id":"lab-target-01"}'
```

### Example: request routing diagnosis

```bash
curl --cacert config/certs/ca.crt \
  -H "Authorization: Bearer ${TRUSTDIAG_BEARER_TOKEN}" \
  -H "Content-Type: application/json" \
  -X POST https://localhost:8000/v1/diagnostics/routing \
  -d '{"target_id":"lab-target-01"}'
```

Replace these examples with the final paths and request schema when the API is implemented. Never publish a real token in documentation, terminal screenshots, source code, or issue reports.

## 16. Testing and Evaluation

The tests should verify both successful operation and deliberate rejection of invalid or unauthorized requests. Run tests only against lab systems or destinations for which the team has explicit permission.

| Test ID | Scenario | Expected outcome |
|---|---|---|
| T01 | Valid signed DNS discovery | Expected metadata is returned and accepted by the configured policy. |
| T02 | DNSSEC-bogus response | Protected invocation is rejected. |
| T03 | Validation is indeterminate or unavailable | Protected invocation is rejected when successful validation is mandatory. |
| T04 | Missing or malformed metadata | Discovery result is rejected with a useful error. |
| T05 | Required metadata digest does not match | Discovery result is rejected. |
| T06 | Endpoint violates allowlist or scheme/port policy | Endpoint is not invoked. |
| T07 | TLS certificate or hostname is invalid | Client refuses the protected connection. |
| T08 | Credential is missing or invalid | API denies the request. |
| T09 | Valid client requests an unauthorized operation | API denies the operation. |
| T10 | Request names an unapproved target | API rejects the target. |
| T11 | Diagnostic service is unavailable or times out | Client returns a controlled failure instead of crashing. |
| T12 | DNS endpoint changes | Client observes the update according to TTL and cache behaviour. |
| T13 | Successful authorized diagnostic request | Service returns a correctly structured result. |
| T14 | Logging is inspected after success and failure | Relevant events are recorded without secrets. |

### Suggested testing layers

- **Unit tests:** metadata parsing, schema rules, endpoint policy, authorization policy, and response normalization.
- **Integration tests:** discovery client, validating resolver, TLS connection, API service, and credential checks working together.
- **Security tests:** DNSSEC failures, invalid TLS identities, malformed requests, missing credentials, unauthorized operations, and forbidden targets.
- **Regression tests:** ensure that a fix for one failure does not allow previously rejected inputs.

Example test command when the repository uses `pytest`:

```bash
python -m pytest -q
```

Record the actual command, date, test environment, test count, and failures in the project report. Do not report tests as passed until they have been executed and the results reviewed.

## 17. Expected Results and Metrics

The evaluation should compare the selected baseline with TrustDiag in the same controlled environment. Useful metrics include:

- **Discovery latency:** time required to resolve and process the service information.
- **Invocation latency:** time from request submission to response, separately from discovery time where practical.
- **Success rate:** successful authorized operations divided by total valid test operations.
- **Invalid-discovery rejection rate:** invalid DNS or metadata cases correctly rejected divided by invalid cases tested.
- **Unauthorized-request rejection rate:** unauthorized operations correctly denied divided by unauthorized cases tested.
- **Failure handling:** whether service outage, timeout, or resolver failure is reported without a crash or unsafe fallback.
- **Endpoint-change behaviour:** time and requests needed to observe a DNS update under the configured TTL and cache conditions.

Possible comparison baselines are static endpoint configuration, DNS discovery without the additional TrustDiag workflow, and TrustDiag with its configured validation and access controls. State exactly what each baseline includes. Measure results; do not insert expected values as if they were experimental results.

## 18. Error Handling and Audit Logging

The system should use stable internal error codes and safe client-facing messages for situations such as:

- DNS query failure or timeout.
- DNSSEC bogus, insecure, or indeterminate status.
- Missing or invalid metadata.
- Disallowed endpoint.
- TLS certificate or hostname verification failure.
- Missing or invalid credentials.
- Authorization denial.
- Unsupported diagnostic operation.
- Unapproved target.
- Diagnostic timeout or unavailable service.

Logs should make it possible to correlate a request across discovery and service invocation using a non-secret request identifier. Where appropriate, record timestamp, service name, validation outcome, operation, authorization decision, duration, and final status. Avoid logging authorization headers, bearer tokens, private keys, or unnecessary sensitive network details. Limit log access and retention according to the lab's requirements.

## 19. Safety, Privacy, and Limitations

- Run the prototype only in a lab or on systems and targets for which the team has authorization.
- Use an allowlist to prevent arbitrary scanning and server-side request forgery (SSRF).
- Limit request rates and diagnostic timeouts to avoid overwhelming targets.
- Keep lab CA private keys and bearer tokens confidential.
- Use synthetic or non-sensitive data in demonstrations and screenshots.
- Clearly label simulated diagnostics, and never present simulated values as real measurements.
- DNS caching can delay visibility of a legitimate record change until cached data expires.
- DNSSEC status depends on correct resolver configuration and a valid trust chain.
- TLS certificate identity checks require correct certificates and hostname matching.
- Traceroute and similar techniques may return incomplete results because some network devices filter or rate-limit probes.
- A prototype and a finite test suite cannot prove that the system is immune to all attacks.
- The selected DNS-AID or other discovery draft may evolve; the implementation must pin and document the version it actually follows.

## 20. Development Roadmap

### Phase 1 — Requirements and specification

- Confirm project requirements and the exact discovery specification revision.
- Define service names, metadata fields, threat model, trust policy, and interfaces.
- Establish the test plan and a controlled lab scope.

### Phase 2 — DNS infrastructure

- Configure an authoritative lab DNS zone.
- Sign the zone and configure trust validation for the lab.
- Test valid, bogus, and unavailable validation outcomes.

### Phase 3 — Diagnostic APIs

- Implement the latency, connectivity, and routing services.
- Restrict targets and validate request parameters.
- Define consistent success and error responses.

### Phase 4 — Discovery client

- Implement DNS queries and metadata parsing.
- Apply DNSSEC policy and metadata validation.
- Reject disallowed endpoints and handle DNS errors.

### Phase 5 — Secure invocation

- Configure HTTPS/TLS with hostname verification.
- Implement credential validation and server-side authorization.
- Add audit logging and fail-closed handling.

### Phase 6 — Testing and evaluation

- Complete unit, integration, and security tests.
- Record measured latency and rejection results.
- Investigate failures and rerun regression tests.

### Phase 7 — End-to-end demonstration

- Test the client and server together in the controlled environment.
- Demonstrate successful discovery and invocation as well as security failures.
- Document DNS cache and endpoint-update behaviour.

### Phase 8 — Submission

- Finalize the README, source documentation, diagrams, test evidence, evaluation, and project report.
- Remove secrets and machine-specific files from the repository.
- Verify that all claimed features and results are supported by code or test evidence.

## 21. Troubleshooting

### The service name does not resolve

Check the queried name, authoritative-zone configuration, resolver address, network connectivity, and DNS record existence. Confirm that the client is querying the intended lab resolver.

### DNSSEC validation fails

Check zone signing, signatures and their validity period, parent/child delegation where applicable, resolver trust-anchor configuration, and system clock. Do not disable DNSSEC validation to make the protected flow pass; investigate and fix the trust configuration.

### The client reports an indeterminate validation result

Confirm that the client is using a validating resolver and that the relevant trust anchor is installed. An authoritative server returning signed records does not, by itself, prove that the client validated those records.

### TLS certificate verification fails

Check certificate validity, hostname or subject alternative name, CA trust configuration, and system time. Connect using a hostname that matches the certificate. Do not disable verification in the final demonstration.

### The API returns an authentication or authorization error

Verify that the token is supplied through the intended mechanism and that the requested operation is allowed for that client. Keep authentication failures separate from authorization denials when reviewing logs.

### A diagnostic target is rejected

Confirm that the target is part of the explicit lab allowlist and that the client is requesting a supported target identifier. Do not remove target restrictions to make the test pass.

### An endpoint update is not immediately visible

Review the record TTL, resolver cache, and any application-level cache. A DNS update does not invalidate all cached answers immediately; test according to the configured cache and expiry behaviour.

## 22. References

The following foundational documents are relevant to the design. The exact DNS-AID or service-discovery proposal revision used by the project must be pinned separately in the project report.

1. R. Arends, R. Austein, M. Larson, D. Massey, and S. Rose, **DNS Security Introduction and Requirements**, RFC 4033, March 2005. https://www.rfc-editor.org/rfc/rfc4033
2. R. Arends, R. Austein, M. Larson, D. Massey, and S. Rose, **Resource Records for the DNS Security Extensions**, RFC 4034, March 2005. https://www.rfc-editor.org/rfc/rfc4034
3. R. Arends, R. Austein, M. Larson, D. Massey, and S. Rose, **Protocol Modifications for the DNS Security Extensions**, RFC 4035, March 2005. https://www.rfc-editor.org/rfc/rfc4035
4. M. Bishop, **Service Binding and Parameter Specification via the DNS (SVCB and HTTPS Resource Records)**, RFC 9460, November 2023. https://www.rfc-editor.org/rfc/rfc9460
5. E. Rescorla, **The Transport Layer Security (TLS) Protocol Version 1.3**, RFC 8446, August 2018. https://www.rfc-editor.org/rfc/rfc8446
6. R. Fielding, M. Nottingham, and J. Reschke, **HTTP Semantics**, RFC 9110, June 2022. https://www.rfc-editor.org/rfc/rfc9110
7. IETF Datatracker, **DNS-AID Internet-Draft record** (consult the revision selected for this project and cite the exact revision used). https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/

These references provide background standards and proposals; they do not imply that TrustDiag already implements every feature described in them. The report should map each implemented mechanism to the exact requirements and specification clauses that were tested.

## 23. Team

| Role | Details |
|---|---|
| Hackathon project | PS-033 — DNS-Based Discovery of Diagnostic Services |
| Solution name | TrustDiag |
| Team code | A3-PS033-TC318 |
| Team name | Team rocks |
| Student | Sudhakar A |
| Student | Thanush Priyan R |
| Project guide | Dr. E. Bijolin Edwin, M.E., Ph.D. |

---

**TrustDiag — discover carefully, validate trust, authenticate clients, authorize operations, and audit diagnostic activity.**
