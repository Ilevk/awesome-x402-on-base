"""Tests for service layer."""

import uuid
from unittest.mock import patch

import pytest
from pydantic import HttpUrl

from app.core.database import DonationDB
from app.models.dtos import DonationMessage, Streamer
from app.models.schemas import DonationMessageCreateSchema
from app.services.donation_service import DonationService
from app.services.streamer_service import StreamerService
from app.services.validation_service import ValidationService


class TestValidationService:
    """Test validation service operations."""

    def test_validate_wallet_address_valid(self) -> None:
        """Test validation of valid Ethereum address."""
        service = ValidationService()
        address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        assert service.validate_wallet_address(address) is True

    def test_validate_wallet_address_invalid(self) -> None:
        """Test validation of invalid address format."""
        service = ValidationService()
        assert service.validate_wallet_address("invalid") is False
        assert service.validate_wallet_address("") is False
        assert service.validate_wallet_address("0x123") is False

    def test_validate_wallet_address_exception_handling(self) -> None:
        """Test validation handles exceptions gracefully."""
        service = ValidationService()
        # Test with None - should not raise
        assert service.validate_wallet_address(None) is False  # type: ignore

    def test_sanitize_message_removes_html(self) -> None:
        """Test sanitization removes HTML tags."""
        service = ValidationService()
        result = service.sanitize_message("<script>alert('xss')</script>Hello")
        # bleach.clean() removes tags but keeps content
        assert result == "alert('xss')Hello"

    def test_sanitize_message_trims_length(self) -> None:
        """Test sanitization respects max length."""
        service = ValidationService()
        long_message = "a" * 300
        result = service.sanitize_message(long_message, max_length=200)
        assert result is not None
        assert len(result) == 200

    def test_sanitize_message_strips_whitespace(self) -> None:
        """Test sanitization strips whitespace."""
        service = ValidationService()
        result = service.sanitize_message("   Hello World   ")
        assert result == "Hello World"

    def test_sanitize_message_returns_none_for_empty(self) -> None:
        """Test sanitization returns None for empty strings."""
        service = ValidationService()
        assert service.sanitize_message(None) is None
        assert service.sanitize_message("") is None
        assert service.sanitize_message("   ") is None

    def test_sanitize_message_returns_none_after_cleaning(self) -> None:
        """Test sanitization returns None if empty after HTML removal."""
        service = ValidationService()
        result = service.sanitize_message("<div></div>")
        assert result is None

    def test_validate_amount_range_valid(self) -> None:
        """Test amount validation for valid amounts."""
        service = ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)
        is_valid, error = service.validate_amount_range(5.0)
        assert is_valid is True
        assert error is None

    def test_validate_amount_range_too_small(self) -> None:
        """Test amount validation rejects amounts below minimum."""
        service = ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)
        is_valid, error = service.validate_amount_range(0.001)
        assert is_valid is False
        assert error == "Donation amount must be at least $0.01"

    def test_validate_amount_range_too_large(self) -> None:
        """Test amount validation rejects amounts above maximum."""
        service = ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)
        is_valid, error = service.validate_amount_range(2000.0)
        assert is_valid is False
        assert error == "Donation amount cannot exceed $1000.00"

    def test_validate_amount_range_at_boundaries(self) -> None:
        """Test amount validation at min/max boundaries."""
        service = ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)

        # Exactly at minimum
        is_valid, error = service.validate_amount_range(0.01)
        assert is_valid is True
        assert error is None

        # Exactly at maximum
        is_valid, error = service.validate_amount_range(1000.0)
        assert is_valid is True
        assert error is None

    def test_validate_donation_tier_match_exact(self) -> None:
        """Test tier matching with exact amount."""
        service = ValidationService()
        tier_amounts = [1.0, 5.0, 10.0]

        is_match, tier_idx = service.validate_donation_tier_match(5.0, tier_amounts)
        assert is_match is True
        assert tier_idx == 1

    def test_validate_donation_tier_match_tolerance(self) -> None:
        """Test tier matching within tolerance."""
        service = ValidationService()
        tier_amounts = [1.0, 5.0, 10.0]

        # Within default tolerance (0.01)
        is_match, tier_idx = service.validate_donation_tier_match(5.009, tier_amounts)
        assert is_match is True
        assert tier_idx == 1

    def test_validate_donation_tier_match_no_match(self) -> None:
        """Test tier matching returns false when no match."""
        service = ValidationService()
        tier_amounts = [1.0, 5.0, 10.0]

        is_match, tier_idx = service.validate_donation_tier_match(7.5, tier_amounts)
        assert is_match is False
        assert tier_idx is None

    def test_validate_donation_tier_match_custom_tolerance(self) -> None:
        """Test tier matching with custom tolerance."""
        service = ValidationService()
        tier_amounts = [1.0, 5.0, 10.0]

        # Just outside default tolerance but inside custom
        is_match, tier_idx = service.validate_donation_tier_match(5.05, tier_amounts, tolerance=0.1)
        assert is_match is True
        assert tier_idx == 1


class TestStreamerService:
    """Test streamer service operations."""

    def test_get_streamer_by_id(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test retrieving streamer by ID."""
        db.put_streamer(sample_streamer)
        service = StreamerService(db)

        result = service.get_streamer_by_id(sample_streamer.id)
        assert result is not None
        assert result.id == sample_streamer.id

    def test_get_streamer_by_id_not_found(self, db: DonationDB) -> None:
        """Test retrieving non-existent streamer returns None."""
        service = StreamerService(db)
        result = service.get_streamer_by_id("nonexistent-id")
        assert result is None

    def test_get_streamer_by_wallet(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test retrieving streamer by wallet address."""
        db.put_streamer(sample_streamer)
        service = StreamerService(db)

        result = service.get_streamer_by_wallet(sample_streamer.wallet_address)
        assert result is not None
        assert result.wallet_address == sample_streamer.wallet_address

    def test_get_streamer_by_wallet_not_found(self, db: DonationDB) -> None:
        """Test retrieving streamer by non-existent wallet returns None."""
        service = StreamerService(db)
        result = service.get_streamer_by_wallet("0x0000000000000000000000000000000000000000")
        assert result is None

    def test_list_streamers(self, db: DonationDB, multiple_streamers: list[Streamer]) -> None:
        """Test listing all streamers."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        service = StreamerService(db)
        streamers = service.list_streamers(limit=100)
        assert len(streamers) == len(multiple_streamers)

    def test_list_streamers_respects_limit(
        self, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test list_streamers respects the limit parameter."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        service = StreamerService(db)
        streamers = service.list_streamers(limit=3)
        assert len(streamers) == 3

    def test_list_streamers_enforces_max_limit(
        self, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test list_streamers enforces maximum limit of 1000."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        service = StreamerService(db)
        # Request more than 1000, should be capped
        streamers = service.list_streamers(limit=5000)
        # We only have 5 streamers, so should get all 5
        assert len(streamers) == len(multiple_streamers)

    def test_find_matching_tier_exact_match(self, sample_streamer: Streamer) -> None:
        """Test finding tier with exact amount match."""
        service = StreamerService(db=None)  # type: ignore

        tier = service.find_matching_tier(sample_streamer, 5.0)
        assert tier is not None
        assert tier.amount_usd == 5.0

    def test_find_matching_tier_within_tolerance(self, sample_streamer: Streamer) -> None:
        """Test finding tier within tolerance."""
        service = StreamerService(db=None)  # type: ignore

        tier = service.find_matching_tier(sample_streamer, 5.009)
        assert tier is not None
        assert tier.amount_usd == 5.0

    def test_find_matching_tier_no_match(self, sample_streamer: Streamer) -> None:
        """Test finding tier returns None when no match."""
        service = StreamerService(db=None)  # type: ignore

        tier = service.find_matching_tier(sample_streamer, 7.5)
        assert tier is None

    def test_find_matching_tier_custom_tolerance(self, sample_streamer: Streamer) -> None:
        """Test finding tier with custom tolerance."""
        service = StreamerService(db=None)  # type: ignore

        # Just outside default tolerance but inside custom
        tier = service.find_matching_tier(sample_streamer, 5.05, tolerance=0.1)
        assert tier is not None
        assert tier.amount_usd == 5.0

    def test_validate_streamer_active(self, sample_streamer: Streamer) -> None:
        """Test streamer active validation."""
        service = StreamerService(db=None)  # type: ignore

        is_active, error = service.validate_streamer_active(sample_streamer)
        assert is_active is True
        assert error is None

    def test_get_available_tier_amounts(self, sample_streamer: Streamer) -> None:
        """Test getting available tier amounts."""
        service = StreamerService(db=None)  # type: ignore

        amounts = service.get_available_tier_amounts(sample_streamer)
        assert len(amounts) == len(sample_streamer.donation_tiers)
        assert 1.0 in amounts
        assert 5.0 in amounts
        assert 10.0 in amounts


class TestDonationService:
    """Test donation service operations."""

    @pytest.fixture
    def validation_service(self) -> ValidationService:
        """Create validation service instance."""
        return ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)

    @pytest.fixture
    def streamer_service(self, db: DonationDB) -> StreamerService:
        """Create streamer service instance."""
        return StreamerService(db)

    @pytest.fixture
    def donation_service(
        self,
        db: DonationDB,
        validation_service: ValidationService,
        streamer_service: StreamerService,
    ) -> DonationService:
        """Create donation service instance."""
        return DonationService(db, validation_service, streamer_service)

    def test_process_donation_success(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test successful donation processing."""
        db.put_streamer(sample_streamer)

        donation_data = DonationMessageCreateSchema(
            amount_usd=5.0,
            donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="Great stream!",
            clip_url=None,
        )

        with patch("time.time", return_value=1699999999):
            response = donation_service.process_donation(sample_streamer.id, donation_data)

        assert response.donation_id is not None
        assert response.popup_message == "Amazing! 🎉"
        assert response.duration_ms == 5000

        # Verify donation was stored
        stored = db.get_donation(response.donation_id)
        assert stored is not None
        assert stored.amount_usd == 5.0
        assert stored.donor_address == donation_data.donor_address

    def test_process_donation_streamer_not_found(self, donation_service: DonationService) -> None:
        """Test donation processing fails when streamer not found."""
        donation_data = DonationMessageCreateSchema(
            amount_usd=5.0,
            donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="Test",
            clip_url=None,
        )

        with pytest.raises(ValueError, match="Streamer not found"):
            donation_service.process_donation("nonexistent-id", donation_data)

    def test_process_donation_invalid_donor_address(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test donation processing fails with invalid donor address."""
        from pydantic import ValidationError

        db.put_streamer(sample_streamer)

        # Pydantic validates before service validation
        with pytest.raises(ValidationError):
            DonationMessageCreateSchema(
                amount_usd=5.0,
                donor_address="invalid_address",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                message="Test",
                clip_url=None,
            )

    def test_process_donation_invalid_amount_too_small(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test donation processing fails with amount below minimum."""
        db.put_streamer(sample_streamer)

        donation_data = DonationMessageCreateSchema(
            amount_usd=0.001,
            donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="Test",
            clip_url=None,
        )

        with pytest.raises(ValueError, match="Donation amount must be at least"):
            donation_service.process_donation(sample_streamer.id, donation_data)

    def test_process_donation_invalid_amount_too_large(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test donation processing fails with amount above maximum."""
        from pydantic import ValidationError

        db.put_streamer(sample_streamer)

        # Pydantic validates before service validation
        with pytest.raises(ValidationError):
            DonationMessageCreateSchema(
                amount_usd=2000.0,
                donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                message="Test",
                clip_url=None,
            )

    def test_process_donation_no_matching_tier(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test donation processing fails when no tier matches amount."""
        db.put_streamer(sample_streamer)

        donation_data = DonationMessageCreateSchema(
            amount_usd=7.5,  # Not a valid tier amount
            donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="Test",
            clip_url=None,
        )

        with pytest.raises(ValueError, match="Invalid donation amount"):
            donation_service.process_donation(sample_streamer.id, donation_data)

    def test_process_donation_sanitizes_message(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test donation processing sanitizes user message."""
        db.put_streamer(sample_streamer)

        donation_data = DonationMessageCreateSchema(
            amount_usd=5.0,
            donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="<script>alert('xss')</script>Clean message",
            clip_url=None,
        )

        with patch("time.time", return_value=1699999999):
            response = donation_service.process_donation(sample_streamer.id, donation_data)

        stored = db.get_donation(response.donation_id)
        assert stored is not None
        # bleach.clean() removes tags but keeps content
        assert stored.message == "alert('xss')Clean message"
        assert "<script>" not in stored.message

    def test_process_donation_handles_clip_url(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test donation processing handles clip URL."""
        db.put_streamer(sample_streamer)

        clip_url = HttpUrl("https://clips.twitch.tv/example")
        donation_data = DonationMessageCreateSchema(
            amount_usd=5.0,
            donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            message="Amazing moment!",
            clip_url=clip_url,
        )

        with patch("time.time", return_value=1699999999):
            response = donation_service.process_donation(sample_streamer.id, donation_data)

        stored = db.get_donation(response.donation_id)
        assert stored is not None
        assert stored.clip_url == str(clip_url)

    def test_get_donation_by_id(
        self, db: DonationDB, donation_service: DonationService, sample_donation: DonationMessage
    ) -> None:
        """Test retrieving donation by ID."""
        db.put_donation(sample_donation)

        result = donation_service.get_donation_by_id(sample_donation.donation_id)
        assert result is not None
        assert result.donation_id == sample_donation.donation_id

    def test_get_donation_by_id_not_found(self, donation_service: DonationService) -> None:
        """Test retrieving non-existent donation returns None."""
        result = donation_service.get_donation_by_id("nonexistent-id")
        assert result is None

    def test_list_donations_for_streamer(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test listing donations for a streamer."""
        db.put_streamer(sample_streamer)

        # Create multiple donations
        for i in range(3):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=5.0,
                donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            db.put_donation(donation)

        donations = donation_service.list_donations_for_streamer(sample_streamer.id)
        assert len(donations) == 3

    def test_list_donations_for_streamer_respects_limit(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test listing donations respects limit parameter."""
        db.put_streamer(sample_streamer)

        # Create 5 donations
        for i in range(5):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=5.0,
                donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            db.put_donation(donation)

        donations = donation_service.list_donations_for_streamer(sample_streamer.id, limit=3)
        assert len(donations) == 3

    def test_list_donations_for_streamer_enforces_max_limit(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test listing donations enforces maximum limit of 1000."""
        db.put_streamer(sample_streamer)

        # Create 3 donations
        for i in range(3):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=5.0,
                donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            db.put_donation(donation)

        # Request more than 1000, should be capped
        donations = donation_service.list_donations_for_streamer(sample_streamer.id, limit=5000)
        # We only have 3 donations, so should get all 3
        assert len(donations) == 3

    def test_get_donation_stats(
        self,
        db: DonationDB,
        donation_service: DonationService,
        sample_streamer: Streamer,
    ) -> None:
        """Test getting donation statistics."""
        db.put_streamer(sample_streamer)

        # Create donations with known amounts
        amounts = [1.0, 5.0, 10.0, 5.0]  # Total: 21.0
        donor1 = "0x1111111111111111111111111111111111111111"
        donor2 = "0x2222222222222222222222222222222222222222"

        for i, amount in enumerate(amounts):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=amount,
                donor_address=donor1 if i < 2 else donor2,
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999,
                message="Test",
                clip_url=None,
            )
            db.put_donation(donation)

        stats = donation_service.get_donation_stats(sample_streamer.id)

        assert stats["total_amount_usd"] == 21.0
        assert stats["donation_count"] == 4
        assert stats["unique_donors"] == 2

    def test_get_donation_stats_no_donations(self, donation_service: DonationService) -> None:
        """Test donation stats return zero values when no donations exist."""
        stats = donation_service.get_donation_stats("nonexistent-id")

        assert stats["total_amount_usd"] == 0.0
        assert stats["donation_count"] == 0
        assert stats["unique_donors"] == 0
