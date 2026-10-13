import hashlib

import dns.flags
import dns.message
import dns.rcode
import pytest

from src.common.errors import EndpointPolicyError, MetadataError
from src.discovery.metadata import validate_hostname, validate_target_ip
from src.discovery.validator import ValidationStatus, classify_dns_response
from src.security.authorization import Principal, can_invoke


def test_hostname_accepts_only_configured_lab_zone():
    assert validate_hostname("latency-api.ps033.test.", "ps033.test") == "latency-api.ps033.test"


def test_hostname_rejects_outside_zone():
    with pytest.raises(EndpointPolicyError):
        validate_hostname("metadata.evil.example", "ps033.test")


def test_hostname_rejects_underscore_label():
    with pytest.raises(MetadataError):
        validate_hostname("bad_name.ps033.test", "ps033.test")


def test_target_ip_must_be_allow_listed():
    assert validate_target_ip("127.0.0.1", ("127.0.0.1",)) == "127.0.0.1"
    with pytest.raises(EndpointPolicyError):
        validate_target_ip("192.0.2.1", ("127.0.0.1",))


def test_authorization_is_per_service():
    principal = Principal("test", frozenset({"latency"}))
    assert can_invoke(principal, "latency")
    assert not can_invoke(principal, "routing")


def test_dnssec_ad_bit_is_secure_for_configured_trusted_resolver():
    response = dns.message.make_response(dns.message.make_query("latency.ps033.test", "SVCB"))
    response.flags |= dns.flags.AD
    result = classify_dns_response(response)
    assert result.status is ValidationStatus.SECURE
    assert result.authenticated_data


def test_missing_ad_is_not_treated_as_secure():
    response = dns.message.make_response(dns.message.make_query("latency.ps033.test", "SVCB"))
    result = classify_dns_response(response)
    assert result.status is ValidationStatus.INSECURE
    assert not result.authenticated_data


def test_servfail_without_validation_reason_is_indeterminate():
    response = dns.message.make_response(dns.message.make_query("latency.ps033.test", "SVCB"))
    response.set_rcode(dns.rcode.SERVFAIL)
    result = classify_dns_response(response)
    assert result.status is ValidationStatus.INDETERMINATE
