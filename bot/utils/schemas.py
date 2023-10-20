from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Схема для единого ответа от API."""
    data: Any | None
    error: type[Exception] | None
