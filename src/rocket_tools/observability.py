"""Observability: structured logging, metrics, and request tracing."""

from contextvars import ContextVar

from prometheus_client import Counter, Histogram, generate_latest

from rocket_tools.config import settings

# ---- Request Context ----

request_id_var: ContextVar[str] = ContextVar("request_id")

# ---- Metrics ----

_TOOL_CALL_COUNTER = Counter(
    f"{settings.metrics_prefix}_tool_calls_total",
    "Total tool calls",
    ["tool_name", "status"],
)

_TOOL_CALL_DURATION = Histogram(
    f"{settings.metrics_prefix}_tool_call_duration_seconds",
    "Tool call duration in seconds",
    ["tool_name"],
    buckets=[0.0001, 0.001, 0.01, 0.1, 1.0, 10.0],
)

_REQUEST_COUNTER = Counter(
    f"{settings.metrics_prefix}_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

_REQUEST_DURATION = Histogram(
    f"{settings.metrics_prefix}_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.0001, 0.001, 0.01, 0.1, 1.0, 10.0],
)


# ---- Tool Metrics Wrapper ----


def record_tool_call(tool_name: str, status: str = "success", duration: float = 0.0) -> None:
    """Record a tool call in Prometheus metrics."""
    if not settings.metrics_enabled:
        return
    _TOOL_CALL_COUNTER.labels(tool_name=tool_name, status=status).inc()
    _TOOL_CALL_DURATION.labels(tool_name=tool_name).observe(duration)


def record_http_request(method: str, endpoint: str, status: int, duration: float) -> None:
    """Record an HTTP request in Prometheus metrics."""
    if not settings.metrics_enabled:
        return
    status_class = f"{status // 100}xx"
    _REQUEST_COUNTER.labels(method=method, endpoint=endpoint, status=status_class).inc()
    _REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def get_prometheus_metrics() -> bytes:
    """Get current Prometheus metrics as bytes."""
    return generate_latest()
