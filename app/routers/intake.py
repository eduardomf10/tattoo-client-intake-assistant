"""Intake API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.intake import IntakeMessageRequest, IntakeAnalysisResponse
from app.services.intake_service import analyze_message
from app.services.lead_service import create_lead

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post(
    "/analyze-message",
    response_model=IntakeAnalysisResponse,
    summary="Analyze client message",
    description="Receives a client message describing a tattoo idea and returns "
    "structured information with extracted data, missing info, and follow-up questions. "
    "Saves the lead to the database.",
)
def analyze_intake_message(
    request: IntakeMessageRequest,
    db: Session = Depends(get_db),
) -> IntakeAnalysisResponse:
    """
    Analyze a client message and return structured tattoo intake data.

    Extracts tattoo idea, style, body location, size, and color preference.
    Returns missing information and suggested follow-up questions.
    Saves the lead to the database.
    """
    result = analyze_message(request.message)

    lead = create_lead(
        db,
        original_message=request.message,
        tattoo_idea=result.summary.idea,
        body_location=result.summary.body_location,
        size=result.summary.size,
        style=result.summary.style,
        color_type=result.summary.color_preference,
        missing_information=result.missing_information,
        summary=result.summary.model_dump(),
    )

    return IntakeAnalysisResponse(
        lead_id=lead.id,
        summary=result.summary,
        missing_information=result.missing_information,
        follow_up_questions=result.follow_up_questions,
    )
