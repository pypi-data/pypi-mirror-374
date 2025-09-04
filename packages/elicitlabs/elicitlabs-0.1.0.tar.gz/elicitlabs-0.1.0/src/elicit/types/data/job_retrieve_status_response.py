# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["JobRetrieveStatusResponse"]


class JobRetrieveStatusResponse(BaseModel):
    job_id: str
    """The job ID"""

    status: str
    """Current job status"""
