"""Production ASGI entry point with MCP SSE, health, and metrics."""

from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

import rocket_tools
from rocket_tools.config import settings
from rocket_tools.observability import get_prometheus_metrics, record_http_request
from rocket_tools.server import mcp

# ---- Middleware ----


class MetricsMiddleware(BaseHTTPMiddleware):
    """Record request metrics and add request IDs."""

    async def dispatch(self, request: Request, call_next):
        import time
        import uuid

        start = time.perf_counter()
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        response = await call_next(request)

        duration = time.perf_counter() - start
        endpoint = request.url.path
        record_http_request(request.method, endpoint, response.status_code, duration)

        response.headers["X-Request-ID"] = request_id
        return response


# ---- Health Endpoints ----


async def health(request):
    """Liveness probe — returns 200 if the process is running."""
    return JSONResponse(
        {
            "status": "ok",
            "service": "rocket-tools",
            "version": rocket_tools.__version__,
        }
    )


async def ready(request):
    """Readiness probe — returns 200 if the server is ready to serve requests."""
    # In the future, check external dependencies here
    return JSONResponse(
        {
            "status": "ready",
            "service": "rocket-tools",
            "version": rocket_tools.__version__,
            "tools": 35,
        }
    )


async def metrics(request):
    """Prometheus-compatible metrics endpoint."""
    if not settings.metrics_enabled:
        return PlainTextResponse("# Metrics disabled", status_code=503)

    return PlainTextResponse(get_prometheus_metrics().decode("utf-8"))


async def root(request):
    """Root endpoint with service metadata."""
    return JSONResponse(
        {
            "service": "rocket-tools",
            "version": rocket_tools.__version__,
            "description": "Aerospace engineering intelligence for AI agents",
            "endpoints": {
                "mcp": "/sse",
                "health": "/health",
                "ready": "/ready",
                "metrics": "/metrics",
            },
            "tools": 35,
        }
    )


# ---- Lifespan ----


@asynccontextmanager
async def lifespan(app):
    """Application lifespan — startup and shutdown hooks."""
    # Startup
    yield
    # Shutdown


# ---- Starlette App ----

routes = [
    Route("/", root),
    Route("/health", health),
    Route("/ready", ready),
    Route("/metrics", metrics),
]

# Mount the MCP SSE app at /sse
mcp_sse_app = mcp.sse_app()

app = Starlette(
    debug=settings.server_log_level == "debug",
    routes=routes,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(MetricsMiddleware)

# Manually mount the SSE sub-app
app.mount("/sse", mcp_sse_app)
