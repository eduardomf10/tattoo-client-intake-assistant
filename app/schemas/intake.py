"""Pydantic schemas for the intake analysis endpoint."""

from pydantic import BaseModel, Field


class IntakeMessageRequest(BaseModel):
    """Request model for the analyze-message endpoint."""

    message: str = Field(
        ...,
        description="Raw message from the client describing their tattoo idea",
        min_length=1,
        examples=["I want a small rose tattoo with my mom's name on my forearm."],
    )


class TattooSummary(BaseModel):
    """Structured summary of the tattoo request."""

    idea: str = Field(
        ...,
        description="Main tattoo idea or design description",
    )
    style: str | None = Field(
        default=None,
        description="Tattoo style if detectable (e.g., traditional, minimal, realism)",
    )
    body_location: str | None = Field(
        default=None,
        description="Preferred body placement",
    )
    size: str | None = Field(
        default=None,
        description="Approximate size (e.g., small, medium, large)",
    )
    color_preference: str | None = Field(
        default=None,
        description="Color or black and grey preference",
    )
    design_type: str | None = Field(
        default=None,
        description="Request type: text_only, illustrative, cover_up, or unknown",
    )
    additional_details: str | None = Field(
        default=None,
        description="Any extra details mentioned",
    )


class IntakeAnalysisResponse(BaseModel):
    """Response model for the analyze-message endpoint."""

    lead_id: int | None = Field(
        default=None,
        description="ID of the saved lead in the database",
    )
    summary: TattooSummary = Field(
        ...,
        description="Structured summary of the tattoo request",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="List of information that should be clarified with the client",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Suggested questions to ask the client",
    )
