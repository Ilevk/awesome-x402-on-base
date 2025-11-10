"""
Repository for donation data access.

Provides abstraction layer over database operations for donations.
"""

import logging

from app.core.database import DonationDB
from app.models.dtos import DonationMessage

logger = logging.getLogger(__name__)


class DonationRepository:
    """Repository for managing donation data access."""

    def __init__(self, db: DonationDB) -> None:
        """
        Initialize repository with database instance.

        Args:
            db: DonationDB instance for data access
        """
        self.db = db

    def get_by_id(self, donation_id: str) -> DonationMessage | None:
        """
        Retrieve donation by unique ID.

        Args:
            donation_id: UUID4 donation identifier

        Returns:
            DonationMessage if found, None otherwise
        """
        return self.db.get_donation(donation_id)

    def list_by_streamer(self, streamer_id: str, limit: int = 100) -> list[DonationMessage]:
        """
        List donations for a specific streamer.

        Args:
            streamer_id: UUID4 streamer identifier
            limit: Maximum number of donations to return

        Returns:
            List of DonationMessage models sorted by timestamp descending
        """
        return self.db.list_donations_by_streamer(streamer_id, limit=limit)

    def save(self, donation: DonationMessage) -> None:
        """
        Save donation to database.

        Args:
            donation: DonationMessage model to save
        """
        self.db.put_donation(donation)
        logger.debug(
            f"Saved donation: {donation.donation_id} "
            f"(${donation.amount_usd} to {donation.streamer_id})"
        )

    def get_stats(self, streamer_id: str) -> dict:
        """
        Get donation statistics for a streamer.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Dictionary with total_amount_usd, donation_count, unique_donors
        """
        return self.db.get_donation_stats(streamer_id)

    def exists(self, donation_id: str) -> bool:
        """
        Check if donation exists by ID.

        Args:
            donation_id: UUID4 donation identifier

        Returns:
            True if donation exists, False otherwise
        """
        return self.get_by_id(donation_id) is not None
