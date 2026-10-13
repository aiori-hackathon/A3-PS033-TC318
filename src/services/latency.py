"""Simulated latency probe; does not claim to measure network RTT."""
from fastapi import APIRouter, Depends
from src.common.schemas import DiagnosticRequest, DiagnosticResponse
from src.security.authentication import require_service_access
from src.services.shared import timestamp

router = APIRouter(tags=["latency"])


@router.post("/v1/diagnostics/latency", response_model=DiagnosticResponse)
def latency_probe(request: DiagnosticRequest, _principal=Depends(require_service_access("latency"))) -> DiagnosticResponse:
    return DiagnosticResponse(
        service="latency", status="simulated", request_id=request.request_id,
        timestamp=timestamp(), mode="simulated",
        details={"latency_ms": 12.4, "measurement": "simulated_fixture", "note": "This value is synthetic, not a measured network round trip."},
    )
