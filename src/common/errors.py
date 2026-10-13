"""Typed errors shared by the discovery client and API."""

class PS033Error(Exception):
    code = "ps033_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class DiscoveryError(PS033Error):
    code = "discovery_error"


class DNSSECValidationError(DiscoveryError):
    code = "dnssec_validation_failed"

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


class MetadataError(DiscoveryError):
    code = "invalid_metadata"


class EndpointPolicyError(DiscoveryError):
    code = "endpoint_policy_rejected"


class ServiceUnavailable(PS033Error):
    code = "service_unavailable"
