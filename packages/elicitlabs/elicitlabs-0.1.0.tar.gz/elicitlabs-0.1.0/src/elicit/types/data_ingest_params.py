# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Required, TypedDict

__all__ = ["DataIngestParams"]


class DataIngestParams(TypedDict, total=False):
    content_type: Required[str]
    """MIME-ish content type string (e.g., 'email', 'text', 'file:text/plain')"""

    payload: Required[Union[str, Dict[str, object]]]
    """Raw content as string, object, or base64 encoded data"""

    user_id: Required[str]
    """User ID to associate the data with"""

    filename: Optional[str]
    """Filename of the uploaded file"""

    timestamp_override: Optional[str]
    """ISO-8601 timestamp to preserve original data moment"""
