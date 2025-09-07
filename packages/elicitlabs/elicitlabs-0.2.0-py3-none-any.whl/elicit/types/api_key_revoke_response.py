# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["APIKeyRevokeResponse"]


class APIKeyRevokeResponse(BaseModel):
    message: str
    """Confirmation message"""

    success: Optional[bool] = None
    """Indicates successful revocation"""
