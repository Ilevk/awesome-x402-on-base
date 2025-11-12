"""
Streamer service for business logic related to streamer operations.

This service encapsulates all streamer-related business logic including
retrieval, validation, tier matching, and creation.
"""

import logging
import uuid

from app.core.database import DonationDB
from app.models.dtos import DonationTier, Platform, Streamer

logger = logging.getLogger(__name__)


class StreamerService:
    """Service for managing streamer-related business logic."""

    def __init__(self, db: DonationDB) -> None:
        """
        Initialize streamer service with database instance.

        Args:
            db: DonationDB instance for data access
        """
        self.db = db

    def create_streamer(
        self,
        name: str,
        wallet_address: str,
        platforms: list[Platform],
        donation_tiers: list[dict[str, float | str | int]],
        avatar_url: str | None = None,
        thank_you_message: str = "Thank you for your support!",
    ) -> Streamer:
        """
        Create a new streamer with donation tiers.

        Args:
            name: Streamer display name
            wallet_address: Ethereum wallet address (must be unique)
            platforms: List of streaming platforms
            donation_tiers: List of tier configs (amount_usd, popup_message, duration_ms)
            avatar_url: Optional profile image URL
            thank_you_message: Custom thank you message

        Returns:
            Created Streamer model with generated UUID

        Raises:
            ValueError: If validation fails (duplicate wallet, invalid tiers, etc.)

        Example:
            >>> streamer = service.create_streamer(
            ...     name="Logan",
            ...     wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            ...     platforms=[Platform.YOUTUBE, Platform.TWITCH],
            ...     donation_tiers=[
            ...         {"amount_usd": 1.0, "popup_message": "Thank you! 💙", "duration_ms": 3000},
            ...         {"amount_usd": 5.0, "popup_message": "Amazing! 🎉", "duration_ms": 5000},
            ...     ]
            ... )
        """
        # Generate UUID for new streamer
        streamer_id = str(uuid.uuid4())

        # Validate wallet address uniqueness (already checked in route, but double-check)
        if self.db.get_streamer_by_wallet(wallet_address):
            raise ValueError(f"Wallet address {wallet_address} is already registered")

        # Convert donation tier dicts to DonationTier objects
        tier_objects = [
            DonationTier(
                amount_usd=float(tier["amount_usd"]),
                popup_message=str(tier["popup_message"]),
                duration_ms=int(tier.get("duration_ms", 3000)),
            )
            for tier in donation_tiers
        ]

        # Validate tier amounts are unique
        amounts = [tier.amount_usd for tier in tier_objects]
        if len(amounts) != len(set(amounts)):
            raise ValueError("Donation tier amounts must be unique")

        # Validate tier amounts are sorted ascending
        if amounts != sorted(amounts):
            raise ValueError("Donation tiers must be sorted by amount in ascending order")

        # Create Streamer DTO
        streamer = Streamer(
            id=streamer_id,
            name=name,
            wallet_address=wallet_address,
            platforms=platforms,
            avatar_url=avatar_url,
            donation_tiers=tier_objects,
            thank_you_message=thank_you_message,
        )

        # Save to database
        self.db.put_streamer(streamer)

        logger.info(
            f"Created streamer: {name} ({streamer_id}) with {len(tier_objects)} tiers"
        )

        return streamer

    def get_streamer_by_id(self, streamer_id: str) -> Streamer | None:
        """
        Retrieve streamer by unique ID.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Streamer model if found, None otherwise
        """
        return self.db.get_streamer(streamer_id)

    def get_streamer_by_wallet(self, wallet_address: str) -> Streamer | None:
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
    ) -> DonationTier | None:
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

    def validate_streamer_active(self, streamer: Streamer) -> tuple[bool, str | None]:
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
