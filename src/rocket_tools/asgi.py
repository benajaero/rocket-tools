"""Production ASGI entry point with MCP SSE, health, and metrics."""

from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from rocket_tools.config import settings
from rocket_tools.server import mcp

# ---- Metrics Storage ----
_request_count = 0
_request_errors = 0


# ---- Health Endpoints ----


async def health(request):
    """Liveness probe — returns 200 if the process is running."""
    return JSONResponse(
        {
            "status": "ok",
            "service": "rocket-tools",
            "version": "0.3.0",
        }
    )


async def ready(request):
    """Readiness probe — returns 200 if the server is ready to serve requests."""
    # In the future, check external dependencies here
    return JSONResponse(
        {
            "status": "ready",
            "service": "rocket-tools",
            "version": "0.3.0",
            "tools": 11,
        }
    )


async def metrics(request):
    """Prometheus-compatible metrics endpoint."""
    if not settings.metrics_enabled:
        return PlainTextResponse("# Metrics disabled", status_code=503)

    lines = [
        "# HELP rocket_tools_info Service info",
        "# TYPE rocket_tools_info gauge",
        f'{settings.metrics_prefix}_info{{version="0.3.0"}} 1',
        "",
        "# HELP rocket_tools_health Health status",
        "# TYPE rocket_tools_health gauge",
        f"{settings.metrics_prefix}_health 1",
    ]
    return PlainTextResponse("\n".join(lines))


async def root(request):
    """Root endpoint with service metadata."""
    return JSONResponse(
        {
            "service": "rocket-tools",
            "version": "0.3.0",
            "description": "Aerospace engineering intelligence for AI agents",
            "endpoints": {
                "mcp": "/sse",
                "health": "/health",
                "ready": "/ready",
                "metrics": "/metrics",
            },
            "tools": 11,
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

# Manually mount the SSE sub-app
app.mount("/sse", mcp_sse_app)
