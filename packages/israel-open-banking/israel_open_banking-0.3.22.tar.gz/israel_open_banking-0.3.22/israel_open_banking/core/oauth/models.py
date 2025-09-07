from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    """Token response model."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Expiration time in seconds")
    scope: str | None = Field(None, description="Scope of the token")
    consented_on: int | None = Field(default=None, description="Consent date and time")
    refresh_token: str | None = Field(None, description="Refresh token")
    refresh_token_expires_in: int | None = Field(default=None, description="Refresh token expiration time in seconds")
    metadata: str | None = Field(default=None, description="Metadata associated with the token")
