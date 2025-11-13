"""Tests for API route endpoints."""

import uuid
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.database import DonationDB
from app.core.dependencies import get_db
from app.main import app
from app.models.dtos import DonationMessage, Streamer


@pytest.fixture
def client(db: DonationDB) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with dependency overrides."""
    from app.core.dependencies import (
        get_donation_service,
        get_streamer_service,
        get_validation_service,
    )
    from app.services.donation_service import DonationService
    from app.services.streamer_service import StreamerService
    from app.services.validation_service import ValidationService

    def override_get_db() -> DonationDB:
        return db

    def override_get_validation_service() -> ValidationService:
        return ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)

    def override_get_streamer_service() -> StreamerService:
        return StreamerService(db)

    def override_get_donation_service() -> DonationService:
        return DonationService(
            db=db,
            validation_service=override_get_validation_service(),
            streamer_service=override_get_streamer_service(),
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_validation_service] = override_get_validation_service
    app.dependency_overrides[get_streamer_service] = override_get_streamer_service
    app.dependency_overrides[get_donation_service] = override_get_donation_service

    yield TestClient(app)
    app.dependency_overrides.clear()


class TestDonationRoutes:
    """Test donation API endpoints."""

    def test_submit_donation_success(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test successful donation submission."""
        db.put_streamer(sample_streamer)

        donation_data = {
            "amount_usd": 5.0,
            "donor_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "message": "Great stream!",
            "clip_url": None,
        }

        with patch("time.time", return_value=1699999999):
            response = client.post(f"/api/donate/{sample_streamer.id}/message", json=donation_data)

        assert response.status_code == 201
        data = response.json()
        assert "donation_id" in data
        assert data["popup_message"] == "Amazing! 🎉"
        assert data["duration_ms"] == 5000

    def test_submit_donation_streamer_not_found(self, client: TestClient) -> None:
        """Test donation submission with non-existent streamer."""
        donation_data = {
            "amount_usd": 5.0,
            "donor_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "message": "Test",
            "clip_url": None,
        }

        response = client.post("/api/donate/nonexistent-id/message", json=donation_data)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_submit_donation_invalid_amount(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donation submission with invalid amount."""
        db.put_streamer(sample_streamer)

        donation_data = {
            "amount_usd": 0.001,  # Below minimum
            "donor_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "message": "Test",
            "clip_url": None,
        }

        response = client.post(f"/api/donate/{sample_streamer.id}/message", json=donation_data)

        # Service validation catches it before Pydantic
        assert response.status_code == 400

    def test_submit_donation_invalid_wallet(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donation submission with invalid wallet address."""
        db.put_streamer(sample_streamer)

        donation_data = {
            "amount_usd": 5.0,
            "donor_address": "invalid_address",
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "message": "Test",
            "clip_url": None,
        }

        response = client.post(f"/api/donate/{sample_streamer.id}/message", json=donation_data)

        assert response.status_code == 422  # Pydantic validation error

    def test_submit_donation_no_matching_tier(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test donation submission with amount not matching any tier."""
        db.put_streamer(sample_streamer)

        donation_data = {
            "amount_usd": 7.5,  # Not a valid tier amount
            "donor_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "message": "Test",
            "clip_url": None,
        }

        response = client.post(f"/api/donate/{sample_streamer.id}/message", json=donation_data)

        assert response.status_code == 400
        assert "invalid donation amount" in response.json()["detail"].lower()

    def test_get_donation_by_id(
        self, client: TestClient, db: DonationDB, sample_donation: DonationMessage
    ) -> None:
        """Test retrieving donation by ID."""
        db.put_donation(sample_donation)

        response = client.get(f"/api/donations/{sample_donation.donation_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["donation_id"] == sample_donation.donation_id
        assert data["amount_usd"] == sample_donation.amount_usd

    def test_get_donation_not_found(self, client: TestClient) -> None:
        """Test retrieving non-existent donation."""
        response = client.get("/api/donations/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_donations_for_streamer(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test listing donations for a streamer."""
        db.put_streamer(sample_streamer)

        # Create multiple donations
        for i in range(3):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=5.0,
                donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            db.put_donation(donation)

        response = client.get(f"/api/donations/streamer/{sample_streamer.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("donation_id" in item for item in data)

    def test_list_donations_streamer_not_found(self, client: TestClient) -> None:
        """Test listing donations for non-existent streamer."""
        response = client.get("/api/donations/streamer/nonexistent-id")

        assert response.status_code == 404

    def test_list_donations_respects_limit(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test listing donations respects limit parameter."""
        db.put_streamer(sample_streamer)

        # Create 5 donations
        for i in range(5):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=5.0,
                donor_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999 + i,
                message=f"Donation {i}",
                clip_url=None,
            )
            db.put_donation(donation)

        response = client.get(f"/api/donations/streamer/{sample_streamer.id}?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_donation_stats(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test getting donation statistics."""
        db.put_streamer(sample_streamer)

        # Create donations with known amounts
        amounts = [1.0, 5.0, 10.0, 5.0]  # Total: 21.0
        donor1 = "0x1111111111111111111111111111111111111111"
        donor2 = "0x2222222222222222222222222222222222222222"

        for i, amount in enumerate(amounts):
            donation = DonationMessage(
                donation_id=str(uuid.uuid4()),
                streamer_id=sample_streamer.id,
                amount_usd=amount,
                donor_address=donor1 if i < 2 else donor2,
                tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                timestamp=1699999999,
                message="Test",
                clip_url=None,
            )
            db.put_donation(donation)

        response = client.get(f"/api/donations/streamer/{sample_streamer.id}/stats")

        assert response.status_code == 200
        stats = response.json()
        assert stats["total_amount_usd"] == 21.0
        assert stats["donation_count"] == 4
        assert stats["unique_donors"] == 2

    def test_get_donation_stats_streamer_not_found(self, client: TestClient) -> None:
        """Test getting stats for non-existent streamer."""
        response = client.get("/api/donations/streamer/nonexistent-id/stats")

        assert response.status_code == 404


class TestStreamerRoutes:
    """Test streamer API endpoints."""

    def test_get_streamer_by_id(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test retrieving streamer by ID."""
        db.put_streamer(sample_streamer)

        response = client.get(f"/api/streamer/{sample_streamer.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_streamer.id
        assert data["name"] == sample_streamer.name
        assert data["wallet_address"] == sample_streamer.wallet_address
        assert len(data["donation_tiers"]) == 3

    def test_get_streamer_not_found(self, client: TestClient) -> None:
        """Test retrieving non-existent streamer."""
        response = client.get("/api/streamer/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_streamers(
        self, client: TestClient, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test listing all streamers."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        response = client.get("/api/streamers")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(multiple_streamers)
        assert all("id" in item for item in data)
        assert all("name" in item for item in data)

    def test_list_streamers_empty(self, client: TestClient) -> None:
        """Test listing streamers when none exist."""
        response = client.get("/api/streamers")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_streamers_respects_limit(
        self, client: TestClient, db: DonationDB, multiple_streamers: list[Streamer]
    ) -> None:
        """Test listing streamers respects limit parameter."""
        for streamer in multiple_streamers:
            db.put_streamer(streamer)

        response = client.get("/api/streamers?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_streamer_by_wallet(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test retrieving streamer by wallet address."""
        db.put_streamer(sample_streamer)

        response = client.get(f"/api/streamer/by-wallet/{sample_streamer.wallet_address}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_streamer.id
        assert data["wallet_address"] == sample_streamer.wallet_address

    def test_get_streamer_by_wallet_not_found(self, client: TestClient) -> None:
        """Test retrieving streamer by non-existent wallet."""
        response = client.get("/api/streamer/by-wallet/0x0000000000000000000000000000000000000000")

        assert response.status_code == 404
        detail = response.json()["detail"].lower()
        assert "no streamer found" in detail or "not found" in detail


class TestRouteEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_limit_too_small(self, client: TestClient) -> None:
        """Test query parameter validation for limit below minimum."""
        response = client.get("/api/streamers?limit=0")

        assert response.status_code == 422  # Validation error

    def test_invalid_limit_too_large(self, client: TestClient) -> None:
        """Test query parameter validation for limit above maximum."""
        response = client.get("/api/streamers?limit=5000")

        assert response.status_code == 422  # Validation error

    def test_malformed_json(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test handling of malformed JSON in request body."""
        db.put_streamer(sample_streamer)

        response = client.post(
            f"/api/donate/{sample_streamer.id}/message",
            data={"invalid json": "invalid json"},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    def test_missing_required_fields(
        self, client: TestClient, db: DonationDB, sample_streamer: Streamer
    ) -> None:
        """Test handling of missing required fields."""
        db.put_streamer(sample_streamer)

        # Missing donor_address and tx_hash
        incomplete_data = {
            "amount_usd": 5.0,
            "message": "Test",
        }

        response = client.post(f"/api/donate/{sample_streamer.id}/message", json=incomplete_data)

        assert response.status_code == 422
