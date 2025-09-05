"""
Common type definitions for the Konigle SDK.

This module defines common types, type aliases, and generic types
used throughout the SDK.
"""

from datetime import datetime
from typing import Any, BinaryIO, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

# Type aliases for common data structures
JSONDict = Dict[str, Any]
Headers = Dict[str, str]
QueryParams = Dict[str, Union[str, int, float, bool]]

# File input types
FileInput = Union[str, bytes, "BinaryIO"]

# Generic type variable for resources
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standardized pagination response wrapper.

    This generic class wraps paginated API responses with metadata
    about the pagination state and navigation.
    """

    payload: List[T] = Field(...)
    """List of resources in this page."""

    count: int = Field(..., ge=0)
    """Total number of resources."""

    next: Optional[str] = Field(None)
    """URL for next page."""

    previous: Optional[str] = Field(None)
    """URL for previous page."""

    page_size: int = Field(..., gt=0)
    """Number of items per page."""

    current_page: int = Field(..., ge=1)
    """Current page number."""

    num_pages: int = Field(..., ge=0)
    """Total number of pages."""

    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.next is not None

    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.previous is not None

    @property
    def is_first_page(self) -> bool:
        """Check if this is the first page."""
        return self.current_page == 1

    @property
    def is_last_page(self) -> bool:
        """Check if this is the last page."""
        return self.current_page == self.num_pages


class PaginationParams(BaseModel):
    """
    Pagination parameter validation and defaults.

    Used to validate and normalize pagination parameters
    across all list operations.
    """

    page: int = Field(1, ge=1)
    """Page number."""

    page_size: int = Field(20, ge=1, le=200)
    """Items per page."""


class TimestampMixin(BaseModel):
    """
    Mixin for models that include timestamp fields.

    Provides common timestamp fields that many resources include.
    """

    created_at: datetime = Field(...)
    """Creation timestamp."""

    updated_at: datetime = Field(...)
    """Last update timestamp."""


class IDMixin(BaseModel):
    """
    Mixin for models that include an ID field.

    Provides the standard ID field that most resources include.
    Default type is string to handle UUIDs and large integers from API.
    Resource models can override the type if needed.
    """

    id: str = Field(...)
    """Unique identifier."""
