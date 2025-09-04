# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["InferenceProcessParams"]


class InferenceProcessParams(TypedDict, total=False):
    messages: Required[Iterable[Dict[str, object]]]
    """List of conversation messages to process"""

    session_id: Required[str]
    """Session identifier for conversation continuity"""

    user_id: Required[str]
    """Unique identifier for the user"""
