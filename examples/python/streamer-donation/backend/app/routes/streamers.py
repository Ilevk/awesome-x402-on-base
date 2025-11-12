"""
API routes for streamer operations.

This module provides endpoints for retrieving streamer information.
Uses Dependency Injection for service layer access.
"""

import dataclasses
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_streamer_service
from app.models.schemas import (
    ErrorResponseSchema,
    StreamerCreateSchema,
    StreamerSchema,
)
from app.services.streamer_service import StreamerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["streamers"])


@router.post(
    "/streamer",
    response_model=StreamerSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseSchema, "description": "Invalid request data"},
        409: {"model": ErrorResponseSchema, "description": "Wallet address already registered"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="Register a new streamer",
    description="Create a new streamer profile with donation tiers and configuration.",
)
async def create_streamer(
    streamer_data: StreamerCreateSchema,
    streamer_service: Annotated[StreamerService, Depends(get_streamer_service)],
) -> StreamerSchema:
    """
    Register a new streamer.

    This endpoint allows creating a new streamer profile with customized
    donation tiers and thank you message. The wallet address must be unique.

    Args:
        streamer_data: Streamer profile data (name, wallet, tiers, etc.)
        streamer_service: Injected StreamerService instance

    Returns:
        Created streamer with generated UUID

    Raises:
        HTTPException: 400 for invalid data, 409 for duplicate wallet, 500 on error
    """
    try:
        # Check if wallet address already registered
        existing_streamer = streamer_service.get_streamer_by_wallet(
            streamer_data.wallet_address
        )
        if existing_streamer is not None:
            logger.warning(
                f"Duplicate wallet registration attempted: {streamer_data.wallet_address}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Wallet address {streamer_data.wallet_address} is already registered",
            )

        # Convert Pydantic schemas to dicts for service layer
        tier_dicts = [
            {
                "amount_usd": tier.amount_usd,
                "popup_message": tier.popup_message,
                "duration_ms": tier.duration_ms,
            }
            for tier in streamer_data.donation_tiers
        ]

        # Create streamer (service will generate UUID and validate tiers)
        streamer = streamer_service.create_streamer(
            name=streamer_data.name,
            wallet_address=streamer_data.wallet_address,
            platforms=streamer_data.platforms,
            donation_tiers=tier_dicts,
            avatar_url=str(streamer_data.avatar_url) if streamer_data.avatar_url else None,
            thank_you_message=streamer_data.thank_you_message,
        )

        logger.info(f"Streamer created: {streamer.name} ({streamer.id})")

        # Convert DTO to Pydantic schema
        return StreamerSchema(**dataclasses.asdict(streamer))

    except HTTPException:
        raise
    except ValueError as e:
        # Service-level validation errors
        logger.error(f"Validation error creating streamer: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to create streamer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create streamer profile",
        )


@router.get(
    "/streamer/{streamer_id}",
    response_model=StreamerSchema,
    responses={
        404: {"model": ErrorResponseSchema, "description": "Streamer not found"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="Get streamer information",
    description="Retrieve streamer profile and donation configuration by UUID.",
)
async def get_streamer(
    streamer_id: str,
    streamer_service: Annotated[StreamerService, Depends(get_streamer_service)],
) -> StreamerSchema:
    """
    Get streamer information by ID.

    Args:
        streamer_id: UUID4 streamer identifier
        streamer_service: Injected StreamerService instance

    Returns:
        Streamer model with profile and donation tiers

    Raises:
        HTTPException: 404 if streamer not found, 500 on database error
    """
    try:
        streamer = streamer_service.get_streamer_by_id(streamer_id)

        if streamer is None:
            logger.warning(f"Streamer not found: {streamer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Streamer not found: {streamer_id}",
            )

        logger.debug(f"Retrieved streamer: {streamer.name} ({streamer_id})")

        # Convert DTO to Pydantic schema
        return StreamerSchema(**dataclasses.asdict(streamer))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get streamer {streamer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve streamer information",
        )


@router.get(
    "/streamers",
    response_model=list[StreamerSchema],
    responses={
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="List all streamers",
    description="Retrieve a list of all registered streamers (limited to 100).",
)
async def list_streamers(
    streamer_service: Annotated[StreamerService, Depends(get_streamer_service)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[StreamerSchema]:
    """
    List all streamers.

    Args:
        limit: Maximum number of streamers to return (default: 100, max: 1000)
        streamer_service: Injected StreamerService instance

    Returns:
        List of Streamer models

    Raises:
        HTTPException: 500 on database error
    """
    try:
        streamers = streamer_service.list_streamers(limit=limit)

        logger.debug(f"Retrieved {len(streamers)} streamers")

        # Convert DTOs to Pydantic schemas
        return [
            StreamerSchema(**dataclasses.asdict(streamer))
            for streamer in streamers
        ]

    except Exception as e:
        logger.error(f"Failed to list streamers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve streamers list",
        )


@router.get(
    "/streamer/by-wallet/{wallet_address}",
    response_model=StreamerSchema,
    responses={
        404: {"model": ErrorResponseSchema, "description": "Streamer not found"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="Get streamer by wallet address",
    description="Retrieve streamer profile by Ethereum wallet address.",
)
async def get_streamer_by_wallet(
    wallet_address: str,
    streamer_service: Annotated[StreamerService, Depends(get_streamer_service)],
) -> StreamerSchema:
    """
    Get streamer by wallet address.

    Args:
        wallet_address: Ethereum wallet address (0x...)
        streamer_service: Injected StreamerService instance

    Returns:
        Streamer model

    Raises:
        HTTPException: 404 if not found, 500 on database error
    """
    try:
        streamer = streamer_service.get_streamer_by_wallet(wallet_address)

        if streamer is None:
            logger.warning(f"Streamer not found for wallet: {wallet_address}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No streamer found with wallet: {wallet_address}",
            )

        logger.debug(f"Retrieved streamer by wallet: {streamer.name}")

        # Convert DTO to Pydantic schema
        return StreamerSchema(**dataclasses.asdict(streamer))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get streamer by wallet {wallet_address}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve streamer information",
        )
