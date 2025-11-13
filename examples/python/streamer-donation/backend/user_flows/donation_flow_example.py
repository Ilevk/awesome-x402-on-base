"""
Example script demonstrating end-to-end donation flow.

This script shows how a user can:
1. Search for their favorite streamer
2. View available donation tiers
3. Make a donation using x402 payment protocol
4. Verify the donation was recorded

Usage:
    python user_flows/donation_flow_example.py

Requirements:
    - Backend server running (http://localhost:8000)
    - x402 client library installed
    - Web3 wallet configured with private key

Author: Logan (Base Korea Developer Ambassador)
License: MIT
"""

import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv
from eth_account import Account

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
NETWORK = os.getenv("NETWORK", "base-sepolia")

# Validate configuration
if not PRIVATE_KEY:
    raise ValueError(
        "PRIVATE_KEY not set in environment. "
        "Please set it in .env file or as environment variable."
    )

# Initialize Web3 account
account = Account.from_key(PRIVATE_KEY)
donor_address = account.address

print("=" * 80)
print("🎮 Streamer Donation Flow Example - x402 on Base")
print("=" * 80)
print(f"Donor Address: {donor_address}")
print(f"Network: {NETWORK}")
print(f"API URL: {API_BASE_URL}")
print("=" * 80)
print()


def search_streamer(name_query: str) -> dict[str, Any] | None:
    """
    Search for a streamer by name.

    Args:
        name_query: Streamer name to search for

    Returns:
        Streamer data if found, None otherwise
    """
    print(f"🔍 Searching for streamer: '{name_query}'...")

    try:
        response = httpx.get(f"{API_BASE_URL}/api/streamers", timeout=10)
        response.raise_for_status()

        streamers = response.json()
        print(f"   Found {len(streamers)} total streamers")

        # Search by name (case-insensitive)
        for streamer in streamers:
            if name_query.lower() in streamer["name"].lower():
                print(f"✅ Found streamer: {streamer['name']} ({streamer['id']})")
                return streamer

        print(f"❌ No streamer found matching '{name_query}'")
        return None

    except httpx.HTTPError as e:
        print(f"❌ Error searching streamers: {e}")
        return None


def display_donation_tiers(streamer: dict[str, Any]) -> None:
    """
    Display available donation tiers for a streamer.

    Args:
        streamer: Streamer data from API
    """
    print()
    print(f"💰 Available donation tiers for {streamer['name']}:")
    print("-" * 60)

    for i, tier in enumerate(streamer["donation_tiers"], 1):
        print(f"{i}. ${tier['amount_usd']:.2f} USD")
        print(f"   💬 Message: {tier['popup_message']}")
        print(f"   ⏱️  Duration: {tier['duration_ms'] / 1000:.1f}s")
        print()


def access_donation_page_with_x402(streamer_id: str) -> bool:
    """
    Access the x402-protected donation page.

    This simulates the flow where:
    1. Client tries to access /donate/{streamer_id}
    2. Server responds with 402 Payment Required
    3. Client pays via x402 protocol
    4. Client accesses the page with payment proof

    Args:
        streamer_id: Streamer UUID

    Returns:
        True if access granted, False otherwise
    """
    print()
    print("🔐 Accessing x402-protected donation page...")
    print(f"   Endpoint: GET /donate/{streamer_id}")

    try:
        # Try accessing without payment
        response = httpx.get(
            f"{API_BASE_URL}/donate/{streamer_id}",
            timeout=10,
            follow_redirects=False,
        )

        if response.status_code == 402:
            print("   💳 Server requires payment (402 Payment Required)")
            print()
            print("   ⚠️  Note: Full x402 payment flow requires:")
            print("      - x402 client library integration")
            print("      - Payment signature generation")
            print("      - X-PAYMENT header with proof")
            print()
            print("   📝 For this example, we'll skip x402 payment")
            print("      and proceed directly to donation submission.")
            return True

        elif response.status_code == 200:
            print("   ✅ Access granted (page loaded)")
            return True

        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False

    except httpx.HTTPError as e:
        print(f"   ❌ Error accessing page: {e}")
        return False


def make_donation(
    streamer_id: str,
    amount_usd: float,
    message: str | None = None,
) -> dict[str, Any] | None:
    """
    Submit a donation message to the streamer.

    Args:
        streamer_id: Streamer UUID
        amount_usd: Donation amount in USD
        message: Optional custom message

    Returns:
        Donation response data if successful, None otherwise
    """
    print()
    print(f"💸 Making donation of ${amount_usd:.2f}...")

    # Generate a mock transaction hash (in real scenario, this comes from blockchain)
    tx_hash = "0x" + os.urandom(32).hex()

    donation_data = {
        "amount_usd": amount_usd,
        "donor_address": donor_address,
        "tx_hash": tx_hash,
        "message": message,
        "clip_url": None,
    }

    try:
        response = httpx.post(
            f"{API_BASE_URL}/api/donate/{streamer_id}/message",
            json=donation_data,
            timeout=10,
        )
        response.raise_for_status()

        result = response.json()
        print("✅ Donation successful!")
        print(f"   Donation ID: {result['donation_id']}")
        print(f"   Popup Message: {result['popup_message']}")
        print(f"   Duration: {result['duration_ms'] / 1000:.1f}s")

        return result

    except httpx.HTTPStatusError as e:
        print(f"❌ Donation failed: {e.response.status_code}")
        print(f"   Error: {e.response.json().get('detail', 'Unknown error')}")
        return None
    except httpx.HTTPError as e:
        print(f"❌ Error making donation: {e}")
        return None


def verify_donation(donation_id: str) -> dict[str, Any] | None:
    """
    Verify that the donation was recorded correctly.

    Args:
        donation_id: Donation UUID

    Returns:
        Donation data if found, None otherwise
    """
    print()
    print("🔍 Verifying donation...")

    try:
        response = httpx.get(
            f"{API_BASE_URL}/api/donations/{donation_id}",
            timeout=10,
        )
        response.raise_for_status()

        donation = response.json()
        print("✅ Donation verified!")
        print(f"   Amount: ${donation['amount_usd']:.2f}")
        print(f"   Message: {donation.get('message', 'No message')}")
        print(f"   TX Hash: {donation['tx_hash'][:20]}...")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(donation["timestamp"]))
        print(f"   Timestamp: {timestamp}")

        return donation

    except httpx.HTTPError as e:
        print(f"❌ Error verifying donation: {e}")
        return None


def view_streamer_stats(streamer_id: str) -> None:
    """
    View donation statistics for the streamer.

    Args:
        streamer_id: Streamer UUID
    """
    print()
    print("📊 Fetching streamer donation statistics...")

    try:
        response = httpx.get(
            f"{API_BASE_URL}/api/donations/streamer/{streamer_id}/stats",
            timeout=10,
        )
        response.raise_for_status()

        stats = response.json()
        print("✅ Statistics retrieved!")
        print(f"   Total Amount: ${stats['total_amount_usd']:.2f}")
        print(f"   Total Donations: {stats['donation_count']}")
        print(f"   Unique Donors: {stats['unique_donors']}")

    except httpx.HTTPError as e:
        print(f"❌ Error fetching statistics: {e}")


def main() -> None:
    """
    Main donation flow demonstration.

    Flow:
    1. Search for favorite streamer
    2. View donation tiers
    3. Access x402-protected donation page
    4. Make a donation
    5. Verify donation was recorded
    6. View updated statistics
    """
    # Step 1: Search for streamer
    print("Step 1: Search for your favorite streamer")
    print("-" * 80)
    streamer_name = input("Enter streamer name to search (or press Enter for 'Logan'): ").strip()
    if not streamer_name:
        streamer_name = "Logan"

    streamer = search_streamer(streamer_name)
    if not streamer:
        print()
        print("❌ Cannot proceed without finding a streamer.")
        print("   Make sure the backend server is running with mock data.")
        return

    # Step 2: View donation tiers
    print()
    print("Step 2: View available donation tiers")
    print("-" * 80)
    display_donation_tiers(streamer)

    # Step 3: Select donation amount
    print("Step 3: Select donation amount")
    print("-" * 80)
    tier_amounts = [tier["amount_usd"] for tier in streamer["donation_tiers"]]
    print(f"Available amounts: {', '.join(f'${amt:.2f}' for amt in tier_amounts)}")

    prompt = f"Enter donation amount (or press Enter for ${tier_amounts[0]:.2f}): "
    amount_input = input(prompt).strip()
    if not amount_input:
        donation_amount = tier_amounts[0]
    else:
        try:
            donation_amount = float(amount_input)
        except ValueError:
            print(f"Invalid amount, using default: ${tier_amounts[0]:.2f}")
            donation_amount = tier_amounts[0]

    # Step 4: Add custom message
    print()
    print("Step 4: Add a custom message (optional)")
    print("-" * 80)
    custom_message = input("Enter your message (or press Enter to skip): ").strip()
    if not custom_message:
        custom_message = "Thanks for the amazing stream! 🎉"

    # Step 5: Access x402-protected page
    print()
    print("Step 5: Access x402-protected donation page")
    print("-" * 80)
    access_granted = access_donation_page_with_x402(streamer["id"])
    if not access_granted:
        print("❌ Could not access donation page. Exiting.")
        return

    # Step 6: Make donation
    print()
    print("Step 6: Submit donation")
    print("-" * 80)
    donation_result = make_donation(
        streamer_id=streamer["id"],
        amount_usd=donation_amount,
        message=custom_message,
    )

    if not donation_result:
        print("❌ Donation failed. Exiting.")
        return

    # Step 7: Verify donation
    print()
    print("Step 7: Verify donation was recorded")
    print("-" * 80)
    verify_donation(donation_result["donation_id"])

    # Step 8: View updated statistics
    print()
    print("Step 8: View updated streamer statistics")
    print("-" * 80)
    view_streamer_stats(streamer["id"])

    # Success summary
    print()
    print("=" * 80)
    print("✨ Donation flow completed successfully!")
    print("=" * 80)
    print("📝 Summary:")
    print(f"   Streamer: {streamer['name']}")
    print(f"   Amount: ${donation_amount:.2f}")
    print(f"   Message: {custom_message}")
    print(f"   Donation ID: {donation_result['donation_id']}")
    print(f"   Popup: {donation_result['popup_message']}")
    print()
    print("🎉 Thank you for supporting your favorite streamer!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Donation flow interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        raise
