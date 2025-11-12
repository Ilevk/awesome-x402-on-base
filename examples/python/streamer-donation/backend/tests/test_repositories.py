"""Tests for repository layer."""

import uuid

from app.core.database import DonationDB
from app.models.dtos import DonationMessage, Streamer
from app.repositories.donation_repository import DonationRepository
from app.repositories.streamer_repository import StreamerRepository


class TestStreamerRepository:
    """Test streamer repository operations."""

    def test_save_streamer(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test saving a new streamer."""
        repo = StreamerRepository(db)
        repo.save(sample_streamer)

        retrieved = repo.get_by_id(sample_streamer.id)
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id
        assert retrieved.name == sample_streamer.name
        assert retrieved.wallet_address == sample_streamer.wallet_address

    def test_get_streamer_by_id(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test retrieving streamer by ID."""
        repo = StreamerRepository(db)
        repo.save(sample_streamer)

        retrieved = repo.get_by_id(sample_streamer.id)
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id

    def test_get_streamer_by_id_not_found(self, db: DonationDB) -> None:
        """Test retrieving non-existent streamer returns None."""
        repo = StreamerRepository(db)
        result = repo.get_by_id("nonexistent-id")
        assert result is None

    def test_get_streamer_by_wallet(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test retrieving streamer by wallet address."""
        repo = StreamerRepository(db)
        repo.save(sample_streamer)

        retrieved = repo.get_by_wallet(sample_streamer.wallet_address)
        assert retrieved is not None
        assert retrieved.wallet_address == sample_streamer.wallet_address

    def test_get_streamer_by_wallet_case_insensitive(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test wallet address search is case-insensitive."""
        repo = StreamerRepository(db)
        repo.save(sample_streamer)

        retrieved = repo.get_by_wallet(sample_streamer.wallet_address.upper())
        assert retrieved is not None
        assert retrieved.id == sample_streamer.id

    def test_get_streamer_by_wallet_not_found(self, db: DonationDB) -> None:
        """Test retrieving streamer by non-existent wallet returns None."""
        repo = StreamerRepository(db)
        result = repo.get_by_wallet("0x0000000000000000000000000000000000000000")
        assert result is None

    def test_list_streamers(
        self, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test listing all streamers."""
        repo = StreamerRepository(db)
        for streamer in multiple_streamers:
            repo.save(streamer)

        streamers = repo.list_all(limit=100)
        assert len(streamers) == len(multiple_streamers)

    def test_list_streamers_respects_limit(
        self, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test list_all respects the limit parameter."""
        repo = StreamerRepository(db)
        for streamer in multiple_streamers:
            repo.save(streamer)

        streamers = repo.list_all(limit=3)
        assert len(streamers) == 3

    def test_list_streamers_empty_database(self, db: DonationDB) -> None:
        """Test listing streamers from empty database."""
        repo = StreamerRepository(db)
        streamers = repo.list_all()
        assert streamers == []

    def test_update_streamer(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test updating a streamer using save method."""
        repo = StreamerRepository(db)
        repo.save(sample_streamer)

        # Create updated version
        updated = Streamer(
            id=sample_streamer.id,
            name="Updated Name",
            wallet_address=sample_streamer.wallet_address,
            platforms=sample_streamer.platforms,
            donation_tiers=sample_streamer.donation_tiers,
            thank_you_message="Updated message",
            avatar_url=sample_streamer.avatar_url,
        )

        repo.save(updated)
        result = repo.get_by_id(sample_streamer.id)
        assert result is not None
        assert result.name == "Updated Name"
        assert result.thank_you_message == "Updated message"

    def test_exists_returns_true_for_existing_streamer(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test exists returns True for existing streamer."""
        repo = StreamerRepository(db)
        repo.save(sample_streamer)

        assert repo.exists(sample_streamer.id) is True

    def test_exists_returns_false_for_nonexistent_streamer(self, db: DonationDB) -> None:
        """Test exists returns False for non-existent streamer."""
        repo = StreamerRepository(db)
        assert repo.exists("nonexistent-id") is False


class TestDonationRepository:
    """Test donation repository operations."""

    def test_save_donation(
        self, db: DonationDB, sample_donation: DonationMessage
    ) -> None:
        """Test saving a new donation."""
        repo = DonationRepository(db)
        repo.save(sample_donation)

        retrieved = repo.get_by_id(sample_donation.donation_id)
        assert retrieved is not None
        assert retrieved.donation_id == sample_donation.donation_id
        assert retrieved.streamer_id == sample_donation.streamer_id
        assert retrieved.amount_usd == sample_donation.amount_usd

    def test_get_donation_by_id(
        self, db: DonationDB, sample_donation: DonationMessage
    ) -> None:
        """Test retrieving donation by ID."""
        repo = DonationRepository(db)
        repo.save(sample_donation)

        retrieved = repo.get_by_id(sample_donation.donation_id)
        assert retrieved is not None
        assert retrieved.donation_id == sample_donation.donation_id

    def test_get_donation_by_id_not_found(self, db: DonationDB) -> None:
        """Test retrieving non-existent donation returns None."""
        repo = DonationRepository(db)
        result = repo.get_by_id("nonexistent-id")
        assert result is None

    def test_list_donations_by_streamer(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test listing donations for a specific streamer."""
        repo = DonationRepository(db)

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
            repo.save(donation)

        retrieved = repo.list_by_streamer(sample_streamer.id, limit=100)
        assert len(retrieved) == 5

    def test_list_donations_by_streamer_sorts_by_timestamp(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donations are sorted by timestamp in descending order."""
        repo = DonationRepository(db)

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
            repo.save(donation)

        retrieved = repo.list_by_streamer(sample_streamer.id, limit=100)

        # Verify descending order (most recent first)
        assert retrieved[0].timestamp > retrieved[1].timestamp
        assert retrieved[1].timestamp > retrieved[2].timestamp

    def test_list_donations_by_streamer_respects_limit(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test list_by_streamer respects the limit parameter."""
        repo = DonationRepository(db)

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
            repo.save(donation)

        retrieved = repo.list_by_streamer(sample_streamer.id, limit=3)
        assert len(retrieved) == 3

    def test_list_donations_by_streamer_empty(self, db: DonationDB) -> None:
        """Test listing donations for non-existent streamer returns empty list."""
        repo = DonationRepository(db)
        donations = repo.list_by_streamer("nonexistent-id", limit=100)
        assert donations == []

    def test_get_donation_stats(self, db: DonationDB, sample_streamer: Streamer) -> None:
        """Test getting donation statistics."""
        repo = DonationRepository(db)

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
            repo.save(donation)

        stats = repo.get_stats(sample_streamer.id)

        assert stats["total_amount_usd"] == 21.0
        assert stats["donation_count"] == 4
        assert stats["unique_donors"] == 2

    def test_get_donation_stats_no_donations(self, db: DonationDB) -> None:
        """Test donation stats return zero values when no donations exist."""
        repo = DonationRepository(db)
        stats = repo.get_stats("nonexistent-id")

        assert stats["total_amount_usd"] == 0.0
        assert stats["donation_count"] == 0
        assert stats["unique_donors"] == 0

    def test_get_donation_stats_case_insensitive_donors(
        self, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test unique donor counting is case-insensitive."""
        repo = DonationRepository(db)
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
            repo.save(donation)

        stats = repo.get_stats(sample_streamer.id)
        assert stats["unique_donors"] == 1  # Should count as one donor

    def test_exists_returns_true_for_existing_donation(
        self, db: DonationDB, sample_donation: DonationMessage
    ) -> None:
        """Test exists returns True for existing donation."""
        repo = DonationRepository(db)
        repo.save(sample_donation)

        assert repo.exists(sample_donation.donation_id) is True

    def test_exists_returns_false_for_nonexistent_donation(self, db: DonationDB) -> None:
        """Test exists returns False for non-existent donation."""
        repo = DonationRepository(db)
        assert repo.exists("nonexistent-id") is False
