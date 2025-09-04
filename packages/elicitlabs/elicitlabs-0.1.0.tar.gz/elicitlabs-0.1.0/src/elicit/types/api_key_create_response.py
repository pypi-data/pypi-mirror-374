# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["APIKeyCreateResponse"]


class APIKeyCreateResponse(BaseModel):
    id: str
    """Unique identifier for the API key"""

    api_key: str
    """The actual API key (only shown once)"""

    created_at: str
    """Creation timestamp"""

    org_id: str
    """Organization ID"""

    user_id: str
    """User ID"""

    label: Optional[str] = None
    """Label for the API key"""

    success: Optional[bool] = None
    """Indicates successful creation"""
