# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ExperimentDeleteResponse"]


class ExperimentDeleteResponse(BaseModel):
    id: str
    """ID of the deleted experiment"""
