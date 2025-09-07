# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["MachineLearnResponse"]


class MachineLearnResponse(BaseModel):
    message: str
    """Status message about the learning process"""

    session_id: str
    """Session identifier used for the learning"""

    job_id: Optional[str] = None
    """Job identifier if processed asynchronously"""

    success: Optional[bool] = None
    """Whether the learning was processed successfully"""
