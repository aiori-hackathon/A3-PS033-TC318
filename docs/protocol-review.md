# Protocol and Standards Review

Research checked 13 October 2026:

- **DNS-AID:** IETF Internet-Draft `draft-mozleywilliams-dnsop-dnsaid-02`, *DNS for AI Discovery*, published May 2026 and listed as an active Internet-Draft with an expiry of 28 November 2026. It is not an RFC or a finalized Internet Standard. It describes SVCB connectivity metadata, an agent index/discovery convention, and optional DNSSEC/DANE TLSA use. It explicitly introduces no new DNS record types. See https://datatracker.ietf.org/doc/html/draft-mozleywilliams-dnsop-dnsaid-02.
- **SVCB:** RFC 9460 defines Service Binding and HTTPS records. PS-033 uses SVCB ServiceMode records for service target, ALPN, and port; see https://www.rfc-editor.org/rfc/rfc9460.
- **DNSSEC:** RFC 4033 provides the DNSSEC introduction and requirements; see https://www.rfc-editor.org/rfc/rfc4033. In this project, DNSSEC validation is delegated to an explicitly trusted validating resolver; the client requires its AD bit and fails closed if it is absent.
- **DNS-SD:** RFC 6763 describes DNS-Based Service Discovery; PS-033 does not claim that its diagnostic naming convention is standard DNS-SD.
- **TLS:** HTTPS server certificate and hostname validation protect the invocation channel separately from DNSSEC.

## Conformance statement
The assignment's service workflow is not itself specified by DNS-AID. Therefore, PS-033 reuses SVCB/DNSSEC discovery concepts but defines the diagnostic names, route mapping, schema, authentication and authorization as a controlled lab extension. No custom DNS RR type is invented.
