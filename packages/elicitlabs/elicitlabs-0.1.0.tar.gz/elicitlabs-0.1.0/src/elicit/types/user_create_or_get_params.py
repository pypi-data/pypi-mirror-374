# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["UserCreateOrGetParams"]


class UserCreateOrGetParams(TypedDict, total=False):
    email: Required[str]
    """User's email address"""

    name: Required[str]
    """User's full name"""

    org_user_id: Optional[str]
    """Organization-specific user ID"""
