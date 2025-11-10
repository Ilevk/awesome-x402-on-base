"""
Repository for streamer data access.

Provides abstraction layer over database operations for streamers.
"""

import logging
from typing import Optional

from app.core.database import DonationDB
from app.models.dtos import Streamer

logger = logging.getLogger(__name__)


class StreamerRepository:
    """Repository for managing streamer data access."""

    def __init__(self, db: DonationDB):
        """
        Initialize repository with database instance.

        Args:
            db: DonationDB instance for data access
        """
        self.db = db

    def get_by_id(self, streamer_id: str) -> Optional[Streamer]:
        """
        Retrieve streamer by unique ID.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Streamer model if found, None otherwise
        """
        return self.db.get_streamer(streamer_id)

    def get_by_wallet(self, wallet_address: str) -> Optional[Streamer]:
        """
        Retrieve streamer by wallet address.

        Args:
            wallet_address: Ethereum wallet address (0x...)

        Returns:
            Streamer model if found, None otherwise
        """
        return self.db.get_streamer_by_wallet(wallet_address)

    def list_all(self, limit: int = 100) -> list[Streamer]:
        """
        List all streamers.

        Args:
            limit: Maximum number of streamers to return

        Returns:
            List of Streamer models
        """
        return self.db.list_streamers(limit=limit)

    def save(self, streamer: Streamer) -> None:
        """
        Save streamer to database.

        Creates new streamer or updates existing one.

        Args:
            streamer: Streamer model to save
        """
        self.db.put_streamer(streamer)
        logger.debug(f"Saved streamer: {streamer.name} ({streamer.id})")

    def exists(self, streamer_id: str) -> bool:
        """
        Check if streamer exists by ID.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            True if streamer exists, False otherwise
        """
        return self.get_by_id(streamer_id) is not None
