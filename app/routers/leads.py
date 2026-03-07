"""Leads API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lead import LeadStatus
from app.schemas.lead import LeadListResponse, LeadResponse, LeadStatusUpdate
from app.services.lead_service import (
    get_all_leads,
    get_lead_by_id,
    update_lead_status,
)

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get(
    "",
    response_model=LeadListResponse,
    summary="List all leads",
    description="Returns all stored leads, ordered by creation date (newest first).",
)
def list_leads(db: Session = Depends(get_db)) -> LeadListResponse:
    """List all leads."""
    leads = get_all_leads(db)
    return LeadListResponse(leads=leads, total=len(leads))


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Get lead by ID",
    description="Returns a single lead by ID. Returns 404 if not found.",
)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> LeadResponse:
    """Get a single lead by ID."""
    lead = get_lead_by_id(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
    summary="Update lead status",
    description="Updates the status of a lead. Returns 404 if not found.",
)
def patch_lead_status(
    lead_id: int,
    body: LeadStatusUpdate,
    db: Session = Depends(get_db),
) -> LeadResponse:
    """Update lead status."""
    lead = update_lead_status(db, lead_id, body.status)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
