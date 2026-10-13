"""Allow-listed deterministic connectivity check with no outbound packets."""
from fastapi import APIRouter, Depends
from src.common.schemas import DiagnosticRequest, DiagnosticResponse
from src.security.authentication import require_service_access
from src.services.shared import timestamp, validate_lab_target

router = APIRouter(tags=["connectivity"])


@router.post("/v1/diagnostics/connectivity", response_model=DiagnosticResponse)
def connectivity_check(request: DiagnosticRequest, _principal=Depends(require_service_access("connectivity"))) -> DiagnosticResponse:
    target = validate_lab_target(request.target)
    return DiagnosticResponse(
        service="connectivity", status="simulated", request_id=request.request_id,
        timestamp=timestamp(), mode="simulated",
        details={"target": target, "reachable": True, "check": "deterministic_simulation", "packets_sent": False},
    )
