"""
Data Transfer Objects (DTOs) for internal use.

These are lightweight dataclasses used for passing data between layers.
Unlike Pydantic models, they don't include validation logic.
"""

from dataclasses import dataclass
from enum import Enum


class Platform(str, Enum):
    """Supported streaming platforms."""

    YOUTUBE = "youtube"
    TWITCH = "twitch"


@dataclass
class DonationTier:
    """
    A donation tier with custom popup message.

    Attributes:
        amount_usd: Donation amount in USD
        popup_message: Message displayed on stream overlay
        duration_ms: Duration to display popup message (milliseconds)
    """

    amount_usd: float
    popup_message: str
    duration_ms: int = 3000


@dataclass
class Streamer:
    """
    Complete streamer data transfer object.

    Used for passing streamer data between service and repository layers.
    """

    id: str
    name: str
    wallet_address: str
    platforms: list[Platform]
    donation_tiers: list[DonationTier]
    thank_you_message: str
    avatar_url: str | None = None


@dataclass
class DonationMessage:
    """
    Complete donation message data transfer object.

    Used for passing donation data between service and repository layers.
    """

    donation_id: str
    streamer_id: str
    amount_usd: float
    donor_address: str
    tx_hash: str
    timestamp: int
    message: str | None = None
    clip_url: str | None = None
