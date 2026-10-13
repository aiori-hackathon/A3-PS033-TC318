# PS-033 Architecture and Security Design

## Scope
PS-033 is a controlled laboratory prototype for DNS-based discovery and protected invocation of three simulated diagnostic APIs. It is not a public service registry and the default diagnostics send no packets to arbitrary targets.

## Request flow
1. CLI selects `latency`, `connectivity`, or `routing`.
2. Client queries the configured recursive validating resolver for an SVCB record and the target A record.
3. The client accepts the response only when the configured trusted resolver returns the AD (Authenticated Data) bit and `PS033_DNS_REQUIRE_AD=true`.
4. The SVCB record is parsed and checked against the allowed DNS zone, service-specific port, supported ALPN, and IP allow-list.
5. The client connects using HTTPS with certificate and hostname verification.
6. The API authenticates a bearer token by comparing its SHA-256 digest against configured token-policy digests.
7. Server-side authorization checks the requested diagnostic capability.
8. Pydantic validates input; connectivity/routing targets are constrained to the lab allow-list; the API returns a clearly labelled simulation.

## Security boundaries
- DNSSEC validation is performed by a configured trusted validating resolver. The AD bit is meaningful only when the client trusts the resolver and the path to it. The client does not claim to validate signatures itself.
- HTTPS certificate validation is independent of DNSSEC. Use a lab CA and install its certificate as the client's trust anchor.
- Authentication establishes token validity; authorization separately checks per-service permissions.
- DNS metadata is untrusted input until DNSSEC policy and local schema/endpoint checks pass.
- The IP allow-list limits DNS rebinding and endpoint redirection risk. Never expand it to arbitrary public or private addresses for convenience.

## Limitations
The project uses SVCB ServiceMode records for transport discovery and a PS-033-specific service naming convention. This is an explicitly documented laboratory extension, not a claim that diagnostic service invocation is defined by DNS-AID. The draft's scope is AI-agent discovery and it does not define the application metadata schema or invocation workflow. The DNSSEC trust chain is only complete after the operator runs the signing script, installs the generated trust anchor into the validating resolver configuration, and verifies the result from the client environment.
