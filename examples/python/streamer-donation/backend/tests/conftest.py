"""Pytest configuration and shared fixtures for async testing."""

import os
import shutil
import tempfile
import uuid
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import Settings
from app.core.database import DonationDB
from app.main import app
from app.models.dtos import DonationMessage, DonationTier, Platform, Streamer


@pytest.fixture(scope="session")
def temp_db_path() -> Generator[str, None, None]:
    """Create temporary database directory for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_donations.db")
    yield db_path
    # Cleanup after all tests
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_settings(temp_db_path: str) -> Settings:
    """Create test settings with temporary database."""
    return Settings(
        network="base-sepolia",
        cdp_api_key_id="test-api-key",
        cdp_api_key_secret="test-secret",
        cdp_wallet_secret="test-wallet-secret",
        rocksdb_path=temp_db_path,
        allowed_origins="http://localhost:3000",
        min_donation_usd=0.01,
        max_donation_usd=1000.0,
    )


@pytest.fixture
def db(temp_db_path: str) -> Generator[DonationDB, None, None]:
    """Create a fresh database instance for each test."""
    db_instance = DonationDB(temp_db_path)
    yield db_instance
    db_instance.close()
    # Clean up database files between tests
    if os.path.exists(temp_db_path):
        shutil.rmtree(temp_db_path)


@pytest.fixture
def sample_streamer() -> Streamer:
    """Create a sample streamer for testing."""
    return Streamer(
        id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
        name="TestStreamer",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
        platforms=[Platform.YOUTUBE, Platform.TWITCH],
        donation_tiers=[
            DonationTier(amount_usd=1.0, popup_message="Thank you! 💙", duration_ms=3000),
            DonationTier(amount_usd=5.0, popup_message="Amazing! 🎉", duration_ms=5000),
            DonationTier(amount_usd=10.0, popup_message="Legend! 🌟", duration_ms=7000),
        ],
        thank_you_message="Thanks for watching!",
        avatar_url="https://example.com/avatar.png",
    )


@pytest.fixture
def sample_donation() -> DonationMessage:
    """Create a sample donation message for testing."""
    return DonationMessage(
        donation_id="d1e2f3a4-b5c6-4890-9bcd-ab1234567890",
        streamer_id="a1b2c3d4-e5f6-4790-8bcd-ef1234567890",
        amount_usd=5.0,
        donor_address="0x1234567890abcdef1234567890abcdef12345678",
        tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        timestamp=1699999999,
        message="Great stream!",
        clip_url=None,
    )


@pytest.fixture
def multiple_streamers() -> list[Streamer]:
    """Create multiple streamers for list testing."""
    return [
        Streamer(
            id=str(uuid.uuid4()),
            name=f"Streamer{i}",
            wallet_address=f"0x{'1' * (i + 1)}{'0' * (39 - i)}",
            platforms=[Platform.YOUTUBE] if i % 2 == 0 else [Platform.TWITCH],
            donation_tiers=[
                DonationTier(
                    amount_usd=float(i + 1), popup_message=f"Thanks {i}!", duration_ms=3000
                )
            ],
            thank_you_message=f"Thank you message {i}",
            avatar_url=None,
        )
        for i in range(5)
    ]


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing async endpoints."""
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def valid_wallet_address() -> str:
    """Valid Ethereum wallet address for testing."""
    return "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"


@pytest.fixture
def invalid_wallet_address() -> str:
    """Invalid wallet address for negative testing."""
    return "invalid_address"


@pytest.fixture
def valid_tx_hash() -> str:
    """Valid transaction hash for testing."""
    return "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"


@pytest.fixture
def invalid_tx_hash() -> str:
    """Invalid transaction hash for negative testing."""
    return "0xinvalid"


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests across layers")
    config.addinivalue_line("markers", "asyncio: Async tests")
