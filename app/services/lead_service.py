"""Service for Lead CRUD operations."""

from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadStatus


def create_lead(
    db: Session,
    *,
    original_message: str,
    tattoo_idea: str | None = None,
    body_location: str | None = None,
    size: str | None = None,
    style: str | None = None,
    color_type: str | None = None,
    missing_information: list[str] | None = None,
    summary: dict | None = None,
) -> Lead:
    """Create a new lead and persist it.

    The lead stores both normalized fields (idea, style, size, etc.) and the full
    structured summary payload for traceability.
    """
    lead = Lead(
        original_message=original_message,
        tattoo_idea=tattoo_idea,
        body_location=body_location,
        size=size,
        style=style,
        color_type=color_type,
        missing_information=missing_information or [],
        summary=summary or {},
        status=LeadStatus.NEW,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_all_leads(db: Session) -> list[Lead]:
    """List all leads, ordered by created_at descending."""
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


def get_lead_by_id(db: Session, lead_id: int) -> Lead | None:
    """Get a single lead by its database id."""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead_status(db: Session, lead_id: int, status: LeadStatus) -> Lead | None:
    """Update lead status. Returns None if lead not found."""
    lead = get_lead_by_id(db, lead_id)
    if lead is None:
        return None
    lead.status = status
    db.commit()
    db.refresh(lead)
    return lead
