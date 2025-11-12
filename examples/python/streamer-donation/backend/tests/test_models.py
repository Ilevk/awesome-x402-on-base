"""Tests for data models (DTOs and Schemas)."""

import pytest
from pydantic import ValidationError

from app.models.dtos import (
    DonationMessage,
    DonationTier,
    Platform,
    Streamer,
)
from app.models.schemas import (
    DonationMessageCreateSchema,
    DonationMessageSchema,
    DonationResponseSchema,
    DonationTierSchema,
    ErrorResponseSchema,
    StreamerSchema,
)


class TestDonationTier:
    """Test DonationTier DTO."""

    def test_create_valid_tier(self) -> None:
        """Test creating a valid donation tier."""
        tier = DonationTier(amount_usd=5.0, popup_message="Thank you!", duration_ms=3000)
        assert tier.amount_usd == 5.0
        assert tier.popup_message == "Thank you!"
        assert tier.duration_ms == 3000

    def test_tier_equality(self) -> None:
        """Test DonationTier equality comparison."""
        tier1 = DonationTier(amount_usd=5.0, popup_message="Thank you!", duration_ms=3000)
        tier2 = DonationTier(amount_usd=5.0, popup_message="Thank you!", duration_ms=3000)
        tier3 = DonationTier(amount_usd=10.0, popup_message="Amazing!", duration_ms=5000)
        assert tier1 == tier2
        assert tier1 != tier3


class TestPlatform:
    """Test Platform enum."""

    def test_platform_values(self) -> None:
        """Test all platform enum values."""
        assert Platform.YOUTUBE.value == "youtube"
        assert Platform.TWITCH.value == "twitch"

    def test_platform_from_string(self) -> None:
        """Test creating platform from string."""
        platform = Platform("youtube")
        assert platform == Platform.YOUTUBE


class TestStreamer:
    """Test Streamer DTO."""

    def test_create_valid_streamer(self, sample_streamer: Streamer) -> None:
        """Test creating a valid streamer."""
        assert sample_streamer.name == "TestStreamer"
        assert sample_streamer.wallet_address == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        assert len(sample_streamer.platforms) == 2
        assert len(sample_streamer.donation_tiers) == 3
        assert sample_streamer.thank_you_message == "Thanks for watching!"

    def test_streamer_equality(self, sample_streamer: Streamer) -> None:
        """Test Streamer equality comparison."""
        streamer2 = Streamer(
            id=sample_streamer.id,
            name=sample_streamer.name,
            wallet_address=sample_streamer.wallet_address,
            platforms=sample_streamer.platforms,
            donation_tiers=sample_streamer.donation_tiers,
            thank_you_message=sample_streamer.thank_you_message,
            avatar_url=sample_streamer.avatar_url,
        )
        assert sample_streamer == streamer2

    def test_streamer_with_optional_avatar(self) -> None:
        """Test streamer with and without avatar URL."""
        # With avatar
        streamer_with_avatar = Streamer(
            id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
            name="Test",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            platforms=[Platform.YOUTUBE],
            donation_tiers=[DonationTier(amount_usd=1.0, popup_message="Thanks", duration_ms=3000)],
            thank_you_message="Thank you!",
            avatar_url="https://example.com/avatar.png",
        )
        assert streamer_with_avatar.avatar_url == "https://example.com/avatar.png"

        # Without avatar
        streamer_without_avatar = Streamer(
            id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
            name="Test",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            platforms=[Platform.YOUTUBE],
            donation_tiers=[DonationTier(amount_usd=1.0, popup_message="Thanks", duration_ms=3000)],
            thank_you_message="Thank you!",
            avatar_url=None,
        )
        assert streamer_without_avatar.avatar_url is None


class TestDonationMessage:
    """Test DonationMessage DTO."""

    def test_create_valid_donation(self, sample_donation: DonationMessage) -> None:
        """Test creating a valid donation message."""
        assert sample_donation.amount_usd == 5.0
        assert sample_donation.donor_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert sample_donation.message == "Great stream!"
        assert sample_donation.clip_url is None

    def test_donation_equality(self, sample_donation: DonationMessage) -> None:
        """Test DonationMessage equality comparison."""
        donation2 = DonationMessage(
            donation_id=sample_donation.donation_id,
            streamer_id=sample_donation.streamer_id,
            amount_usd=sample_donation.amount_usd,
            donor_address=sample_donation.donor_address,
            tx_hash=sample_donation.tx_hash,
            timestamp=sample_donation.timestamp,
            message=sample_donation.message,
            clip_url=sample_donation.clip_url,
        )
        assert sample_donation == donation2

    def test_donation_with_optional_fields(self) -> None:
        """Test donation with optional message and clip_url."""
        # Without optional fields
        donation = DonationMessage(
            donation_id="d1e2f3a4-b5c6-4890-9bcd-ab1234567890",
            streamer_id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
            amount_usd=5.0,
            donor_address="0x1234567890abcdef1234567890abcdef12345678",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            timestamp=1699999999,
            message=None,
            clip_url=None,
        )
        assert donation.message is None
        assert donation.clip_url is None


class TestStreamerSchema:
    """Test StreamerSchema Pydantic model."""

    def test_valid_streamer_schema(self) -> None:
        """Test creating a valid streamer schema."""
        schema = StreamerSchema(
            id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
            name="TestStreamer",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            platforms=[Platform.YOUTUBE, Platform.TWITCH],
            avatar_url=None,
            donation_tiers=[
                DonationTierSchema(
                    amount_usd=1.0,
                    popup_message="Thank you! 💙",
                    duration_ms=3000,
                )
            ],
            thank_you_message="Thanks for watching!",
        )
        assert schema.name == "TestStreamer"
        assert len(schema.platforms) == 2
        assert len(schema.donation_tiers) == 1

    def test_streamer_schema_validation_invalid_id(self) -> None:
        """Test streamer schema validation with invalid UUID."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StreamerSchema(
                id="invalid-uuid",
                name="Test",
                wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                platforms=[Platform.YOUTUBE],
                avatar_url=None,
                donation_tiers=[
                    DonationTierSchema(
                        amount_usd=1.0,
                        popup_message="Thanks",
                        duration_ms=3000,
                    )
                ],
                thank_you_message="Thank you!",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

    def test_streamer_schema_validation_invalid_wallet(self) -> None:
        """Test streamer schema validation with invalid wallet address."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StreamerSchema(
                id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
                name="Test",
                wallet_address="invalid_wallet",
                platforms=[Platform.YOUTUBE],
                avatar_url=None,
                donation_tiers=[
                    DonationTierSchema(
                        amount_usd=1.0,
                        popup_message="Thanks",
                        duration_ms=3000,
                    )
                ],
                thank_you_message="Thank you!",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("wallet_address",) for error in errors)

    def test_streamer_schema_validation_empty_platforms(self) -> None:
        """Test streamer schema validation with empty platforms list."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StreamerSchema(
                id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
                name="Test",
                wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                platforms=[],
                avatar_url=None,
                donation_tiers=[
                    DonationTierSchema(
                        amount_usd=1.0,
                        popup_message="Thanks",
                        duration_ms=3000,
                    )
                ],
                thank_you_message="Thank you!",
            )
        errors = exc_info.value.errors()
        assert any("platforms" in error["loc"] for error in errors)

    def test_streamer_schema_validation_empty_name(self) -> None:
        """Test streamer schema validation with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            _ = StreamerSchema(
                id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
                name="",
                wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                platforms=[Platform.YOUTUBE],
                avatar_url=None,
                donation_tiers=[
                    DonationTierSchema(
                        amount_usd=1.0,
                        popup_message="Thanks",
                        duration_ms=3000,
                    )
                ],
                thank_you_message="Thank you!",
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_streamer_schema_model_validate_from_dto(self, sample_streamer: Streamer) -> None:
        """Test converting Streamer DTO to StreamerSchema."""
        # Pydantic requires dict for validation, convert DTO manually
        streamer_dict = {
            "id": sample_streamer.id,
            "name": sample_streamer.name,
            "wallet_address": sample_streamer.wallet_address,
            "platforms": sample_streamer.platforms,
            "donation_tiers": [
                {
                    "amount_usd": tier.amount_usd,
                    "popup_message": tier.popup_message,
                    "duration_ms": tier.duration_ms,
                }
                for tier in sample_streamer.donation_tiers
            ],
            "thank_you_message": sample_streamer.thank_you_message,
            "avatar_url": sample_streamer.avatar_url,
        }
        schema = StreamerSchema.model_validate(streamer_dict)
        assert schema.id == sample_streamer.id
        assert schema.name == sample_streamer.name
        assert schema.wallet_address == sample_streamer.wallet_address


class TestDonationMessageCreateSchema:
    """Test DonationMessageCreateSchema Pydantic model."""

    def test_valid_donation_create_schema(self) -> None:
        """Test creating a valid donation create schema."""
        schema = DonationMessageCreateSchema(
            amount_usd=5.0,
            donor_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="Great stream!",
            clip_url=None,
        )
        assert schema.amount_usd == 5.0
        assert schema.message == "Great stream!"

    def test_donation_create_schema_validation_negative_amount(self) -> None:
        """Test validation with negative amount."""
        with pytest.raises(ValidationError) as exc_info:
            _ = DonationMessageCreateSchema(
                amount_usd=-1.0,
                donor_address="0x1234567890123456789012345678901234567890",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                message=None,
                clip_url=None,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("amount_usd",) for error in errors)

    def test_donation_create_schema_validation_invalid_wallet(self) -> None:
        """Test validation with invalid donor wallet."""
        with pytest.raises(ValidationError) as exc_info:
            _ = DonationMessageCreateSchema(
                amount_usd=5.0,
                donor_address="invalid_wallet",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                message=None,
                clip_url=None,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("donor_address",) for error in errors)

    def test_donation_create_schema_validation_invalid_tx_hash(self) -> None:
        """Test validation with invalid transaction hash."""
        with pytest.raises(ValidationError) as exc_info:
            _ = DonationMessageCreateSchema(
                amount_usd=5.0,
                donor_address="0x1234567890123456789012345678901234567890",
                tx_hash="0xinvalid",
                message=None,
                clip_url=None,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("tx_hash",) for error in errors)

    def test_donation_create_schema_validation_long_message(self) -> None:
        """Test validation with message exceeding max length."""
        with pytest.raises(ValidationError) as exc_info:
            _ = DonationMessageCreateSchema(
                amount_usd=5.0,
                donor_address="0x1234567890123456789012345678901234567890",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                message="a" * 201,  # Max length is 200
                clip_url=None,
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("message",) for error in errors)

    def test_donation_create_schema_optional_fields(self) -> None:
        """Test schema with optional fields omitted."""
        schema = DonationMessageCreateSchema(
            amount_usd=5.0,
            donor_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message=None,
            clip_url=None,
        )
        assert schema.message is None
        assert schema.clip_url is None


class TestDonationMessageSchema:
    """Test DonationMessageSchema Pydantic model."""

    def test_valid_donation_message_schema(self) -> None:
        """Test creating a valid donation message schema."""
        schema = DonationMessageSchema(
            donation_id="d1e2f3a4-b5c6-4890-9bcd-ab1234567890",
            streamer_id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
            amount_usd=5.0,
            donor_address="0x1234567890abcdef1234567890abcdef12345678",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            timestamp=1699999999,
            message="Great stream!",
            clip_url=None,
        )
        assert schema.amount_usd == 5.0
        assert schema.timestamp == 1699999999

    def test_donation_message_schema_model_validate_from_dto(
        self, sample_donation: DonationMessage
    ) -> None:
        """Test converting DonationMessage DTO to DonationMessageSchema."""
        # Pydantic requires dict for validation, convert DTO manually
        donation_dict = {
            "donation_id": sample_donation.donation_id,
            "streamer_id": sample_donation.streamer_id,
            "amount_usd": sample_donation.amount_usd,
            "donor_address": sample_donation.donor_address,
            "tx_hash": sample_donation.tx_hash,
            "timestamp": sample_donation.timestamp,
            "message": sample_donation.message,
            "clip_url": sample_donation.clip_url,
        }
        schema = DonationMessageSchema.model_validate(donation_dict)
        assert schema.donation_id == sample_donation.donation_id
        assert schema.streamer_id == sample_donation.streamer_id
        assert schema.amount_usd == sample_donation.amount_usd


class TestDonationResponseSchema:
    """Test DonationResponseSchema Pydantic model."""

    def test_valid_donation_response_schema(self) -> None:
        """Test creating a valid donation response schema."""
        schema = DonationResponseSchema(
            donation_id="d1e2f3a4-b5c6-4890-9bcd-ab1234567890",
            popup_message="Thank you! 🎉",
            duration_ms=5000,
        )
        assert schema.popup_message == "Thank you! 🎉"
        assert schema.duration_ms == 5000


class TestErrorResponseSchema:
    """Test ErrorResponseSchema Pydantic model."""

    def test_valid_error_response_schema(self) -> None:
        """Test creating a valid error response schema."""
        schema = ErrorResponseSchema(detail="Streamer not found")
        assert schema.detail == "Streamer not found"

    def test_error_response_schema_different_details(self) -> None:
        """Test error response schema with different error messages."""
        schema1 = ErrorResponseSchema(detail="Not found")
        schema2 = ErrorResponseSchema(detail="Internal server error")
        assert schema1.detail == "Not found"
        assert schema2.detail == "Internal server error"
