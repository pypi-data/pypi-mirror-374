# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["MachineLearnParams"]


class MachineLearnParams(TypedDict, total=False):
    message: Required[Union[Iterable[Dict[str, object]], Dict[str, object], str]]
    """Message content to learn from"""

    user_id: Required[str]
    """Unique identifier for the user"""

    datetime_input: Optional[str]
    """ISO format datetime string for the message timestamp"""

    session_id: Optional[str]
    """Optional session identifier for conversation context"""

    speaker: str
    """Speaker of the message"""
