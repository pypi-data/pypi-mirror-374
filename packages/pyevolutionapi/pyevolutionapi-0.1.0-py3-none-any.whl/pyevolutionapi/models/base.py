"""
Base models and utilities for PyEvolution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, field_serializer


class BaseModel(PydanticBaseModel):
    """Base model with common configuration for all models."""

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    def dict_for_api(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for API requests.
        Removes None values and handles special cases.
        """
        return {k: v for k, v in self.model_dump(by_alias=True).items() if v is not None}


class BaseResponse(BaseModel):
    """Base model for API responses."""

    status: Optional[str] = Field(None, description="Response status")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[bool] = Field(False, description="Whether an error occurred")

    @property
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return not self.error and self.status in ["success", "ok", None]


class PagedResponse(BaseResponse):
    """Base model for paginated API responses."""

    total: Optional[int] = Field(None, description="Total number of items")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, alias="pageSize", description="Items per page")
    pages: Optional[int] = Field(None, description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Check if there are more pages."""
        if self.page is not None and self.pages is not None:
            return self.page < self.pages
        return False

    @property
    def has_previous(self) -> bool:
        """Check if there are previous pages."""
        if self.page is not None:
            return self.page > 1
        return False


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""

    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format."""
        return value.isoformat() if value else None


class ErrorDetail(BaseModel):
    """Model for error details in responses."""

    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseResponse):
    """Model for error responses."""

    error: bool = True
    errors: Optional[List[ErrorDetail]] = None
    status_code: Optional[int] = Field(None, alias="statusCode")

    def get_error_message(self) -> str:
        """Get a formatted error message."""
        if self.message:
            return self.message
        if self.errors:
            messages = [e.message for e in self.errors]
            return "; ".join(messages)
        return "Unknown error occurred"
