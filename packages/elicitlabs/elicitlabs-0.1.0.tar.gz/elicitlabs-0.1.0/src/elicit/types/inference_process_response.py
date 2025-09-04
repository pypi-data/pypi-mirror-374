# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["InferenceProcessResponse"]


class InferenceProcessResponse(BaseModel):
    content: str
    """Generated response content"""

    messages: List[Dict[str, object]]
    """Processed messages with memory injections"""

    session_id: str
    """Session identifier"""

    success: Optional[bool] = None
    """Whether the request was processed successfully"""
