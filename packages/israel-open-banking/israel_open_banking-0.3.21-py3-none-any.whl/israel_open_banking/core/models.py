"""
Base models for the Israel Open Banking SDK.

This module contains Pydantic models that serve as the foundation
for all data structures used throughout the SDK.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, field_validator


class BaseModel(PydanticBaseModel):
    """Base model with common configuration for all SDK models."""

    model_config = ConfigDict(
        # Allow extra fields to be ignored
        extra="ignore",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignments
        validate_assignment=True,
        # Allow population by field name
        populate_by_name=True,
    )


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    success: bool = Field(..., description="Whether the request was successful")
    message: str | None = Field(None, description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    request_id: str | None = Field(None, description="Unique request identifier")

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                pass
        if isinstance(v, datetime):
            return v
        raise ValueError(f"Invalid timestamp format: {v}")


class PaginationInfo(BaseModel):
    """Pagination information for paginated responses."""

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseResponse):
    """Base model for paginated API responses."""

    pagination: PaginationInfo | None = Field(
        None, description="Pagination information"
    )
    data: Any | None = Field(None, description="Response data")


class ErrorResponse(BaseResponse):
    """Model for error responses."""

    success: bool = Field(False, description="Always false for error responses")
    error_code: str | None = Field(None, description="Error code")
    error_details: dict[str, Any] | None = Field(
        None, description="Additional error details"
    )

    @field_validator("success")
    @classmethod
    def validate_success(cls, v: bool) -> bool:
        """Ensure success is always False for error responses."""
        if v:
            raise ValueError("Error responses must have success=False")
        return False


class ConsentRequest(BaseModel):
    """Base model for consent requests."""

    consent_id: str = Field(..., description="Unique consent identifier")
    user_id: str = Field(..., description="User identifier")
    provider: str = Field(..., description="Financial service provider")
    permissions: list[str] = Field(..., description="Requested permissions")
    expires_at: datetime | None = Field(None, description="Consent expiration time")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class ConsentResponse(BaseResponse):
    """Model for consent responses."""

    consent_id: str = Field(..., description="Consent identifier")
    status: str = Field(..., description="Consent status")
    granted_permissions: list[str] = Field(..., description="Granted permissions")
    expires_at: datetime | None = Field(None, description="Consent expiration time")
