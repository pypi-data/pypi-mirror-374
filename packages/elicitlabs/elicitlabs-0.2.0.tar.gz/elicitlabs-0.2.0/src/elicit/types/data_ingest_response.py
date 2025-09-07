# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["DataIngestResponse"]


class DataIngestResponse(BaseModel):
    content_type: str
    """Content type that was processed"""

    created_at: str
    """Timestamp when job was created"""

    job_id: str
    """Unique job identifier for tracking"""

    status: str
    """Processing status ('accepted', 'queued', 'failed')"""

    user_id: str
    """User ID associated with the data"""

    message: Optional[str] = None
    """Additional status or error message"""

    success: Optional[bool] = None
    """Whether the request was accepted successfully"""
