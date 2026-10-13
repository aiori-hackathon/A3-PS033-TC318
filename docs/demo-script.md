# Demonstration Script

1. Show `python -m src.client.main list`.
2. Start the validating resolver and confirm `dig @127.0.0.1 -p 5353 latency.ps033.test SVCB +dnssec` returns the expected record and a trusted validating path.
3. Run `python -m src.client.main discover latency` and show `dnssec_status: secure` only when the resolver actually validates the signed zone.
4. Run `python -m src.client.main diagnose latency` with a configured authorized token and show the result says `mode: simulated`.
5. Use a controlled test zone with an invalid signature; verify the validating resolver returns a validation failure and discovery exits nonzero. Do not test against public DNS.
6. Replace an SVCB target with an invalid/out-of-zone hostname; confirm metadata validation rejects it.
7. Run the API without a token or with an invalid token; expect HTTP 401.
8. Use a valid token lacking a service permission; expect HTTP 403.
9. Stop an API and invoke its service; confirm the client reports a connection/timeout error rather than bypassing validation.
10. Change an SVCB target in the lab zone, increment the SOA serial, re-sign/reload the zone, wait for TTL/cache expiry or pass `--no-cache`, then discover again. Explain that discovery changes do not guarantee service health or failover.

Capture real screenshots and actual command output during the live demo. Do not use this procedure as evidence that steps have already been run.
