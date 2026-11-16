import json
from typing import List
from sqlmodel import Session
from wa.db import engine, EventDB
from wa.events import Event


def ingest_event(event: Event, session: Session | None = None) -> EventDB:
    db_event = EventDB(
        site_id=event.site_id,
        event_name=event.event_name,
        anonymous_id=event.anonymous_id,
        session_id=event.session_id,
        timestamp=event.timestamp,
        properties_json=json.dumps(event.properties),
    )
    if session is not None:
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event

    with Session(engine) as new_session:
        new_session.add(db_event)
        new_session.commit()
        new_session.refresh(db_event)
        return db_event


def ingest_events_batch(events: List[Event], session: Session | None = None) -> int:
    db_events = [
        EventDB(
            site_id=e.site_id,
            event_name=e.event_name,
            anonymous_id=e.anonymous_id,
            session_id=e.session_id,
            timestamp=e.timestamp,
            properties_json=json.dumps(e.properties),
        )
        for e in events
    ]
    if session is not None:
        session.add_all(db_events)
        session.commit()
        return len(db_events)

    with Session(engine) as new_session:
        new_session.add_all(db_events)
        new_session.commit()
        return len(db_events)
