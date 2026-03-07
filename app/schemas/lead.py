"""Pydantic schemas for Lead endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.lead import LeadStatus


class LeadSummarySchema(BaseModel):
    """Summary object stored in lead (tattoo idea, style, etc.)."""

    idea: str | None = None
    style: str | None = None
    body_location: str | None = None
    size: str | None = None
    color_preference: str | None = None
    additional_details: str | None = None


class LeadResponse(BaseModel):
    """Response schema for a single lead."""

    id: int
    original_message: str
    tattoo_idea: str | None
    body_location: str | None
    size: str | None
    style: str | None
    color_type: str | None
    missing_information: list[str]
    summary: dict
    status: LeadStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadStatusUpdate(BaseModel):
    """Request schema for PATCH lead status."""

    status: LeadStatus = Field(
        ...,
        description="New status for the lead",
    )


class LeadListResponse(BaseModel):
    """Response schema for lead list endpoint."""

    leads: list[LeadResponse]
    total: int
