"""
Application configuration using Pydantic Settings.

This module loads environment variables and provides typed configuration
for the FastAPI application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be configured via .env file or environment variables.
    """

    # Network Configuration
    network: str = "base-sepolia"

    # CDP Platform Credentials
    cdp_api_key_id: str = ""
    cdp_api_key_secret: str = ""
    cdp_wallet_secret: str = ""

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Database
    rocksdb_path: str = "./data/donations.db"

    # Security
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    min_donation_usd: float = 0.01
    max_donation_usd: float = 1000.0
    max_message_length: int = 200

    # x402 Configuration
    x402_timeout_seconds: int = 120
    x402_donation_page_price: str = "$0.001"  # Price to access donation page
    server_wallet_address: str = ""  # Server wallet address for receiving payments

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_testnet(self) -> bool:
        """Check if running on testnet."""
        return "sepolia" in self.network.lower() or "test" in self.network.lower()

    @property
    def base_chain_id(self) -> int:
        """Get Base chain ID based on network."""
        if self.is_testnet:
            return 84532  # Base Sepolia
        return 8453  # Base Mainnet

    def validate_cdp_credentials(self) -> bool:
        """Check if CDP credentials are configured."""
        return bool(self.cdp_api_key_id and self.cdp_api_key_secret and self.cdp_wallet_secret)


# Global settings instance
settings = Settings()
