"""
FastAPI main application with Layered Architecture.

This application implements a streamer donation system using x402 protocol
on Base blockchain with the following architecture:

Layers:
1. Presentation Layer: FastAPI routes (app/routes/)
2. Business Logic Layer: Service classes (app/services/)
3. Data Access Layer: Repository pattern (app/repositories/)
4. Infrastructure Layer: RocksDB, Web3, x402 (app/database.py, app/config.py)

Author: Logan (Base Korea Developer Ambassador)
License: MIT
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from x402.fastapi.middleware import require_payment

from app.core.config import Settings
from app.core.dependencies import close_db, get_db, get_settings, init_db
from app.mock_data import init_mock_data_in_db
from app.routes import donations, pages, streamers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database, load mock data
    - Shutdown: Close database connection gracefully
    """
    # Startup
    settings = get_settings()
    logger.info(f"Starting Streamer Donation System on {settings.network}")
    logger.info(f"Chain ID: {settings.base_chain_id}")

    # Initialize database
    try:
        db = init_db(settings.rocksdb_path)
        logger.info(f"Database initialized at: {settings.rocksdb_path}")

        # Load mock data
        init_mock_data_in_db(db)
        logger.info("Mock streamer data loaded")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")
    close_db()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="Streamer Donation System",
    description=(
        "x402-based donation system for streamers on Base blockchain. "
        "Supports multi-tier donations with customizable popup messages."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
settings = Settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure x402 payment middleware for donation page
# This protects the /donate/{streamer_id} route
if settings.server_wallet_address:
    app.middleware("http")(
        require_payment(
            path="/donate/*",
            price=settings.x402_donation_page_price,
            pay_to_address=settings.server_wallet_address,
            network=settings.network,
        )
    )
    logger.info(
        f"x402 middleware enabled for /donate/* (price: {settings.x402_donation_page_price})"
    )
else:
    logger.warning(
        "x402 middleware disabled: SERVER_WALLET_ADDRESS not configured. "
        "Donation page will be accessible without payment."
    )


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns system status and configuration information.
    """
    settings = get_settings()

    try:
        # Check database connection
        get_db()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    return JSONResponse(
        content={
            "status": "healthy" if db_status == "connected" else "degraded",
            "network": settings.network,
            "chain_id": settings.base_chain_id,
            "database": db_status,
            "testnet": settings.is_testnet,
        }
    )


# Include API routers
app.include_router(streamers.router)
app.include_router(donations.router)
app.include_router(pages.router)  # x402-protected HTML pages


# Root endpoint
@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.
    """
    return {
        "message": "Streamer Donation System API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
