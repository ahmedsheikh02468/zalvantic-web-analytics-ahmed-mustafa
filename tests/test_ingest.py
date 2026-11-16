import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
import wa.db as db_module
import wa.ingest as ingest_module
import wa.metrics as metrics_module
from wa.app import app


@pytest.fixture(name="client")
def client_fixture(tmp_path):
    test_db_path = tmp_path / "test_analytics.db"
    test_engine = create_engine(f"sqlite:///{test_db_path}", echo=False)
    SQLModel.metadata.create_all(test_engine)

    # Point app modules to isolated temporary test DB
    db_module.engine = test_engine
    ingest_module.engine = test_engine
    metrics_module.engine = test_engine

    with TestClient(app) as client:
        yield client


def test_single_and_batch_ingest_and_summary_matches_hand_calculation(client):
    # 1. Single event via POST /events (User u1, Session s1 -> 1 event = Bounce)
    single_event = {
        "site_id": "test_site",
        "event_name": "page_view",
        "anonymous_id": "u1",
        "session_id": "s1",
        "timestamp": "2026-11-10T10:00:00Z",
        "properties": {"page": "/home"},
    }
    res_single = client.post("/events", json=single_event)
    assert res_single.status_code == 201
    assert res_single.json()["status"] == "accepted"

    # 2. Batch events via POST /events/batch (User u2 across s2 and s3 -> both converted)
    batch_payload = {
        "events": [
            {
                "site_id": "test_site",
                "event_name": "page_view",
                "anonymous_id": "u2",
                "session_id": "s2",
                "timestamp": "2026-11-10T10:05:00Z",
                "properties": {"page": "/pricing"},
            },
            {
                "site_id": "test_site",
                "event_name": "signup",
                "anonymous_id": "u2",
                "session_id": "s2",
                "timestamp": "2026-11-10T10:06:00Z",
                "properties": {"plan": "free"},
            },
            {
                "site_id": "test_site",
                "event_name": "page_view",
                "anonymous_id": "u2",
                "session_id": "s3",
                "timestamp": "2026-11-10T12:00:00Z",
                "properties": {"page": "/checkout"},
            },
            {
                "site_id": "test_site",
                "event_name": "purchase",
                "anonymous_id": "u2",
                "session_id": "s3",
                "timestamp": "2026-11-10T12:02:00Z",
                "properties": {"amount": 49.0},
            },
        ]
    }
    res_batch = client.post("/events/batch", json=batch_payload)
    assert res_batch.status_code == 201
    assert res_batch.json() == {"status": "accepted", "inserted": 4}

    # 3. Verify GET /metrics/summary matches hand-calculated numbers
    res_summary = client.get("/metrics/summary", params={"site_id": "test_site"})
    assert res_summary.status_code == 200
    data = res_summary.json()

    assert data["visits"] == 3
    assert data["unique_users"] == 2
    assert data["bounce_rate"] == 0.3333
    assert data["conversion_rate"] == 0.6667


def test_pydantic_validation_rejects_invalid_event(client):
    invalid_event = {
        "site_id": "test_site",
        "event_name": "page_view",
        # Missing required fields: anonymous_id, session_id, timestamp
    }
    res = client.post("/events", json=invalid_event)
    assert res.status_code == 422
