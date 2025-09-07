# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["UserCreateOrGetResponse"]


class UserCreateOrGetResponse(BaseModel):
    created_at: str
    """User creation timestamp"""

    email: str
    """User's email address"""

    name: str
    """User's name"""

    user_id: str
    """Generated user ID"""

    org_user_id: Optional[str] = None
    """Organization-specific user ID"""

    success: Optional[bool] = None
    """Whether the user was created successfully"""
