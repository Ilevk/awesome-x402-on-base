"""
Validation service for input sanitization and verification.

This service provides centralized validation logic for wallet addresses,
messages, and donation amounts to ensure data integrity and security.
"""

import logging
from typing import Optional

import bleach
from web3 import Web3

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating and sanitizing user inputs."""

    def __init__(self, min_donation_usd: float = 0.01, max_donation_usd: float = 1000.0):
        """
        Initialize validation service with donation limits.

        Args:
            min_donation_usd: Minimum allowed donation amount in USD
            max_donation_usd: Maximum allowed donation amount in USD
        """
        self.min_donation_usd = min_donation_usd
        self.max_donation_usd = max_donation_usd

    def validate_wallet_address(self, address: str) -> bool:
        """
        Validate Ethereum wallet address format.

        Args:
            address: Ethereum address string to validate

        Returns:
            True if address is valid, False otherwise

        Example:
            >>> service = ValidationService()
            >>> service.validate_wallet_address("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
            True
            >>> service.validate_wallet_address("invalid")
            False
        """
        try:
            return Web3.is_address(address)
        except Exception as e:
            logger.warning(f"Failed to validate address {address}: {e}")
            return False

    def sanitize_message(
        self, message: str | None, max_length: int = 200
    ) -> Optional[str]:
        """
        Sanitize user message to prevent XSS attacks.

        Removes all HTML tags and trims to maximum length.

        Args:
            message: User-provided message to sanitize
            max_length: Maximum allowed message length (default: 200)

        Returns:
            Sanitized message or None if empty after cleaning

        Example:
            >>> service = ValidationService()
            >>> service.sanitize_message("<script>alert('xss')</script>Hello")
            'Hello'
            >>> service.sanitize_message("   ")
            None
        """
        if message is None or not message.strip():
            return None

        # Remove all HTML tags and strip whitespace
        clean = bleach.clean(message, tags=[], strip=True)

        # Trim to max length
        clean = clean[:max_length]

        # Return None if empty after cleaning
        return clean.strip() if clean.strip() else None

    def validate_amount_range(self, amount_usd: float) -> tuple[bool, Optional[str]]:
        """
        Validate donation amount is within allowed range.

        Args:
            amount_usd: Donation amount in USD to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if amount is valid
            - error_message: None if valid, error description if invalid

        Example:
            >>> service = ValidationService()
            >>> service.validate_amount_range(5.0)
            (True, None)
            >>> service.validate_amount_range(0.001)
            (False, 'Donation amount must be at least $0.01')
            >>> service.validate_amount_range(2000.0)
            (False, 'Donation amount cannot exceed $1000.00')
        """
        if amount_usd < self.min_donation_usd:
            return (
                False,
                f"Donation amount must be at least ${self.min_donation_usd:.2f}",
            )

        if amount_usd > self.max_donation_usd:
            return (
                False,
                f"Donation amount cannot exceed ${self.max_donation_usd:.2f}",
            )

        return (True, None)

    def validate_donation_tier_match(
        self, amount_usd: float, tier_amounts: list[float], tolerance: float = 0.01
    ) -> tuple[bool, Optional[int]]:
        """
        Check if donation amount matches any tier amount.

        Args:
            amount_usd: Donation amount to check
            tier_amounts: List of valid tier amounts
            tolerance: Floating point comparison tolerance (default: 0.01)

        Returns:
            Tuple of (is_match, tier_index)
            - is_match: True if amount matches a tier
            - tier_index: Index of matching tier, or None if no match

        Example:
            >>> service = ValidationService()
            >>> service.validate_donation_tier_match(5.0, [1.0, 5.0, 10.0])
            (True, 1)
            >>> service.validate_donation_tier_match(7.5, [1.0, 5.0, 10.0])
            (False, None)
        """
        for idx, tier_amount in enumerate(tier_amounts):
            if abs(tier_amount - amount_usd) < tolerance:
                return (True, idx)

        return (False, None)
