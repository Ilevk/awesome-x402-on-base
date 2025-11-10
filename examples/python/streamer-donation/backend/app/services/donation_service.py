"""
Donation service for business logic related to donation operations.

This service encapsulates donation processing, validation, and statistics.
"""

import logging
import time
import uuid
from typing import Optional

from app.core.database import DonationDB
from app.models.dtos import DonationMessage, Streamer
from app.models.schemas import DonationMessageCreateSchema, DonationResponseSchema
from app.services.streamer_service import StreamerService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class DonationService:
    """Service for managing donation-related business logic."""

    def __init__(
        self,
        db: DonationDB,
        validation_service: ValidationService,
        streamer_service: StreamerService,
    ):
        """
        Initialize donation service with dependencies.

        Args:
            db: DonationDB instance for data access
            validation_service: ValidationService for input validation
            streamer_service: StreamerService for streamer operations
        """
        self.db = db
        self.validation_service = validation_service
        self.streamer_service = streamer_service

    def process_donation(
        self, streamer_id: str, donation_data: DonationMessageCreateSchema
    ) -> DonationResponseSchema:
        """
        Process a donation submission with full validation.

        This is the core business logic for handling donations:
        1. Validate streamer exists and is active
        2. Validate donor and streamer wallet addresses
        3. Validate donation amount is within range
        4. Find matching donation tier
        5. Sanitize user message
        6. Create donation record
        7. Return popup configuration

        Args:
            streamer_id: UUID4 streamer identifier
            donation_data: Donation details from request

        Returns:
            DonationResponse with popup message configuration

        Raises:
            ValueError: If validation fails with descriptive error message
        """
        # Step 1: Validate streamer exists
        streamer = self.streamer_service.get_streamer_by_id(streamer_id)
        if streamer is None:
            raise ValueError(f"Streamer not found: {streamer_id}")

        # Check streamer is active
        is_active, error_msg = self.streamer_service.validate_streamer_active(streamer)
        if not is_active:
            raise ValueError(error_msg)

        # Step 2: Validate wallet addresses
        if not self.validation_service.validate_wallet_address(
            donation_data.donor_address
        ):
            raise ValueError(f"Invalid donor address: {donation_data.donor_address}")

        if not self.validation_service.validate_wallet_address(streamer.wallet_address):
            logger.error(f"Streamer has invalid wallet: {streamer.wallet_address}")
            raise ValueError("Streamer wallet address is invalid")

        # Step 3: Validate donation amount range
        is_valid_amount, amount_error = self.validation_service.validate_amount_range(
            donation_data.amount_usd
        )
        if not is_valid_amount:
            raise ValueError(amount_error)

        # Step 4: Find matching tier
        matching_tier = self.streamer_service.find_matching_tier(
            streamer, donation_data.amount_usd
        )
        if matching_tier is None:
            available_amounts = self.streamer_service.get_available_tier_amounts(
                streamer
            )
            raise ValueError(
                f"Invalid donation amount: ${donation_data.amount_usd}. "
                f"Must match one of: {available_amounts}"
            )

        # Step 5: Sanitize message
        clean_message = self.validation_service.sanitize_message(
            donation_data.message, max_length=200
        )

        # Step 6: Create donation record
        donation = DonationMessage(
            donation_id=str(uuid.uuid4()),
            streamer_id=streamer_id,
            amount_usd=donation_data.amount_usd,
            donor_address=donation_data.donor_address,
            message=clean_message,
            clip_url=str(donation_data.clip_url) if donation_data.clip_url else None,
            timestamp=int(time.time()),
            tx_hash=donation_data.tx_hash,
        )

        # Store in database
        self.db.put_donation(donation)

        logger.info(
            f"Donation processed: ${donation.amount_usd} from "
            f"{donation.donor_address[:10]}... to {streamer.name} "
            f"(tx: {donation.tx_hash[:10]}...)"
        )

        # Step 7: Return popup configuration
        return DonationResponseSchema(
            donation_id=donation.donation_id,
            popup_message=matching_tier.popup_message,
            duration_ms=matching_tier.duration_ms,
        )

    def get_donation_by_id(self, donation_id: str) -> Optional[DonationMessage]:
        """
        Retrieve donation by unique ID.

        Args:
            donation_id: UUID4 donation identifier

        Returns:
            DonationMessage if found, None otherwise
        """
        return self.db.get_donation(donation_id)

    def list_donations_for_streamer(
        self, streamer_id: str, limit: int = 100
    ) -> list[DonationMessage]:
        """
        List all donations for a specific streamer.

        Args:
            streamer_id: UUID4 streamer identifier
            limit: Maximum number of donations to return (default: 100, max: 1000)

        Returns:
            List of DonationMessage models sorted by timestamp descending
        """
        # Enforce maximum limit
        if limit > 1000:
            limit = 1000

        return self.db.list_donations_by_streamer(streamer_id, limit=limit)

    def get_donation_stats(self, streamer_id: str) -> dict:
        """
        Calculate donation statistics for a streamer.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Dictionary with:
            - total_amount_usd: Total donations received
            - donation_count: Number of donations
            - unique_donors: Number of unique donor addresses
        """
        return self.db.get_donation_stats(streamer_id)
