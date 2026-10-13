"""FastAPI entry point for one service or all services in local tests."""
from __future__ import annotations
import logging
import os
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.services import latency, connectivity, routing
from src.config.settings import get_settings

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("ps033.api")

app = FastAPI(title="PS-033 Diagnostic API", version="1.0.0", docs_url="/docs", redoc_url=None)
kind = os.getenv("SERVICE_KIND", "all").strip().lower()
routers = {"latency": latency.router, "connectivity": connectivity.router, "routing": routing.router}
if kind == "all":
    for router in routers.values():
        app.include_router(router)
elif kind in routers:
    app.include_router(routers[kind])
else:
    raise RuntimeError("SERVICE_KIND must be all, latency, connectivity, or routing")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service_kind": kind}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {
        "code": "request_validation_failed",
        "message": "Request did not match the expected schema.",
        "request_id": str(uuid4()),
        "fields": [{"field": ".".join(str(part) for part in item["loc"]), "type": item["type"]} for item in exc.errors()],
    }})


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    # Keep internal exception details out of responses/logs; a request ID allows
    # operators to correlate this generic error with trusted server-side logging.
    request_id = str(uuid4())
    logger.error("Unhandled API exception request_id=%s exception_type=%s", request_id, type(exc).__name__)
    return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "Internal server error.", "request_id": request_id}})
