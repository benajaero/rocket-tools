"""Application settings with pydantic-settings.

All hardcoded constants from across the codebase are centralized here
and can be overridden via environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Rocket-tools production configuration."""

    model_config = SettingsConfigDict(
        env_prefix="ROCKET_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- ISA Atmosphere ---
    isa_max_altitude_m: float = 25_000.0
    isa_altitude_step_m: float = 1.0
    isa_t0: float = 288.15
    isa_p0: float = 101_325.0
    isa_g_std: float = 9.80665
    isa_r_air: float = 287.05

    # --- Session Memory ---
    session_ttl_seconds: float = 86_400.0
    session_cleanup_interval: int = 100

    # --- Caching ---
    isa_cache_size: int = 1024
    fast_cache_size: int = 128

    # --- Server ---
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_log_level: str = "info"
    server_request_timeout: float = 30.0
    server_max_payload_size: int = 1_000_000  # 1 MB

    # --- Router ---
    router_confidence_threshold: float = 0.4
    router_session_confidence_floor: float = 0.5
    router_tool_name_boost: float = 0.15

    # --- Security ---
    rate_limit_requests_per_minute: int = 120
    rate_limit_burst: int = 10

    # --- Observability ---
    metrics_enabled: bool = True
    metrics_prefix: str = "rocket_tools"


# Singleton instance — import this everywhere
settings = Settings()
