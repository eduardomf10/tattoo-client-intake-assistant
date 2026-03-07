"""Service for analyzing client tattoo intake messages."""

import re

from app.config import settings
from app.schemas.intake import IntakeAnalysisResponse, TattooSummary
from app.services.ai_analyzer import analyze_with_openai
from app.services.extractors import (
    extract_body_location,
    extract_color_preference,
    extract_design_type,
    extract_size,
    extract_style,
    extract_tattoo_idea,
)


def _extract_additional_details(message: str) -> str | None:
    """Extract meaningful additional details from the message."""
    details = []
    message_lower = message.lower()

    if re.search(r"\b(name|nome)\b", message_lower):
        details.append("includes personal name/text")
    if re.search(r"\b(mom|dad|mother|father|mãe|pai|filho|filha|brother|sister)\b", message_lower):
        details.append("memorial or family tribute")
    if re.search(r"\b(date|data|birthday|aniversário)\b", message_lower):
        details.append("dates or anniversary")
    if re.search(r"\b(quote|frase|phrase)\b", message_lower):
        details.append("includes quote or text")

    return "; ".join(details) if details else None


def _build_missing_info_and_questions(
    summary: TattooSummary,
) -> tuple[list[str], list[str]]:
    """Detect missing information and build suggested follow-up questions."""
    missing: list[str] = []
    questions: list[str] = []

    # Missing or vague tattoo idea
    idea = summary.idea.strip()
    if not idea or idea.lower() == "no description provided":
        missing.append("tattoo idea")
        questions.append(
            "Could you describe what you'd like to get? "
            "For example: a specific image, symbol, text, or concept."
        )
    elif len(idea) < 15 and not summary.additional_details:
        missing.append("more detail on the design")
        questions.append(
            "Could you tell me a bit more about the design? "
            "Any references, placement preferences, or meaning behind it?"
        )

    # Unclear design type (text-only vs illustrative vs cover-up)
    if not summary.design_type or summary.design_type == "unknown":
        missing.append("type of request")
        questions.append(
            "Is this going to be text/lettering only, an image or design, "
            "or a cover-up of an existing tattoo?"
        )

    # Missing style (especially relevant for illustrative)
    if not summary.style:
        missing.append("tattoo style")
        questions.append(
            "Do you have a style in mind? "
            "e.g. traditional, realism, minimal, watercolor, blackwork, fine line."
        )

    # Missing body placement
    if not summary.body_location:
        missing.append("body placement")
        questions.append("Where on your body would you like this tattoo?")

    # Missing size
    if not summary.size:
        missing.append("approximate size")
        questions.append(
            "Roughly what size are you thinking? "
            "e.g. small (coin-sized), medium (palm-sized), or large."
        )

    # Missing color preference
    if not summary.color_preference:
        missing.append("color preference")
        questions.append("Would you prefer color or black and grey?")

    return missing, questions


def _analyze_with_rules(message: str) -> IntakeAnalysisResponse:
    """Rule-based analysis. Fallback when OpenAI is unavailable."""
    idea = extract_tattoo_idea(message)
    body_location = extract_body_location(message)
    size = extract_size(message)
    style = extract_style(message)
    color_preference = extract_color_preference(message)
    design_type = extract_design_type(message)
    additional_details = _extract_additional_details(message)

    summary = TattooSummary(
        idea=idea,
        style=style,
        body_location=body_location,
        size=size,
        color_preference=color_preference,
        design_type=design_type,
        additional_details=additional_details,
    )

    # Note: missing-info/question generation is intentionally centralized here so the
    # rule-based path stays consistent and easy to iterate on.
    missing_info, follow_up = _build_missing_info_and_questions(summary)

    return IntakeAnalysisResponse(
        summary=summary,
        missing_information=missing_info,
        follow_up_questions=follow_up,
    )


def analyze_message(message: str) -> IntakeAnalysisResponse:
    """
    Analyze a client message and return structured intake data.

    Uses OpenAI when available. Falls back to rule-based extraction
    if the API is unavailable or misconfigured.
    """
    message = message.strip()
    if not message:
        return IntakeAnalysisResponse(
            summary=TattooSummary(idea="No message provided"),
            missing_information=["message content"],
            follow_up_questions=["Could you describe what tattoo you're interested in?"],
        )

    result = analyze_with_openai(message, settings.openai_api_key)
    if result is not None:
        return result

    return _analyze_with_rules(message)
