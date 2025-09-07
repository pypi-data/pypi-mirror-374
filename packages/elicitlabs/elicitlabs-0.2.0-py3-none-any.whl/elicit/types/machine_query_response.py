# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["MachineQueryResponse"]


class MachineQueryResponse(BaseModel):
    new_prompt: str
    """Edited prompt for the query"""

    raw_results: Dict[str, object]
    """Raw results from the retrieval process"""

    success: Optional[bool] = None
    """Whether the query was processed successfully"""
