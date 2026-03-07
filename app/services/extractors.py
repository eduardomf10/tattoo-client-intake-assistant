"""Modular extractors for tattoo intake message analysis.

These functions implement a conservative, rule-based fallback for when the AI
analysis is unavailable. The goal is to extract *useful* structure without
over-confident guesses.
"""

import re


# --- Body location extractor ---

BODY_LOCATIONS = [
    # Compound locations first (more specific)
    "inner forearm", "outer forearm", "inner arm", "outer arm",
    "upper arm", "lower arm", "upper back", "lower back",
    "upper thigh", "lower leg", "inner thigh", "outer thigh",
    "upper chest", "lower back", "collarbone", "clavícula",
    "spinal", "spine", "coluna",
    # Simple locations
    "forearm", "braço", "arm", "wrist", "pulso", "shoulder", "ombro",
    "back", "costas", "chest", "peito", "leg", "perna", "thigh", "coxa",
    "ankle", "tornozelo", "neck", "pescoço", "rib", "costela", "calf",
    "hand", "mão", "finger", "dedo", "foot", "pé", "hip", "quadril",
    "bicep", "tricep", "sternum", "esterno",
]

# Sorted by length descending so "inner forearm" matches before "forearm"
BODY_LOCATIONS_SORTED = sorted(BODY_LOCATIONS, key=len, reverse=True)


def extract_body_location(text: str) -> str | None:
    """Extract body placement from message. Prefers more specific matches."""
    text_lower = text.lower()
    for location in BODY_LOCATIONS_SORTED:
        if re.search(rf"\b{re.escape(location)}\b", text_lower):
            return location
    return None


# --- Size extractor ---
# Note: "minimal" is excluded here to avoid conflict with style; use style extractor for it

SIZE_PATTERNS = [
    # (pattern, normalized_value)
    (r"\b(palm[- ]?sized|tamanho\s+de\s+mão)\b", "small"),
    (r"\b(coin[- ]?sized|tamanho\s+de\s+moeda)\b", "small"),
    (r"\b(credit\s+card\s+sized?)\b", "medium"),
    (r"\b(\d+)\s*(cm|centimeters?)\b", "custom"),  # e.g. "5 cm"
    (r"\b(\d+)\s*(inches?|in)\b", "custom"),      # e.g. "3 inches"
    (r"\b(small|pequeno|tiny|mini)\b", "small"),
    (r"\b(medium|médio|medio|average)\b", "medium"),
    (r"\b(large|grande|big|full)\b", "large"),
    (r"\b(sleeve)\b", "large"),
]


def extract_size(text: str) -> str | None:
    """Extract approximate size from message."""
    text_lower = text.lower()
    for pattern, size in SIZE_PATTERNS:
        if re.search(pattern, text_lower):
            return size
    return None


# --- Style extractor ---

STYLE_KEYWORDS = {
    "neo-traditional": "neo-traditional",
    "neo traditional": "neo-traditional",
    "fine line": "fineline",
    "fineline": "fineline",
    "fine-line": "fineline",
    "old school": "traditional",
    "oldschool": "traditional",
    "new school": "new school",
    "traditional": "traditional",
    "realism": "realism",
    "realistic": "realism",
    "realista": "realism",
    "minimal": "minimal",
    "minimalist": "minimal",
    "minimalista": "minimal",
    "linework": "linework",
    "linha": "linework",
    "watercolor": "watercolor",
    "blackwork": "blackwork",
    "dotwork": "dotwork",
    "japanese": "japanese",
    "irezumi": "japanese",
    "tribal": "tribal",
    "geometric": "geometric",
    "geometrico": "geometric",
    "ornamental": "ornamental",
    "script": "script",
    "lettering": "script",
}
# Longer phrases first
STYLE_SORTED = sorted(STYLE_KEYWORDS.items(), key=lambda x: -len(x[0]))


def extract_style(text: str) -> str | None:
    """Extract tattoo style from message."""
    text_lower = text.lower()
    for keyword, style in STYLE_SORTED:
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            return style
    return None


# --- Color preference extractor ---
# Longer phrases first so "black and grey" matches before "black"

COLOR_KEYWORDS = [
    ("black and grey", "black and grey"),
    ("black and gray", "black and grey"),
    ("black & grey", "black and grey"),
    ("black & gray", "black and grey"),
    ("b&g", "black and grey"),
    ("greyscale", "black and grey"),
    ("grayscale", "black and grey"),
    ("preto e branco", "black and grey"),
    ("preto e cinza", "black and grey"),
    ("color", "color"),
    ("colorido", "color"),
    ("colour", "color"),
    ("colored", "color"),
    ("colourful", "color"),
    ("colorful", "color"),
    ("colorida", "color"),
]


def extract_color_preference(text: str) -> str | None:
    """Extract color vs black and grey preference."""
    text_lower = text.lower()
    for keyword, preference in COLOR_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            return preference
    # "black" alone often implies B&G in tattoo context
    if re.search(r"\bblack\s+(only|ink)?\b", text_lower):
        return "black and grey"
    return None


# --- Design type extractor (text_only, illustrative, cover_up, unknown) ---

DESIGN_TYPE_PATTERNS = [
    # Cover-up first (explicit intent)
    (r"\bcover[- ]?up\b", "cover_up"),
    (r"\bcover[- ]?over\b", "cover_up"),
    (r"\bcover\s+existing\b", "cover_up"),
    (r"\bcover\s+old\b", "cover_up"),
    (r"\bcobrir\s+(tatuagem|tattoo)\b", "cover_up"),
    # Text-only (names, quotes, lettering)
    (r"\b(just|only)\s+(text|words|lettering|script|name|names)\b", "text_only"),
    (r"\b(text|lettering|script|words|quote|phrase|name|initial)\s+only\b", "text_only"),
    (r"\b(name|nome|names|quote|frase|lettering|script|initials|date)\s+(tattoo|tatuagem|as\s+a\s+tattoo)\b", "text_only"),
    (r"\b(my\s+)?(kids?\s+)?names?\s+(as\s+a\s+)?(tattoo|tatuagem)\b", "text_only"),
    (r"\btattoo\s+(of\s+)?(my\s+)?(name|names|quote|phrase|initials)\b", "text_only"),
    (r"\bjust\s+(a\s+)?(name|quote|phrase|word)\b", "text_only"),
    (r"\bjust\s+want\s+(my\s+)?(name|names|quote|lettering)\b", "text_only"),
    (r"\bsó\s+(texto|nome|frase)\b", "text_only"),
    # Illustrative (image, design, symbol)
    (r"\b(design|image|picture|symbol|art|drawing|illustration)\b", "illustrative"),
    (r"\b(flower|rose|animal|portrait|dragon|skull)\b", "illustrative"),
    (r"\b(traditional|realism|minimal|watercolor)\s+(style\s+)?(tattoo|piece)\b", "illustrative"),
]


def extract_design_type(text: str) -> str:
    """Classify request as text_only, illustrative, cover_up, or unknown."""
    text_lower = text.lower()
    for pattern, design_type in DESIGN_TYPE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return design_type
    return "unknown"


# --- Tattoo idea extractor ---

IDEA_PATTERNS = [
    # "X tattoo with Y" - capture design including modifiers
    r"(?:i want|want|looking for|quero|gostaria)\s+(?:a\s+)?(.+?)\s+tattoo\s+with\s+(.+?)(?:\s+on\s|\s+for\s|\.|$)",
    r"(?:a\s+)?(.+?)\s+tattoo\s+with\s+(.+?)(?:\s+on\s|\s+for\s|\.|$)",
    # Standard "I want X tattoo"
    r"(?:i want|i'd like|i would like|looking for|interested in|quero|gostaria|procuro)\s+(?:a\s+)?(.+?)(?:\s+tattoo|\s+tattoos|\.|$)",
    r"(?:want|wanting)\s+(?:a\s+)?(.+?)(?:\s+tattoo|\s+tattoos|\.|$)",
    r"(?:thinking about|considering)\s+(?:a\s+)?(.+?)(?:\s+tattoo|\s+tattoos|\.|$)",
    r"(?:get|getting)\s+(?:a\s+)?(.+?)(?:\s+tattoo|\s+tattoos|\.|$)",
    r"(?:a\s+)?(.+?)\s+tattoo(?:\s+with|\s+of|\s+on|,|\.|$)",
    r"(?:tattoo\s+of)\s+(.+)",
    r"(?:tattoo\s+idea|design)\s*[:\s]+(.+)",
]


def extract_tattoo_idea(text: str) -> str:
    """Extract or summarize the main tattoo idea from the message."""
    text = text.strip()
    if not text:
        return "No description provided"

    text_lower = text.lower()
    for pattern in IDEA_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            groups = match.groups()
            # Handle "X tattoo with Y" patterns (2 groups)
            if len(groups) >= 2 and groups[1]:
                idea = f"{groups[0].strip()} with {groups[1].strip()}"
            else:
                idea = groups[0].strip()
            # Clean trailing fragments (on my X, for Y, etc.)
            idea = re.sub(r"\s+(on\s+my\s+\w+|for\s+my\s+\w+)\s*$", "", idea, flags=re.I)
            idea = re.sub(r"\s+(tattoo|on|with|for)\s*$", "", idea, flags=re.I)
            if len(idea) >= 5:
                # Preserve original casing from message
                start = text_lower.find(idea.lower())
                if start >= 0:
                    return text[start : start + len(idea)].strip()
                return idea

    # Fallback: use full message, truncated if long
    if len(text) <= 200:
        return text
    return text[:200].rstrip() + "..."
