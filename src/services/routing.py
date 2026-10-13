"""Synthetic route diagnostic; does not run traceroute or scan a network."""
from fastapi import APIRouter, Depends
from src.common.schemas import DiagnosticRequest, DiagnosticResponse
from src.security.authentication import require_service_access
from src.services.shared import timestamp, validate_lab_target

router = APIRouter(tags=["routing"])


@router.post("/v1/diagnostics/routing", response_model=DiagnosticResponse)
def routing_diagnostic(request: DiagnosticRequest, _principal=Depends(require_service_access("routing"))) -> DiagnosticResponse:
    target = validate_lab_target(request.target)
    return DiagnosticResponse(
        service="routing", status="simulated", request_id=request.request_id,
        timestamp=timestamp(), mode="simulated",
        details={
            "target": target,
            "hops": [
                {"hop": 1, "host": "lab-gateway.ps033.test", "latency_ms": 1.1},
                {"hop": 2, "host": "lab-core.ps033.test", "latency_ms": 2.7},
                {"hop": 3, "host": target, "latency_ms": 4.2},
            ],
            "simulation": True,
            "packets_sent": False,
        },
    )
