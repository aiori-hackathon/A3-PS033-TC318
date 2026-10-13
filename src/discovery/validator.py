"""DNSSEC validation state mapping for trusted validating-resolver responses."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import dns.edns
import dns.flags
import dns.rcode


class ValidationStatus(str, Enum):
    SECURE = "secure"
    INSECURE = "insecure"
    BOGUS = "bogus"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


@dataclass(frozen=True)
class ValidationResult:
    status: ValidationStatus
    authenticated_data: bool
    reason: str


def classify_dns_response(response) -> ValidationResult:
    """Classify a DNS response from the configured trusted validating resolver.

    The AD bit is only trusted because the deployment explicitly trusts the
    configured validating resolver. A recursive response without AD is not
    accepted as authenticated. SERVFAIL without DNSSEC-Bogus EDE is kept
    indeterminate rather than falsely asserted to be a cryptographic failure.
    """
    if response is None:
        return ValidationResult(ValidationStatus.ERROR, False, "No DNS response")
    authenticated = bool(response.flags & dns.flags.AD)
    rcode = response.rcode()
    if authenticated:
        return ValidationResult(ValidationStatus.SECURE, True, "Trusted resolver set AD after validation")
    if rcode == dns.rcode.SERVFAIL:
        for option in getattr(response, "options", ()):
            if isinstance(option, getattr(dns.edns, "EDEOption", ())):
                if getattr(option, "code", None) == 6:
                    return ValidationResult(ValidationStatus.BOGUS, False, "Resolver returned EDE DNSSEC Bogus")
        return ValidationResult(ValidationStatus.INDETERMINATE, False, "SERVFAIL without a DNSSEC-Bogus EDE reason")
    if rcode in (dns.rcode.NOERROR, dns.rcode.NXDOMAIN):
        return ValidationResult(ValidationStatus.INSECURE, False, "Response did not carry the AD validation signal")
    return ValidationResult(ValidationStatus.INDETERMINATE, False, f"DNS response code {dns.rcode.to_text(rcode)} without AD")
