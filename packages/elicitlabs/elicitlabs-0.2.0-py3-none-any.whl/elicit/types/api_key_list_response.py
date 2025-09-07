# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["APIKeyListResponse", "APIKey"]


class APIKey(BaseModel):
    id: str
    """Unique identifier for the API key"""

    created_at: str
    """Creation timestamp"""

    org_id: str
    """Organization ID"""

    user_id: str
    """User ID"""

    label: Optional[str] = None
    """Label for the API key"""

    last_used_at: Optional[str] = None
    """Last usage timestamp"""


class APIKeyListResponse(BaseModel):
    api_keys: List[APIKey]
    """List of API keys"""

    success: Optional[bool] = None
    """Indicates successful retrieval"""
