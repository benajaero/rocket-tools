"""Shared base for all tool schemas.

Every schema model rejects non-finite floats (NaN, +/-inf). Without this,
Pydantic's `gt`/`ge` constraints accept infinity (``inf > 0`` is True), so an
``inf`` input would propagate to an ``inf`` output instead of a clean error.
"""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base model that forbids NaN and infinite float values."""

    model_config = ConfigDict(allow_inf_nan=False)
