"""
Dependency injection container for FastAPI.

Provides factory functions for creating service instances with proper
dependency management and lifecycle control.
"""

import logging
from functools import lru_cache

from app.core.config import Settings
from app.core.database import DonationDB
from app.repositories.donation_repository import DonationRepository
from app.repositories.streamer_repository import StreamerRepository
from app.services.donation_service import DonationService
from app.services.streamer_service import StreamerService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

# Global database instance (singleton)
_db_instance: DonationDB | None = None


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings instance.

    Cached as singleton to avoid repeated environment loading.

    Returns:
        Settings instance with environment configuration
    """
    return Settings()


def get_db() -> DonationDB:
    """
    Get database instance.

    Uses global singleton pattern to ensure single DB connection
    across application lifecycle.

    Returns:
        DonationDB instance

    Raises:
        RuntimeError: If database has not been initialized
    """
    global _db_instance

    if _db_instance is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() during startup."
        )

    return _db_instance


def init_db(db_path: str | None = None) -> DonationDB:
    """
    Initialize database instance during application startup.

    Should be called in FastAPI lifespan context.

    Args:
        db_path: Optional custom database path. If None, uses settings.

    Returns:
        Initialized DonationDB instance
    """
    global _db_instance

    if _db_instance is not None:
        logger.warning("Database already initialized. Returning existing instance.")
        return _db_instance

    if db_path is None:
        settings = get_settings()
        db_path = settings.rocksdb_path

    logger.info(f"Initializing database at: {db_path}")
    _db_instance = DonationDB(db_path)

    return _db_instance


def close_db() -> None:
    """
    Close database connection during application shutdown.

    Should be called in FastAPI lifespan context.
    """
    global _db_instance

    if _db_instance is not None:
        logger.info("Closing database connection")
        _db_instance.close()
        _db_instance = None


# Repository Factories


def get_streamer_repository() -> StreamerRepository:
    """
    Get StreamerRepository instance.

    Depends on: Database

    Returns:
        StreamerRepository instance
    """
    db = get_db()
    return StreamerRepository(db)


def get_donation_repository() -> DonationRepository:
    """
    Get DonationRepository instance.

    Depends on: Database

    Returns:
        DonationRepository instance
    """
    db = get_db()
    return DonationRepository(db)


# Service Factories


def get_validation_service() -> ValidationService:
    """
    Get ValidationService instance.

    Depends on: Settings

    Returns:
        ValidationService instance
    """
    settings = get_settings()
    return ValidationService(
        min_donation_usd=settings.min_donation_usd,
        max_donation_usd=settings.max_donation_usd,
    )


def get_streamer_service() -> StreamerService:
    """
    Get StreamerService instance.

    Depends on: Database

    Returns:
        StreamerService instance
    """
    db = get_db()
    return StreamerService(db)


def get_donation_service() -> DonationService:
    """
    Get DonationService instance.

    Depends on: Database, ValidationService, StreamerService

    Returns:
        DonationService instance
    """
    db = get_db()
    validation_service = get_validation_service()
    streamer_service = get_streamer_service()

    return DonationService(
        db=db,
        validation_service=validation_service,
        streamer_service=streamer_service,
    )
