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
from app.models.schemas import ErrorResponseSchema, StreamerSchema
from app.services.streamer_service import StreamerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["streamers"])


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
