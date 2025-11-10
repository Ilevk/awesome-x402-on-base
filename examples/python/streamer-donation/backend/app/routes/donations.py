"""
API routes for donation operations.

This module provides endpoints for creating and retrieving donations.
Uses Dependency Injection for service layer access.
"""

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_donation_service, get_streamer_service
from app.models.schemas import (
    DonationMessageCreateSchema,
    DonationMessageSchema,
    DonationResponseSchema,
    ErrorResponseSchema,
)
from app.services.donation_service import DonationService
from app.services.streamer_service import StreamerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["donations"])


@router.post(
    "/donate/{streamer_id}/message",
    response_model=DonationResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseSchema, "description": "Invalid request data"},
        404: {"model": ErrorResponseSchema, "description": "Streamer not found"},
        422: {"model": ErrorResponseSchema, "description": "Validation error"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="Submit donation message",
    description="Record a donation and return the popup message configuration.",
)
async def submit_donation_message(
    streamer_id: str,
    donation_data: DonationMessageCreateSchema,
    donation_service: Annotated[DonationService, Depends(get_donation_service)],
) -> DonationResponseSchema:
    """
    Submit a donation message after payment confirmation.

    This endpoint is called by the frontend after the x402 payment
    is successfully processed on the blockchain.

    Args:
        streamer_id: UUID4 streamer identifier
        donation_data: Donation details including amount, donor, message, and tx hash
        donation_service: Injected DonationService instance

    Returns:
        DonationResponse with popup message configuration

    Raises:
        HTTPException: 400/404/422/500 on various error conditions
    """
    try:
        # Delegate business logic to service layer
        return donation_service.process_donation(streamer_id, donation_data)

    except ValueError as e:
        # Business logic validation errors
        logger.warning(f"Donation validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Failed to process donation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process donation message",
        )


@router.get(
    "/donations/streamer/{streamer_id}",
    response_model=List[DonationMessageSchema],
    responses={
        404: {"model": ErrorResponseSchema, "description": "Streamer not found"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="List donations for a streamer",
    description="Retrieve all donations for a specific streamer (most recent first).",
)
async def list_donations_for_streamer(
    streamer_id: str,
    limit: int = 100,
    donation_service: Annotated[DonationService, Depends(get_donation_service)],
    streamer_service: Annotated[StreamerService, Depends(get_streamer_service)],
) -> List[DonationMessageSchema]:
    """
    List all donations for a streamer.

    Args:
        streamer_id: UUID4 streamer identifier
        limit: Maximum number of donations to return (default: 100, max: 1000)
        donation_service: Injected DonationService instance
        streamer_service: Injected StreamerService instance

    Returns:
        List of DonationMessage models (sorted by timestamp descending)

    Raises:
        HTTPException: 404 if streamer not found, 500 on database error
    """
    try:
        # Validate streamer exists
        streamer = streamer_service.get_streamer_by_id(streamer_id)
        if streamer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Streamer not found: {streamer_id}",
            )

        # Get donations from service
        donations = donation_service.list_donations_for_streamer(streamer_id, limit=limit)

        logger.debug(f"Retrieved {len(donations)} donations for streamer {streamer.name}")
        return donations

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list donations for streamer {streamer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve donations",
        )


@router.get(
    "/donations/{donation_id}",
    response_model=DonationMessageSchema,
    responses={
        404: {"model": ErrorResponseSchema, "description": "Donation not found"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="Get donation by ID",
    description="Retrieve a specific donation by its UUID.",
)
async def get_donation(
    donation_id: str,
    donation_service: Annotated[DonationService, Depends(get_donation_service)],
) -> DonationMessageSchema:
    """
    Get donation by ID.

    Args:
        donation_id: UUID4 donation identifier
        donation_service: Injected DonationService instance

    Returns:
        DonationMessage model

    Raises:
        HTTPException: 404 if not found, 500 on database error
    """
    try:
        donation = donation_service.get_donation_by_id(donation_id)

        if donation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Donation not found: {donation_id}",
            )

        logger.debug(f"Retrieved donation: {donation_id}")
        return donation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get donation {donation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve donation",
        )


@router.get(
    "/donations/streamer/{streamer_id}/stats",
    response_model=dict,
    responses={
        404: {"model": ErrorResponseSchema, "description": "Streamer not found"},
        500: {"model": ErrorResponseSchema, "description": "Internal server error"},
    },
    summary="Get donation statistics",
    description="Get aggregated donation statistics for a streamer.",
)
async def get_donation_stats(
    streamer_id: str,
    donation_service: Annotated[DonationService, Depends(get_donation_service)],
    streamer_service: Annotated[StreamerService, Depends(get_streamer_service)],
) -> dict:
    """
    Get donation statistics for a streamer.

    Args:
        streamer_id: UUID4 streamer identifier
        donation_service: Injected DonationService instance
        streamer_service: Injected StreamerService instance

    Returns:
        Dictionary with total_amount_usd, donation_count, and unique_donors

    Raises:
        HTTPException: 404 if streamer not found, 500 on database error
    """
    try:
        # Validate streamer exists
        streamer = streamer_service.get_streamer_by_id(streamer_id)
        if streamer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Streamer not found: {streamer_id}",
            )

        # Get statistics from service
        stats = donation_service.get_donation_stats(streamer_id)

        logger.debug(f"Retrieved donation stats for streamer {streamer.name}: {stats}")
        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get donation stats for {streamer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve donation statistics",
        )
