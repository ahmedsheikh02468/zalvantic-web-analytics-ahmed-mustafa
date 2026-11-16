from typing import List
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from wa.events import Event
from wa.ingest import ingest_event, ingest_events_batch

router = APIRouter(prefix="/events", tags=["events"])


class BatchEventsRequest(BaseModel):
    events: List[Event] = Field(..., min_length=1, description="List of events to ingest")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(event: Event):
    saved = ingest_event(event)
    return {"status": "accepted", "id": saved.id}


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def create_events_batch(payload: BatchEventsRequest):
    count = ingest_events_batch(payload.events)
    return {"status": "accepted", "inserted": count}
