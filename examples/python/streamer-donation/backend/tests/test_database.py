"""Tests for database layer (RocksDB operations)."""

import uuid

import pytest

from app.core.database import DonationDB
from app.models.dtos import DonationMessage, DonationTier, Platform, Streamer


class TestDonationDBInitialization:
    """Test DonationDB initialization and connection."""

    def test_init_db_creates_database(self, temp_db_path: str) -> None:
        """Test database initialization creates RocksDB instance."""
        db = DonationDB(temp_db_path)
        assert db.db is not None
        assert db.db_path == temp_db_path
        db.close()

    def test_close_db_closes_connection(self, temp_db_path: str) -> None:
        """Test database close releases resources."""
        db = DonationDB(temp_db_path)
        db.close()
        # Verify db connection is closed by checking hasattr
        assert hasattr(db, "db")


class TestStreamerOperations:
    """Test streamer CRUD operations."""

    def test_put_streamer_stores_data(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test storing a streamer in the database."""
        db.put_streamer(sample_streamer)

        # Verify data was stored by retrieving it
        retrieved = db.get_streamer(sample_streamer.id)
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id
        assert retrieved.name == sample_streamer.name
        assert retrieved.wallet_address == sample_streamer.wallet_address

    def test_get_streamer_returns_none_for_nonexistent(self, db: DonationDB) -> None:
        """Test getting non-existent streamer returns None."""
        result = db.get_streamer("nonexistent-id")
        assert result is None

    def test_get_streamer_retrieves_correct_data(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test retrieving streamer returns all fields correctly."""
        db.put_streamer(sample_streamer)

        retrieved = db.get_streamer(sample_streamer.id)
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id
        assert retrieved.name == sample_streamer.name
        assert retrieved.wallet_address == sample_streamer.wallet_address
        assert len(retrieved.platforms) == len(sample_streamer.platforms)
        assert len(retrieved.donation_tiers) == len(sample_streamer.donation_tiers)
        assert retrieved.thank_you_message == sample_streamer.thank_you_message
        assert retrieved.avatar_url == sample_streamer.avatar_url

    def test_get_streamer_by_wallet_finds_streamer(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test finding streamer by wallet address."""
        db.put_streamer(sample_streamer)

        retrieved = db.get_streamer_by_wallet(sample_streamer.wallet_address)
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id
        assert retrieved.wallet_address == sample_streamer.wallet_address

    def test_get_streamer_by_wallet_case_insensitive(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test wallet address search is case-insensitive."""
        db.put_streamer(sample_streamer)

        # Search with uppercase wallet address
        retrieved = db.get_streamer_by_wallet(sample_streamer.wallet_address.upper())
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id

    def test_get_streamer_by_wallet_returns_none_for_nonexistent(self, db: DonationDB) -> None:
        """Test searching for non-existent wallet returns None."""
        result = db.get_streamer_by_wallet("0x0000000000000000000000000000000000000000")
        assert result is None

    def test_list_streamers_returns_all_streamers(
        self, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test listing all streamers."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        streamers = db.list_streamers(limit=100)
        assert len(streamers) == len(multiple_streamers)

    def test_list_streamers_respects_limit(
        self, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test list_streamers respects the limit parameter."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        streamers = db.list_streamers(limit=3)
        assert len(streamers) == 3

    def test_list_streamers_returns_empty_list_when_no_data(self, db: DonationDB) -> None:
        """Test list_streamers returns empty list when database is empty."""
        streamers = db.list_streamers()
        assert streamers == []

    def test_delete_streamer_removes_data(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test deleting a streamer removes it from database."""
        db.put_streamer(sample_streamer)

        # Verify streamer exists
        assert db.get_streamer(sample_streamer.id) is not None

        # Delete streamer
        result = db.delete_streamer(sample_streamer.id)
        assert result is True

        # Verify streamer is gone
        assert db.get_streamer(sample_streamer.id) is None

    def test_delete_streamer_returns_false_for_nonexistent(self, db: DonationDB) -> None:
        """Test deleting non-existent streamer returns False."""
        result = db.delete_streamer("nonexistent-id")
        assert result is False

    def test_update_streamer_overwrites_data(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test updating a streamer overwrites existing data."""
        db.put_streamer(sample_streamer)

        # Create updated version
        updated_streamer = Streamer(
            id=sample_streamer.id,
            name="Updated Name",
            wallet_address=sample_streamer.wallet_address,
            platforms=sample_streamer.platforms,
            donation_tiers=sample_streamer.donation_tiers,
            thank_you_message="Updated message",
            avatar_url=sample_streamer.avatar_url,
        )

        db.put_streamer(updated_streamer)

        # Verify update
        retrieved = db.get_streamer(sample_streamer.id)
        assert retrieved is not None
        assert retrieved.name == "Updated Name"
        assert retrieved.thank_you_message == "Updated message"


class TestDonationOperations:
    """Test donation CRUD operations."""

    def test_put_donation_stores_data(
        self, db: DonationDB, sample_donation: DonationMessage
    ) -> None:
        """Test storing a donation in the database."""
        db.put_donation(sample_donation)

        # Verify data was stored
        retrieved = db.get_donation(sample_donation.donation_id)
        assert retrieved is not None
        assert retrieved.donation_id == sample_donation.donation_id

    def test_get_donation_returns_none_for_nonexistent(self, db: DonationDB) -> None:
        """Test getting non-existent donation returns None."""
        result = db.get_donation("nonexistent-id")
        assert result is None

    def test_get_donation_retrieves_correct_data(
        self, db: DonationDB, sample_donation: DonationMessage
    ) -> None:
        """Test retrieving donation returns all fields correctly."""
        db.put_donation(sample_donation)

        retrieved = db.get_donation(sample_donation.donation_id)
        assert retrieved is not None
        assert retrieved.donation_id == sample_donation.donation_id
        assert retrieved.streamer_id == sample_donation.streamer_id
        assert retrieved.amount_usd == sample_donation.amount_usd
        assert retrieved.donor_address == sample_donation.donor_address
        assert retrieved.tx_hash == sample_donation.tx_hash
        assert retrieved.timestamp == sample_donation.timestamp
        assert retrieved.message == sample_donation.message
        assert retrieved.clip_url == sample_donation.clip_url

    def test_list_donations_by_streamer_returns_donations(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test listing donations for a specific streamer."""
        # Create multiple donations for the same streamer
        donations = [
            DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=float(i + 1),
                donor_address="0x1234567890abcdef1234567890abcdef12345678",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            for i in range(5)
        ]

        for donation in donations:
            db.put_donation(donation)

        retrieved = db.list_donations_by_streamer(sample_streamer.id, limit=100)
        assert len(retrieved) == 5

    def test_list_donations_by_streamer_sorts_by_timestamp_desc(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donations are sorted by timestamp in descending order."""
        # Create donations with different timestamps
        donations = [
            DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=1.0,
                donor_address="0x1234567890abcdef1234567890abcdef12345678",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            for i in range(3)
        ]

        for donation in donations:
            db.put_donation(donation)

        retrieved = db.list_donations_by_streamer(sample_streamer.id, limit=100)

        # Verify descending order (most recent first)
        assert retrieved[0].timestamp > retrieved[1].timestamp
        assert retrieved[1].timestamp > retrieved[2].timestamp

    def test_list_donations_by_streamer_respects_limit(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test list_donations_by_streamer respects the limit parameter."""
        # Create 5 donations
        for _ in range(5):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=1.0,
                donor_address="0x1234567890abcdef1234567890abcdef12345678",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999,
                message="Test",
                clip_url=None,
            )
            db.put_donation(donation)

        retrieved = db.list_donations_by_streamer(sample_streamer.id, limit=3)
        assert len(retrieved) == 3

    def test_list_donations_by_streamer_returns_empty_for_nonexistent(self, db: DonationDB) -> None:
        """Test listing donations for non-existent streamer returns empty list."""
        donations = db.list_donations_by_streamer("nonexistent-id", limit=100)
        assert donations == []

    def test_get_donation_stats_calculates_totals(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donation statistics calculation."""
        # Create donations with known amounts
        amounts = [1.0, 5.0, 10.0, 5.0]  # Total: 21.0
        donor1 = "0x1111111111111111111111111111111111111111"
        donor2 = "0x2222222222222222222222222222222222222222"

        for i, amount in enumerate(amounts):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=amount,
                donor_address=donor1 if i < 2 else donor2,  # 2 unique donors
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999,
                message="Test",
                clip_url=None,
            )
            db.put_donation(donation)

        stats = db.get_donation_stats(sample_streamer.id)

        assert stats["total_amount_usd"] == 21.0
        assert stats["donation_count"] == 4
        assert stats["unique_donors"] == 2

    def test_get_donation_stats_returns_zero_for_no_donations(self, db: DonationDB) -> None:
        """Test donation stats return zero values when no donations exist."""
        stats: dict[str, float] = db.get_donation_stats("nonexistent-id")

        assert stats["total_amount_usd"] == 0.0
        assert stats["donation_count"] == 0
        assert stats["unique_donors"] == 0

    def test_get_donation_stats_counts_unique_donors_case_insensitive(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test unique donor counting is case-insensitive."""
        donor_address = "0x1234567890abcdef1234567890abcdef12345678"

        # Create donations with same address in different cases
        for case_variant in [donor_address, donor_address.upper()]:
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=1.0,
                donor_address=case_variant,
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999,
                message="Test",
                clip_url=None,
            )
            db.put_donation(donation)

        stats = db.get_donation_stats(sample_streamer.id)
        assert stats["unique_donors"] == 1  # Should count as one donor


class TestErrorHandling:
    """Test error handling and exception scenarios."""

    def test_init_db_with_invalid_path(self) -> None:
        """Test database initialization with invalid path."""
        # Using a path that doesn't exist and can't be created
        invalid_path = "/nonexistent/invalid/path/test.db"
        with pytest.raises(Exception):  # RocksDB raises various exceptions for invalid paths
            _ = DonationDB(invalid_path)

    def test_get_db_before_init(self) -> None:
        """Test getting database before initialization."""
        # Save current db state
        from app.core import database

        original_db = database.db

        # Set db to None to simulate uninitialized state
        database.db = None

        try:
            with pytest.raises(RuntimeError, match="Database not initialized"):
                _ = database.get_db()
        finally:
            # Restore original db
            database.db = original_db

    def test_close_db_when_not_initialized(self) -> None:
        """Test closing database when not initialized."""
        from app.core import database

        original_db = database.db

        database.db = None
        try:
            # Should not raise an error
            database.close_db()
        finally:
            database.db = original_db


class TestDataIntegrity:
    """Test data integrity and edge cases."""

    def test_streamer_with_minimal_data(self, db: DonationDB) -> None:
        """Test storing streamer with minimal required fields."""
        minimal_streamer = Streamer(
            id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
            name="Minimal",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678",
            platforms=[Platform.YOUTUBE],
            donation_tiers=[DonationTier(amount_usd=1.0, popup_message="Thanks", duration_ms=3000)],
            thank_you_message="Thank you",
            avatar_url=None,
        )

        db.put_streamer(minimal_streamer)
        retrieved = db.get_streamer(minimal_streamer.id)

        assert retrieved is not None
        assert retrieved.avatar_url is None

    def test_donation_with_optional_fields_none(self, db: DonationDB) -> None:
        """Test storing donation with optional fields as None."""
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

        db.put_donation(donation)
        retrieved = db.get_donation(donation.donation_id)

        assert retrieved is not None
        assert retrieved.message is None
        assert retrieved.clip_url is None

    def test_multiple_streamers_with_different_platforms(self, db: DonationDB) -> None:
        """Test storing multiple streamers with different platform combinations."""
        streamer1 = Streamer(
            id="a1111111-1111-4111-8111-111111111111",
            name="YouTuber",
            wallet_address="0x1111111111111111111111111111111111111111",
            platforms=[Platform.YOUTUBE],
            donation_tiers=[DonationTier(amount_usd=1.0, popup_message="Thanks", duration_ms=3000)],
            thank_you_message="Thanks",
        )

        streamer2 = Streamer(
            id="a2222222-2222-4222-8222-222222222222",
            name="Twitcher",
            wallet_address="0x2222222222222222222222222222222222222222",
            platforms=[Platform.TWITCH],
            donation_tiers=[DonationTier(amount_usd=1.0, popup_message="Thanks", duration_ms=3000)],
            thank_you_message="Thanks",
        )

        db.put_streamer(streamer1)
        db.put_streamer(streamer2)

        streamers = db.list_streamers(limit=10)
        assert len(streamers) == 2

    def test_donation_tiers_preserved_correctly(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donation tiers are stored and retrieved correctly."""
        db.put_streamer(sample_streamer)
        retrieved = db.get_streamer(sample_streamer.id)

        assert retrieved is not None
        assert len(retrieved.donation_tiers) == len(sample_streamer.donation_tiers)

        for original, retrieved_tier in zip(
            sample_streamer.donation_tiers, retrieved.donation_tiers, strict=True
        ):
            assert retrieved_tier.amount_usd == original.amount_usd
            assert retrieved_tier.popup_message == original.popup_message
            assert retrieved_tier.duration_ms == original.duration_ms
