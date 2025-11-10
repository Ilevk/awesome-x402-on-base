"""
Mock streamer data for Phase 1 demonstration.

This module contains hardcoded streamer profiles used for testing
and demonstration purposes. In Phase 2, this will be replaced with
a proper registration system.
"""

from app.core.database import DonationDB
from app.models.dtos import DonationTier, Platform, Streamer

# Mock Streamer 1: Logan
LOGAN = Streamer(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    name="Logan",
    wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    platforms=[Platform.YOUTUBE, Platform.TWITCH],
    avatar_url="https://avatar.iran.liara.run/public/42",
    donation_tiers=[
        DonationTier(
            amount_usd=1.0,
            popup_message="Thank you! 💙",
            duration_ms=3000,
        ),
        DonationTier(
            amount_usd=5.0,
            popup_message="Amazing support! 🎉",
            duration_ms=5000,
        ),
        DonationTier(
            amount_usd=10.0,
            popup_message="You're a legend! 🌟",
            duration_ms=8000,
        ),
        DonationTier(
            amount_usd=50.0,
            popup_message="INSANE DONATION! 🔥🔥🔥",
            duration_ms=10000,
        ),
    ],
    thank_you_message=(
        "Thanks for supporting my stream! Your donation helps me create better content. "
        "See you in the next stream! 🎮"
    ),
)

# Mock Streamer 2: Kim
KIM = Streamer(
    id="b2c3d4e5-f6a7-4b89-c012-defabcde3456",
    name="Kim",
    wallet_address="0x8765432109fedcba8765432109fedcba87654321",
    platforms=[Platform.TWITCH],
    avatar_url="https://avatar.iran.liara.run/public/88",
    donation_tiers=[
        DonationTier(
            amount_usd=2.0,
            popup_message="감사합니다! 🙏",
            duration_ms=3000,
        ),
        DonationTier(
            amount_usd=5.0,
            popup_message="대박! 🎊",
            duration_ms=5000,
        ),
        DonationTier(
            amount_usd=10.0,
            popup_message="핵인싸! 😎",
            duration_ms=7000,
        ),
    ],
    thank_you_message="후원 감사합니다! 더 좋은 방송으로 보답하겠습니다! ❤️",
)

# Mock Streamer 3: Alex
ALEX = Streamer(
    id="c3d4e5f6-a7b8-4c90-d123-efabcdef4567",
    name="Alex",
    wallet_address="0xabcdef1234567890abcdef1234567890abcdef12",
    platforms=[Platform.YOUTUBE],
    avatar_url="https://avatar.iran.liara.run/public/15",
    donation_tiers=[
        DonationTier(
            amount_usd=3.0,
            popup_message="Much appreciated! 🙌",
            duration_ms=3000,
        ),
        DonationTier(
            amount_usd=7.0,
            popup_message="You're awesome! ✨",
            duration_ms=5000,
        ),
        DonationTier(
            amount_usd=15.0,
            popup_message="MVP! 👑",
            duration_ms=8000,
        ),
    ],
    thank_you_message=(
        "Thank you so much for the donation! It really means a lot. "
        "Let's keep building together! 🚀"
    ),
)

# Dictionary for easy lookup
MOCK_STREAMERS = {
    "logan": LOGAN,
    "kim": KIM,
    "alex": ALEX,
}

# List of all mock streamers
ALL_MOCK_STREAMERS = [LOGAN, KIM, ALEX]


def get_mock_streamer_by_id(streamer_id: str) -> Streamer | None:
    """
    Get mock streamer by UUID.

    Args:
        streamer_id: UUID4 streamer identifier

    Returns:
        Streamer model if found, None otherwise
    """
    for streamer in ALL_MOCK_STREAMERS:
        if streamer.id == streamer_id:
            return streamer
    return None


def get_mock_streamer_by_name(name: str) -> Streamer | None:
    """
    Get mock streamer by name (case-insensitive).

    Args:
        name: Streamer name

    Returns:
        Streamer model if found, None otherwise
    """
    return MOCK_STREAMERS.get(name.lower())


def init_mock_data_in_db(db: DonationDB) -> None:
    """
    Initialize database with mock streamer data.

    This should be called on application startup to populate
    the database with test data.

    Args:
        db: DonationDB instance
    """
    if not isinstance(db, DonationDB):
        raise TypeError("db must be a DonationDB instance")

    for streamer in ALL_MOCK_STREAMERS:
        try:
            # Check if streamer already exists
            existing = db.get_streamer(streamer.id)
            if existing is None:
                db.put_streamer(streamer)
                print(f"✓ Initialized mock streamer: {streamer.name} ({streamer.id})")
            else:
                print(f"✓ Mock streamer already exists: {streamer.name}")
        except Exception as e:
            print(f"✗ Failed to initialize streamer {streamer.name}: {e}")
