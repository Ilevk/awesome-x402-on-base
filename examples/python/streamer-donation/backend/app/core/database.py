"""
RocksDB database wrapper for streamer donation system.

This module provides a simple key-value store interface using RocksDB
for persisting streamer and donation data.
"""

import json
import logging
from typing import Any

from rocksdict import Options, Rdict

from app.models.dtos import DonationMessage, DonationTier, Platform, Streamer

logger = logging.getLogger(__name__)


class DonationDB:
    """
    RocksDB wrapper for streamer and donation data.

    This class provides methods to store and retrieve streamer profiles
    and donation messages using RocksDB as the underlying storage engine.
    """

    def __init__(self, db_path: str = "./data/donations.db") -> None:
        """
        Initialize RocksDB connection.

        Args:
            db_path: Path to RocksDB database directory

        Raises:
            Exception: If database initialization fails
        """
        self.db_path = db_path

        # Configure RocksDB options for optimal performance
        opts = Options()
        opts.create_if_missing(True)
        opts.set_max_open_files(300000)
        opts.set_write_buffer_size(67108864)  # 64MB
        opts.set_max_write_buffer_number(3)
        opts.set_target_file_size_base(67108864)  # 64MB

        try:
            self.db: Rdict = Rdict(db_path, options=opts)
            logger.info(f"RocksDB initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize RocksDB: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self, "db"):
            self.db.close()
            logger.info("RocksDB connection closed")

    # ==================== Streamer Operations ====================

    def put_streamer(self, streamer: Streamer) -> None:
        """
        Store or update a streamer profile.

        Args:
            streamer: Streamer DTO to store

        Raises:
            Exception: If database write fails
        """
        key = f"streamers:{streamer.id}".encode()

        # Convert dataclass to dict for JSON serialization
        data = {
            "id": streamer.id,
            "name": streamer.name,
            "wallet_address": streamer.wallet_address,
            "platforms": [p.value for p in streamer.platforms],
            "avatar_url": streamer.avatar_url,
            "donation_tiers": [
                {
                    "amount_usd": tier.amount_usd,
                    "popup_message": tier.popup_message,
                    "duration_ms": tier.duration_ms,
                }
                for tier in streamer.donation_tiers
            ],
            "thank_you_message": streamer.thank_you_message,
        }
        value = json.dumps(data).encode("utf-8")

        try:
            self.db[key] = value
            logger.debug(f"Stored streamer: {streamer.id}")
        except Exception as e:
            logger.error(f"Failed to store streamer {streamer.id}: {e}")
            raise

    def get_streamer(self, streamer_id: str) -> Streamer | None:
        """
        Retrieve a streamer by ID.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Streamer DTO if found, None otherwise

        Raises:
            Exception: If database read fails or data is corrupted
        """
        key = f"streamers:{streamer_id}".encode()

        try:
            value = self.db.get(key)
            if value is not None:
                data: dict[str, Any] = json.loads(value.decode("utf-8"))
                # Convert dict to Streamer DTO
                return Streamer(
                    id=data["id"],
                    name=data["name"],
                    wallet_address=data["wallet_address"],
                    platforms=[Platform(p) for p in data["platforms"]],
                    avatar_url=data.get("avatar_url"),
                    donation_tiers=[DonationTier(**tier) for tier in data["donation_tiers"]],
                    thank_you_message=data["thank_you_message"],
                )
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted data for streamer {streamer_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get streamer {streamer_id}: {e}")
            raise

    def get_streamer_by_wallet(self, wallet_address: str) -> Streamer | None:
        """
        Retrieve a streamer by wallet address.

        Note: This is a full scan operation in Phase 1. Phase 2 will add indexing.

        Args:
            wallet_address: Ethereum wallet address

        Returns:
            Streamer model if found, None otherwise
        """
        wallet_lower = wallet_address.lower()

        # Scan all streamers (inefficient, but acceptable for Phase 1)
        it = self.db.items()

        for key, value in it:
            # Type cast to bytes for decode operation
            key_bytes: bytes = key if isinstance(key, bytes) else key.encode("utf-8")  # type: ignore[union-attr]
            value_bytes: bytes = value if isinstance(value, bytes) else value.encode("utf-8")
            key_str = key_bytes.decode("utf-8")
            if not key_str.startswith("streamers:"):
                break

            try:
                data = json.loads(value_bytes.decode("utf-8"))
                if data.get("wallet_address", "").lower() == wallet_lower:
                    return Streamer(
                        id=data["id"],
                        name=data["name"],
                        wallet_address=data["wallet_address"],
                        platforms=[Platform(p) for p in data["platforms"]],
                        avatar_url=data.get("avatar_url"),
                        donation_tiers=[DonationTier(**tier) for tier in data["donation_tiers"]],
                        thank_you_message=data["thank_you_message"],
                    )
            except Exception as e:
                logger.warning(f"Skipping corrupted streamer data: {e}")
                continue

        return None

    def list_streamers(self, limit: int = 100) -> list[Streamer]:
        """
        List all streamers.

        Args:
            limit: Maximum number of streamers to return

        Returns:
            List of Streamer models
        """
        streamers: list[Streamer] = []

        for key, value in self.db.items(from_key=b"streamers:"):
            # Type cast to bytes for decode operation
            key_bytes: bytes = key if isinstance(key, bytes) else key.encode("utf-8")  # type: ignore[union-attr]
            value_bytes: bytes = value if isinstance(value, bytes) else value.encode("utf-8")
            key_str: str = key_bytes.decode("utf-8")
            if not key_str.startswith("streamers:"):
                break

            if len(streamers) >= limit:
                break

            try:
                data: dict[str, Any] = json.loads(value_bytes.decode("utf-8"))
                streamers.append(
                    Streamer(
                        id=data["id"],
                        name=data["name"],
                        wallet_address=data["wallet_address"],
                        platforms=[Platform(p) for p in data["platforms"]],
                        avatar_url=data.get("avatar_url"),
                        donation_tiers=[DonationTier(**tier) for tier in data["donation_tiers"]],
                        thank_you_message=data["thank_you_message"],
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping corrupted streamer data: {e}")
                continue

        return streamers

    def delete_streamer(self, streamer_id: str) -> bool:
        """
        Delete a streamer by ID.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            True if deleted, False if not found
        """
        key = f"streamers:{streamer_id}".encode()

        try:
            if self.db.get(key):
                self.db.delete(key)
                logger.info(f"Deleted streamer: {streamer_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete streamer {streamer_id}: {e}")
            raise

    # ==================== Donation Operations ====================

    def put_donation(self, donation: DonationMessage) -> None:
        """
        Store a donation message.

        Args:
            donation: DonationMessage DTO to store

        Raises:
            Exception: If database write fails
        """
        key = f"donations:{donation.donation_id}".encode()

        # Convert dataclass to dict for JSON serialization
        data = {
            "donation_id": donation.donation_id,
            "streamer_id": donation.streamer_id,
            "amount_usd": donation.amount_usd,
            "donor_address": donation.donor_address,
            "tx_hash": donation.tx_hash,
            "timestamp": donation.timestamp,
            "message": donation.message,
            "clip_url": donation.clip_url,
        }
        value = json.dumps(data).encode("utf-8")

        try:
            self.db[key] = value
            logger.debug(f"Stored donation: {donation.donation_id}")
        except Exception as e:
            logger.error(f"Failed to store donation {donation.donation_id}: {e}")
            raise

    def get_donation(self, donation_id: str) -> DonationMessage | None:
        """
        Retrieve a donation by ID.

        Args:
            donation_id: UUID4 donation identifier

        Returns:
            DonationMessage DTO if found, None otherwise
        """
        key = f"donations:{donation_id}".encode()

        try:
            value = self.db.get(key)
            if value:
                data = json.loads(value.decode("utf-8"))
                return DonationMessage(
                    donation_id=data["donation_id"],
                    streamer_id=data["streamer_id"],
                    amount_usd=data["amount_usd"],
                    donor_address=data["donor_address"],
                    tx_hash=data["tx_hash"],
                    timestamp=data["timestamp"],
                    message=data.get("message"),
                    clip_url=data.get("clip_url"),
                )
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted data for donation {donation_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get donation {donation_id}: {e}")
            raise

    def list_donations_by_streamer(
        self, streamer_id: str, limit: int = 100
    ) -> list[DonationMessage]:
        """
        List all donations for a specific streamer.

        Note: This is a full scan operation in Phase 1. Phase 2 will add indexing.

        Args:
            streamer_id: UUID4 streamer identifier
            limit: Maximum number of donations to return

        Returns:
            List of DonationMessage models
        """
        donations = []

        for key, value in self.db.items(from_key=b"donations:"):
            # Type cast to bytes for decode operation
            key_bytes: bytes = key if isinstance(key, bytes) else key.encode("utf-8")  # type: ignore[union-attr]
            value_bytes: bytes = value if isinstance(value, bytes) else value.encode("utf-8")
            key_str = key_bytes.decode("utf-8")
            if not key_str.startswith("donations:"):
                break

            if len(donations) >= limit:
                break

            try:
                data = json.loads(value_bytes.decode("utf-8"))
                if data.get("streamer_id") == streamer_id:
                    donations.append(
                        DonationMessage(
                            donation_id=data["donation_id"],
                            streamer_id=data["streamer_id"],
                            amount_usd=data["amount_usd"],
                            donor_address=data["donor_address"],
                            tx_hash=data["tx_hash"],
                            timestamp=data["timestamp"],
                            message=data.get("message"),
                            clip_url=data.get("clip_url"),
                        )
                    )
            except Exception as e:
                logger.warning(f"Skipping corrupted donation data: {e}")
                continue

        # Sort by timestamp descending (most recent first)
        donations.sort(key=lambda d: d.timestamp, reverse=True)
        return donations

    def get_donation_stats(self, streamer_id: str) -> dict[str, float]:
        """
        Get donation statistics for a streamer.

        Args:
            streamer_id: UUID4 streamer identifier

        Returns:
            Dictionary with total_amount, donation_count, and unique_donors
        """
        donations = self.list_donations_by_streamer(streamer_id, limit=10000)

        total_amount = sum(d.amount_usd for d in donations)
        donation_count = len(donations)
        unique_donors = len({d.donor_address.lower() for d in donations})

        return {
            "total_amount_usd": total_amount,
            "donation_count": donation_count,
            "unique_donors": unique_donors,
        }


# Global database instance (initialized in main.py)
db: DonationDB | None = None


def get_db() -> DonationDB:
    """
    Get the global database instance.

    Returns:
        DonationDB instance

    Raises:
        RuntimeError: If database is not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db


def init_db(db_path: str = "./data/donations.db") -> DonationDB:
    """
    Initialize the global database instance.

    Args:
        db_path: Path to RocksDB database directory

    Returns:
        DonationDB instance
    """
    global db
    db = DonationDB(db_path)
    return db


def close_db() -> None:
    """Close the global database instance."""
    global db
    if db is not None:
        db.close()
        db = None
