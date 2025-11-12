"""
HTML page routes protected by x402 payment protocol.

This module provides user-facing HTML pages that require payment via x402:
- Donation page: Protected page where users can make donations
- Dashboard: View donation history and statistics
- Thank you page: Post-donation confirmation

Author: Logan (Base Korea Developer Ambassador)
License: MIT
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.dependencies import get_streamer_service
from app.services.streamer_service import StreamerService

# Create router
router = APIRouter(prefix="/donate", tags=["pages"])

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")


@router.get("/{streamer_id}", response_class=HTMLResponse)
async def donation_page(
    request: Request,
    streamer_id: str,
    streamer_service: StreamerService = Depends(get_streamer_service),
) -> HTMLResponse:
    """
    Protected donation page requiring x402 payment.

    This endpoint is protected by x402 middleware. Users must pay $0.001
    to access the donation page. After payment, they can make donations
    to the streamer.

    Args:
        request: FastAPI request object
        streamer_id: Unique identifier for the streamer
        streamer_service: Injected streamer service

    Returns:
        HTMLResponse: Rendered donation page template

    Raises:
        HTTPException: 404 if streamer not found
    """
    # Verify streamer exists
    streamer = streamer_service.get_streamer_by_id(streamer_id)
    if not streamer:
        raise HTTPException(
            status_code=404, detail=f"Streamer with ID '{streamer_id}' not found"
        )

    # Render donation page with streamer data
    return templates.TemplateResponse(
        "donate.html",
        {
            "request": request,
            "streamer": streamer,
            "donation_tiers": streamer.donation_tiers,
        },
    )


@router.get("/dashboard/{streamer_id}", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    streamer_id: str,
    streamer_service: StreamerService = Depends(get_streamer_service),
) -> HTMLResponse:
    """
    Streamer dashboard showing donation history and statistics.

    Args:
        request: FastAPI request object
        streamer_id: Unique identifier for the streamer
        streamer_service: Injected streamer service

    Returns:
        HTMLResponse: Rendered dashboard template

    Raises:
        HTTPException: 404 if streamer not found
    """
    # Verify streamer exists
    streamer = streamer_service.get_streamer_by_id(streamer_id)
    if not streamer:
        raise HTTPException(
            status_code=404, detail=f"Streamer with ID '{streamer_id}' not found"
        )

    # Render dashboard page with streamer data
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "streamer": streamer,
        },
    )


@router.get("/thank-you/{donation_id}", response_class=HTMLResponse)
async def thank_you_page(
    request: Request,
    donation_id: str,
) -> HTMLResponse:
    """
    Thank you page shown after successful donation.

    Args:
        request: FastAPI request object
        donation_id: Unique identifier for the donation

    Returns:
        HTMLResponse: Rendered thank you page template
    """
    # Render thank you page
    return templates.TemplateResponse(
        "thank_you.html",
        {
            "request": request,
            "donation_id": donation_id,
        },
    )
