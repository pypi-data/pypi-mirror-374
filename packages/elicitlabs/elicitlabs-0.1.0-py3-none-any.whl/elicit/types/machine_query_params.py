# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["MachineQueryParams"]


class MachineQueryParams(TypedDict, total=False):
    question: Required[str]
    """The question to query against user's memories"""

    user_id: Required[str]
    """Unique identifier for the user"""

    session_id: Optional[str]
    """Optional session identifier for conversation context"""
