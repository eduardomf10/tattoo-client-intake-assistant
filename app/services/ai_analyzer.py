"""OpenAI-powered analysis for tattoo client messages."""

import json
import logging

from app.schemas.intake import IntakeAnalysisResponse, TattooSummary

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You analyze messages from potential tattoo clients. Extract structured information and suggest follow-up questions so artists can respond efficiently.

Return a JSON object with these exact keys:

- idea: Clear, concise summary of what they want (string). Keep the client's wording when useful; normalize vague phrases like "something cool" into a short descriptive line.
- style: Tattoo style if mentioned (string or null). Use: traditional, realism, minimal, watercolor, blackwork, fineline, japanese, script, etc.
- body_location: Body placement if mentioned (string or null). Use: forearm, wrist, arm, upper arm, back, chest, thigh, ankle, etc.
- size: Approximate size if mentioned (string or null). Use: small, medium, large, or their words (e.g. "palm-sized", "3 inches").
- color_preference: "color" or "black and grey" if mentioned (string or null). Infer from "colored", "B&G", "greyscale", "preto e branco", etc.
- design_type: One of "text_only", "illustrative", "cover_up", or "unknown".
  - text_only: only names, quotes, lettering, script, initials, dates.
  - illustrative: images, symbols, figures, flowers, animals, portraits, abstract design.
  - cover_up: covering or reworking an existing tattoo.
  - unknown: cannot tell from the message.
- additional_details: Notable extras (string or null): e.g. "memorial/family tribute", "includes personal name", "reference image".
- missing_information: Array of specific gaps a tattoo artist should clarify (e.g. "body placement", "tattoo style", "approximate size", "color preference", "type of request", "more detail on design"). Only include items not already clear from the message.
- follow_up_questions: Array of 2–4 short, professional, friendly questions the artist could send to the client. Be specific (e.g. "Where on your body would you like this tattoo?" not "Location?").

Use null for any single-value field when unknown. missing_information and follow_up_questions must be arrays of strings.
Respond only with valid JSON, no markdown or extra text."""

USER_PROMPT_TEMPLATE = """Analyze this tattoo client message:

"{message}"
"""


def _parse_ai_response(content: str, original_message: str) -> IntakeAnalysisResponse | None:
    """Parse OpenAI response into IntakeAnalysisResponse. Returns None on parse error."""
    try:
        # Strip markdown code blocks if present
        text = content.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        data = json.loads(text)

        idea = data.get("idea") or "No description provided"
        design_type_raw = data.get("design_type")
        if design_type_raw and str(design_type_raw).lower() in (
            "text_only", "illustrative", "cover_up", "unknown"
        ):
            design_type = str(design_type_raw).lower()
        else:
            design_type = None

        summary = TattooSummary(
            idea=str(idea),
            style=data.get("style"),
            body_location=data.get("body_location"),
            size=data.get("size"),
            color_preference=data.get("color_preference"),
            design_type=design_type,
            additional_details=data.get("additional_details"),
        )

        missing = data.get("missing_information", [])
        if not isinstance(missing, list):
            missing = []
        missing = [str(m) for m in missing]

        questions = data.get("follow_up_questions", [])
        if not isinstance(questions, list):
            questions = []
        questions = [str(q) for q in questions]

        return IntakeAnalysisResponse(
            summary=summary,
            missing_information=missing,
            follow_up_questions=questions,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Failed to parse AI response for message=%r: %s", original_message[:80], e)
        return None


def analyze_with_openai(message: str, api_key: str | None) -> IntakeAnalysisResponse | None:
    """
    Analyze client message using OpenAI. Returns None if unavailable or invalid response.
    """
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        # JSON mode ensures responses are machine-parseable and stable for API usage.
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(message=message)},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content
        if not content:
            return None
        return _parse_ai_response(content, message)
    except Exception as e:
        logger.warning("OpenAI API unavailable: %s", e)
        return None
