"""
API Request and Response schemas.

These Pydantic models are used for HTTP request validation and response serialization.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.dtos import Platform as PlatformEnum


class DonationTierSchema(BaseModel):
    """Donation tier schema for API requests/responses."""

    amount_usd: float = Field(
        ...,
        gt=0,
        le=1000.0,
        description="Donation amount in USD",
        json_schema_extra={"example": 5.0},
    )
    popup_message: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Message shown on stream",
        json_schema_extra={"example": "Amazing support! 🎉"},
    )
    duration_ms: int = Field(
        default=3000,
        ge=1000,
        le=30000,
        description="Display duration in milliseconds",
        json_schema_extra={"example": 5000},
    )

    @field_validator("popup_message")
    @classmethod
    def validate_popup_message(cls, v: str) -> str:
        """Ensure popup message is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Popup message cannot be empty")
        return v.strip()


class StreamerBaseSchema(BaseModel):
    """Base schema for streamer data (shared fields)."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Streamer display name",
        json_schema_extra={"example": "Logan"},
    )
    wallet_address: str = Field(
        ...,
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="Ethereum wallet address",
        json_schema_extra={"example": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"},
    )
    platforms: list[PlatformEnum] = Field(
        ...,
        min_length=1,
        description="Streaming platforms",
        json_schema_extra={"example": ["youtube", "twitch"]},
    )
    avatar_url: HttpUrl | None = Field(
        None,
        description="Profile image URL",
        json_schema_extra={"example": "https://example.com/avatars/logan.png"},
    )
    donation_tiers: list[DonationTierSchema] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Available donation tiers",
    )
    thank_you_message: str = Field(
        default="Thank you for your support!",
        max_length=500,
        description="Message shown after donation",
        json_schema_extra={"example": "Thanks for watching my stream!"},
    )


class StreamerCreateSchema(StreamerBaseSchema):
    """
    Request schema for creating a new streamer.

    This is sent to POST /api/streamer endpoint.
    Does not include 'id' field as it will be generated server-side.
    """

    pass


class StreamerSchema(StreamerBaseSchema):
    """
    Complete streamer schema for API responses.

    This is the model returned by GET /api/streamer endpoints.
    """

    id: str = Field(
        ...,
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
        description="UUID4 streamer identifier",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "name": "Logan",
                "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "platforms": ["youtube", "twitch"],
                "avatar_url": "https://example.com/avatars/logan.png",
                "donation_tiers": [
                    {
                        "amount_usd": 1.0,
                        "popup_message": "Thank you! 💙",
                        "duration_ms": 3000,
                    },
                    {
                        "amount_usd": 5.0,
                        "popup_message": "Amazing support! 🎉",
                        "duration_ms": 5000,
                    },
                ],
                "thank_you_message": "Thanks for supporting my stream!",
            }
        }


class DonationMessageCreateSchema(BaseModel):
    """
    Request schema for creating a donation message.

    This is sent by the frontend after payment is confirmed.
    """

    amount_usd: float = Field(
        ...,
        gt=0,
        le=1000.0,
        description="Donation amount in USD",
        json_schema_extra={"example": 5.0},
    )
    donor_address: str = Field(
        ...,
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="Donor's wallet address",
        json_schema_extra={"example": "0x1234567890abcdef1234567890abcdef12345678"},
    )
    message: str | None = Field(
        None,
        max_length=200,
        description="Custom message from donor",
        json_schema_extra={"example": "Great stream! Keep it up! 🔥"},
    )
    clip_url: HttpUrl | None = Field(
        None,
        description="Clip URL (Phase 2)",
        json_schema_extra={"example": None},
    )
    tx_hash: str = Field(
        ...,
        pattern=r"^0x[a-fA-F0-9]{64}$",
        description="Blockchain transaction hash",
        json_schema_extra={
            "example": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        },
    )

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str | None) -> str | None:
        """Remove leading/trailing whitespace from message."""
        if v is not None:
            return v.strip() if v.strip() else None
        return None


class DonationMessageSchema(DonationMessageCreateSchema):
    """
    Complete donation message schema for API responses.

    This is the model returned by GET /api/donations endpoints.
    """

    donation_id: str = Field(
        ...,
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
        description="UUID4 donation identifier",
        json_schema_extra={"example": "d9e8f7g6-h5i4-3210-jklm-nopqrstuvwxy"},
    )
    streamer_id: str = Field(
        ...,
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
        description="Streamer UUID4 (foreign key)",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )
    timestamp: int = Field(
        ...,
        description="Unix timestamp (seconds)",
        json_schema_extra={"example": 1704672000},
    )

    class Config:
        json_schema_extra = {
            "example": {
                "donation_id": "d9e8f7g6-h5i4-3210-jklm-nopqrstuvwxy",
                "streamer_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "amount_usd": 5.0,
                "donor_address": "0x1234567890abcdef1234567890abcdef12345678",
                "message": "Great stream! Keep it up! 🔥",
                "clip_url": None,
                "timestamp": 1704672000,
                "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            }
        }


class DonationResponseSchema(BaseModel):
    """
    Response schema returned after successful donation message submission.

    Includes the popup message configuration for the frontend.
    """

    donation_id: str = Field(
        ...,
        description="UUID4 donation identifier",
        json_schema_extra={"example": "d9e8f7g6-h5i4-3210-jklm-nopqrstuvwxy"},
    )
    popup_message: str = Field(
        ...,
        description="Message to display on stream",
        json_schema_extra={"example": "Amazing support! 🎉"},
    )
    duration_ms: int = Field(
        ...,
        description="Display duration in milliseconds",
        json_schema_extra={"example": 5000},
    )

    class Config:
        json_schema_extra = {
            "example": {
                "donation_id": "d9e8f7g6-h5i4-3210-jklm-nopqrstuvwxy",
                "popup_message": "Amazing support! 🎉",
                "duration_ms": 5000,
            }
        }


class ErrorResponseSchema(BaseModel):
    """Standard error response schema."""

    detail: str = Field(
        ...,
        description="Error message",
        json_schema_extra={"example": "Streamer not found"},
    )

    class Config:
        json_schema_extra = {"example": {"detail": "Streamer not found"}}
