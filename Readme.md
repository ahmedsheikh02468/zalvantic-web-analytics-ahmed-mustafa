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