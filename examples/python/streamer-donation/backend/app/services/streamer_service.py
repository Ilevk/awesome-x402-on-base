"""
Streamer service for business logic related to streamer operations.

This service encapsulates all streamer-related business logic including
retrieval, validation, and tier matching.
"""

import logging
from typing import Optional

from app.core.database import DonationDB
from app.models.dtos import DonationTier, Streamer

logger = logging.getLogger(__name__)


class StreamerService:
    """Service for managing streamer-related business logic."""

    def __init__(self, db: DonationDB):
        """
        Initialize streamer service with database instance.

        Args:
            db: DonationDB instance for data access
        """
        self.db = db

    def get_streamer_by_id(self, streamer_id: str) -> Optional[Streamer]:
        """
        Retrieve streamer by unique ID.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Streamer model if found, None otherwise
        """
        return self.db.get_streamer(streamer_id)

    def get_streamer_by_wallet(self, wallet_address: str) -> Optional[Streamer]:
        """
        Retrieve streamer by wallet address.

        Args:
            wallet_address: Ethereum wallet address (0x...)

        Returns:
            Streamer model if found, None otherwise
        """
        return self.db.get_streamer_by_wallet(wallet_address)

    def list_streamers(self, limit: int = 100) -> list[Streamer]:
        """
        List all streamers with optional limit.

        Args:
            limit: Maximum number of streamers to return (default: 100, max: 1000)

        Returns:
            List of Streamer models
        """
        # Enforce maximum limit
        if limit > 1000:
            limit = 1000

        return self.db.list_streamers(limit=limit)

    def find_matching_tier(
        self, streamer: Streamer, amount_usd: float, tolerance: float = 0.01
    ) -> Optional[DonationTier]:
        """
        Find donation tier that matches the given amount.

        Uses floating point tolerance for comparison to handle
        potential precision issues.

        Args:
            streamer: Streamer whose tiers to search
            amount_usd: Donation amount to match
            tolerance: Floating point comparison tolerance (default: 0.01)

        Returns:
            Matching DonationTier if found, None otherwise

        Example:
            >>> tier = service.find_matching_tier(streamer, 5.0)
            >>> tier.popup_message
            'Amazing support! 🎉'
        """
        for tier in streamer.donation_tiers:
            if abs(tier.amount_usd - amount_usd) < tolerance:
                logger.debug(
                    f"Matched tier: ${tier.amount_usd} for donation ${amount_usd} "
                    f"(streamer: {streamer.name})"
                )
                return tier

        logger.warning(
            f"No matching tier for amount ${amount_usd} "
            f"(streamer: {streamer.name}, available tiers: "
            f"{[t.amount_usd for t in streamer.donation_tiers]})"
        )
        return None

    def validate_streamer_active(self, streamer: Streamer) -> tuple[bool, Optional[str]]:
        """
        Validate that streamer is active and accepting donations.

        Currently all streamers are considered active, but this method
        provides extensibility for future status management.

        Args:
            streamer: Streamer to validate

        Returns:
            Tuple of (is_active, error_message)
            - is_active: True if streamer can accept donations
            - error_message: None if active, error description if inactive
        """
        # Future extension: Check streamer status, suspension, etc.
        # For Phase 1, all streamers are active
        return (True, None)

    def get_available_tier_amounts(self, streamer: Streamer) -> list[float]:
        """
        Get list of all available donation amounts for a streamer.

        Useful for displaying options to users.

        Args:
            streamer: Streamer whose tiers to extract

        Returns:
            List of donation amounts in USD
        """
        return [tier.amount_usd for tier in streamer.donation_tiers]
