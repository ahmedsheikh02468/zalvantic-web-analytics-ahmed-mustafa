# Web Analytics and A/B Testing Platform - Week 1

## Overview
This repository contains the Week 1 implementation for the Zalvantic Data Science Internship project. The focus is on defining a privacy-first event schema, building a realistic synthetic traffic generator, and setting up the FastAPI skeleton with SQLite storage.

## Event Schema
All tracked events adhere to the following fixed structure:
- site_id: Unique identifier for the website (str)
- event_name: Name of the event (page_view, signup, purchase) (str)
- anonymous_id: Hashed privacy-friendly anonymous user identifier (str)
- session_id: Unique session identifier based on a 30-minute inactivity rule (str)
- timestamp: UTC timestamp of the event (datetime)
- properties: Flexible metadata dictionary (contains page, source, device, country, etc.) (dict)

### Example Event JSON
{
  "site_id": "site_001",
  "event_name": "page_view",
  "anonymous_id": "anon_00102",
  "session_id": "sess_0000501",
  "timestamp": "2026-11-02T10:15:00Z",
  "properties": {
    "page": "/landing",
    "source": "google organic",
    "device": "mobile",
    "country": "PK"
  }
}

## Privacy - What We Do NOT Store
To maintain strict data privacy compliance:
- No real names, emails, raw IP addresses, or phone numbers are ever collected or stored.
- Only hashed anonymous IDs are used (anonymous_id).
- All data generated in Week 1 is purely synthetic.

## Synthetic Generator & 100k Events
- The generator (src/wa/synth.py) creates users, sessions, sources (google organic, paid ads, social, direct, referral), devices (mobile, desktop, tablet), and conversion funnels (page_view -> signup -> purchase).
- Successfully generated and stored 100,000 synthetic events into the SQLite database (web_analytics.db).

## Setup and Run Instructions
1. Create and activate virtual environment:
   python -m venv .venv
   .venv\Scripts\activate  # On Windows

2. Install dependencies:
   pip install fastapi uvicorn sqlmodel pandas pytest pydantic

3. Run synthetic generator to populate database:
   $env:PYTHONPATH="src"
   python -m wa.synth

4. Run FastAPI application:
   uvicorn wa.app:app --reload

## What I Learned (Week 1)
- Designed a scalable and flexible event schema using Pydantic.
- Built a realistic synthetic traffic generator incorporating source/device distributions and conversion funnels.
- Set up a FastAPI skeleton connected with SQLite using SQLModel and bulk inserts for performance.

## Week 2: Event Ingestion and Core Metrics

### What Was Built
- **Single Event Ingestion (`POST /events`):** Accepts a single JSON event validated against the Pydantic `Event` schema and stores it in SQLite (`events` table).
- **Batch Event Ingestion (`POST /events/batch`):** Accepts a batch list of events (`{"events": [...]}`) with Pydantic validation and bulk-inserts them into SQLite.
- **Core Metrics Engine (`src/wa/metrics.py`):** Computes summary metrics using SQL aggregations (`COUNT(DISTINCT ...)`, `GROUP BY`) instead of Python loops.
- **Summary Endpoint (`GET /metrics/summary`):** Exposes computed metrics across all sites or filtered by an optional `site_id` query parameter.

### Core Metric Definitions
1. **Visits:** Total count of unique `session_id` values.
2. **Unique Users:** Total count of unique `anonymous_id` values.
3. **Bounce Rate:** Ratio of single-event sessions to total visits (`single_event_sessions / total_visits`).
4. **Conversion Rate:** Ratio of sessions containing at least one `signup` or `purchase` event to total visits (`converted_sessions / total_visits`).

### Hand-Calculated Verification Test (`tests/test_ingest.py`)
To verify accuracy, a controlled 5-event test dataset for `test_site` was ingested via `POST /events` and `POST /events/batch`:
- **User `u1`, Session `s1`:** 1 event (`page_view`) -> Bounce session
- **User `u2`, Session `s2`:** 2 events (`page_view`, `signup`) -> Converted session
- **User `u2`, Session `s3`:** 2 events (`page_view`, `purchase`) -> Converted session

**Hand-Calculated vs. `GET /metrics/summary` Output:**
- **Visits:** `3` (unique sessions: `s1`, `s2`, `s3`)
- **Unique Users:** `2` (unique users: `u1`, `u2`)
- **Bounce Rate:** `1 / 3 = 0.3333`
- **Conversion Rate:** `2 / 3 = 0.6667`

### What I Learned (Week 2)
- Implemented modular FastAPI `APIRouter` endpoints (`events.py` and `metrics.py`) with strict Pydantic validation (`422` status on malformed payloads).
- Computed analytics aggregations directly in SQL via SQLModel/SQLAlchemy rather than iterating over rows in Python.
- Verified endpoint correctness using isolated temporary SQLite test databases in `pytest` against hand-calculated metrics.

---

## Setup, Run, and Test Instructions
1. Create and activate virtual environment:
       python -m venv .venv
       .venv\Scripts\activate  # On Windows

2. Install dependencies:
       pip install fastapi uvicorn sqlmodel pandas pytest pydantic httpx2

3. Run synthetic generator to populate database:
       $env:PYTHONPATH="src"
       python -m wa.synth

4. Run FastAPI application:
       $env:PYTHONPATH="src"
       uvicorn wa.app:app --reload

5. Run automated tests:
       $env:PYTHONPATH="src"
       pytest -v