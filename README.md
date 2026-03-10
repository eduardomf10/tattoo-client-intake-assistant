# Tattoo Client Intake Assistant

**REST API** that structures and qualifies incoming messages from tattoo studio clients. Built with **FastAPI**, **SQLAlchemy**, and **OpenAI**, with a rule-based fallback for reliability.

---

## Project Overview

The Tattoo Client Intake Assistant is a backend service that turns unstructured client messages (e.g. *"hey want something cool on my arm"*) into structured intake data. It extracts tattoo idea, style, placement, size, color preference, and request type (text-only, illustrative, cover-up); detects missing information; and suggests follow-up questions so artists can respond quickly and consistently. Each analyzed message is stored as a **lead** with a configurable status workflow.

The system uses **OpenAI** (GPT-4o-mini) when an API key is available and falls back to **rule-based extraction** when the API is unavailable, so intake keeps working offline or without external services.

---

## Demo

Watch a short demo of the API in action:  
https://youtu.be/rp05D_FTjn4

---

## Business Problem

Tattoo artists and studios often receive vague or fragmented messages from potential clients. Inquiries like *"I want something for my mom"* or *"maybe a small one on my wrist"* lack:

- A clear design concept or idea  
- Preferred style (traditional, realism, minimal, etc.)  
- Body placement and approximate size  
- Color vs. black-and-grey preference  
- Whether the request is text/lettering, an image/design, or a cover-up  

Manually chasing these details is time-consuming and inconsistent. Slow or generic replies can cause leads to go cold. Studios need a way to **normalize and qualify** every message so artists can prioritize and respond with the right questions.

---

## Solution

This API addresses the problem by:

1. **Analyzing** each client message and producing a **structured summary** (idea, style, body location, size, color preference, design type).
2. **Identifying gaps** — listing what information is still missing so the artist knows what to ask.
3. **Suggesting follow-up questions** — concrete, professional questions the artist can send to the client.
4. **Persisting leads** — saving every analyzed message as a lead in SQLite with status (`new`, `awaiting_client_reply`, `in_conversation`, `scheduled`, `closed`, `lost`).

Analysis is **AI-first** (OpenAI) with a **rule-based fallback**: if the API key is missing or the request fails, the service uses keyword and pattern-based extractors so the intake pipeline never breaks.

---

## Features

| Feature | Description |
|--------|-------------|
| **Structured analysis** | Extracts idea, style, body location, size, color type, and design type (text_only / illustrative / cover_up / unknown). |
| **Missing information detection** | Returns a list of fields that should be clarified (e.g. body placement, style, size, color, type of request). |
| **Follow-up questions** | Generates 2–4 specific, professional questions the artist can send to the client. |
| **AI + fallback** | OpenAI-powered analysis when configured; rule-based extraction when the API is unavailable or not configured. |
| **Lead storage** | Every analyzed message is saved as a lead with full summary and missing-info data. |
| **Lead status workflow** | Status can be updated via PATCH (`new` → `awaiting_client_reply` → `in_conversation` → `scheduled` / `closed` / `lost`). |
| **API documentation** | OpenAPI (Swagger) and ReDoc at `/docs` and `/redoc`. |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Framework** | FastAPI |
| **Database** | SQLite, SQLAlchemy 2.x (ORM, migrations via `create_all`) |
| **Validation** | Pydantic v2 |
| **AI** | OpenAI API (GPT-4o-mini), JSON-mode responses |
| **Server** | Uvicorn (ASGI) |

---

## Project Structure

```
tattoo-client-intake-assistant/
├── app/
│   ├── main.py              # FastAPI app, lifespan, router registration
│   ├── config.py            # Settings (DB URL, OpenAI API key from env)
│   ├── database.py          # SQLAlchemy engine, session factory, get_db, init_db
│   ├── routers/
│   │   ├── intake.py        # POST /intake/analyze-message
│   │   └── leads.py         # GET /leads, GET /leads/{id}, PATCH /leads/{id}/status
│   ├── services/
│   │   ├── ai_analyzer.py   # OpenAI integration, prompt, response parsing
│   │   ├── extractors.py    # Rule-based extractors (idea, location, size, style, color, design_type)
│   │   ├── intake_service.py# Orchestrates AI vs rule-based analysis, missing info & questions
│   │   └── lead_service.py  # Lead CRUD (create, list, get by id, update status)
│   ├── schemas/
│   │   ├── intake.py        # IntakeMessageRequest, TattooSummary, IntakeAnalysisResponse
│   │   └── lead.py          # LeadResponse, LeadListResponse, LeadStatusUpdate
│   └── models/
│       └── lead.py          # Lead SQLAlchemy model, LeadStatus enum
├── requirements.txt
├── .env.example             # OPENAI_API_KEY, optional DATABASE_URL
├── leads.db                 # SQLite DB (created on first run)
└── README.md
```

---

## How to Run Locally

**Requirements:** Python 3.10+

1. **Clone and enter the project**
   ```bash
   cd tattoo-client-intake-assistant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   ```
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Windows (CMD): `venv\Scripts\activate.bat`
   - Linux/macOS: `source venv/bin/activate`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional)**
   - Copy `.env.example` to `.env` and set `OPENAI_API_KEY` for AI-powered analysis.
   - Or set in shell: `export OPENAI_API_KEY="sk-..."` (Linux/macOS) or `$env:OPENAI_API_KEY = "sk-..."` (PowerShell).
   - If unset, the API still runs using rule-based analysis only.

5. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```
   - API base: `http://127.0.0.1:8000`
   - Swagger UI: http://127.0.0.1:8000/docs  
   - ReDoc: http://127.0.0.1:8000/redoc  

The SQLite database `leads.db` is created automatically on first request.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check; returns service name and docs link. |
| `POST` | `/intake/analyze-message` | Analyzes message, returns structured summary + missing info + follow-up questions; persists a new lead. |
| `GET` | `/leads` | Lists all leads (newest first). |
| `GET` | `/leads/{lead_id}` | Returns one lead by ID; `404` if not found. |
| `PATCH` | `/leads/{lead_id}/status` | Updates lead status; body `{"status": "..."}`; `404` if not found. |

**Lead status values:** `new`, `awaiting_client_reply`, `in_conversation`, `scheduled`, `closed`, `lost`.

---

## Example Request and Response

### POST /intake/analyze-message

**Request:**

```bash
curl -X POST "http://127.0.0.1:8000/intake/analyze-message" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a small rose tattoo with my moms name on my forearm."}'
```

**Response (200):**

```json
{
  "lead_id": 1,
  "summary": {
    "idea": "small rose with my mom's name",
    "style": null,
    "body_location": "forearm",
    "size": "small",
    "color_preference": null,
    "design_type": "illustrative",
    "additional_details": "includes personal name/text; memorial or family tribute"
  },
  "missing_information": [
    "tattoo style",
    "color preference"
  ],
  "follow_up_questions": [
    "Do you have a style in mind? e.g. traditional, realism, minimal, watercolor, blackwork, fine line.",
    "Would you prefer color or black and grey?"
  ]
}
```

### GET /leads

**Response (200):**

```json
{
  "leads": [
    {
      "id": 1,
      "original_message": "I want a small rose tattoo with my moms name on my forearm.",
      "tattoo_idea": "small rose with my mom's name",
      "body_location": "forearm",
      "size": "small",
      "style": null,
      "color_type": null,
      "missing_information": ["tattoo style", "color preference"],
      "summary": {
        "idea": "small rose with my mom's name",
        "style": null,
        "body_location": "forearm",
        "size": "small",
        "color_preference": null,
        "design_type": "illustrative",
        "additional_details": "includes personal name/text; memorial or family tribute"
      },
      "status": "new",
      "created_at": "2026-03-07T12:00:00"
    }
  ],
  "total": 1
}
```

### PATCH /leads/1/status

**Request:**

```bash
curl -X PATCH "http://127.0.0.1:8000/leads/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_conversation"}'
```

**Response (200):** Full lead object with updated `status`.

---

## Future Improvements

- **Authentication & authorization** — API keys or JWT for studio staff; optional per-studio multi-tenancy.
- **PostgreSQL** — Swap SQLite for PostgreSQL for production and use Alembic for migrations.
- **Pagination** — Cursor or offset pagination for `GET /leads` and optional filtering by status/date.
- **Webhooks / notifications** — Notify artists when a new lead is created or when status changes.
- **Richer AI** — Optional use of vision API for reference images; fine-tuned or few-shot prompts for studio-specific terminology.
- **Audit log** — Log status changes and analysis source (AI vs fallback) for debugging and analytics.
- **Rate limiting** — Per-IP or per-key limits on `/intake/analyze-message` to protect the OpenAI quota.
- **Tests** — Unit tests for extractors and intake service; integration tests for endpoints with a test DB.

---

## License

MIT
