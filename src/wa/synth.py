import random
import json
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from .db import engine, create_db_and_tables, EventDB

def generate_events(total_events: int = 100000, site_id: str = "site_001"):
    print(f"Generating {total_events} synthetic events for {site_id}...")
    create_db_and_tables()

    sources = ["google organic", "paid ads", "social", "direct", "referral"]
    source_weights = [0.40, 0.20, 0.20, 0.10, 0.10]

    devices = ["mobile", "desktop", "tablet"]
    device_weights = [0.60, 0.30, 0.10]

    countries = ["PK", "US", "UK", "IN", "AE"]
    
    num_users = int(total_events / 5)
    users = [f"anon_{i:05d}" for i in range(1, num_users + 1)]

    events_batch = []
    base_time = datetime.now(timezone.utc) - timedelta(days=7)
    
    event_count = 0
    session_counter = 1

    while event_count < total_events:
        user_id = random.choice(users)
        session_id = f"sess_{session_counter:07d}"
        session_counter += 1

        source = random.choices(sources, weights=source_weights)[0]
        device = random.choices(devices, weights=device_weights)[0]
        country = random.choice(countries)

        session_time = base_time + timedelta(seconds=random.randint(0, 7 * 24 * 3600))

        # Funnel: page_view -> signup -> purchase
        props1 = {"page": "/landing", "source": source, "device": device, "country": country}
        events_batch.append(EventDB(
            site_id=site_id,
            event_name="page_view",
            anonymous_id=user_id,
            session_id=session_id,
            timestamp=session_time,
            properties_json=json.dumps(props1)
        ))
        event_count += 1
        if event_count >= total_events:
            break

        if random.random() < 0.40:
            session_time += timedelta(minutes=random.randint(1, 3))
            props2 = {"page": "/signup", "source": source, "device": device, "country": country}
            events_batch.append(EventDB(
                site_id=site_id,
                event_name="page_view",
                anonymous_id=user_id,
                session_id=session_id,
                timestamp=session_time,
                properties_json=json.dumps(props2)
            ))
            event_count += 1
            if event_count >= total_events:
                break

            if random.random() < 0.25:
                session_time += timedelta(minutes=random.randint(1, 5))
                props3 = {"page": "/signup-success", "source": source, "device": device, "country": country}
                events_batch.append(EventDB(
                    site_id=site_id,
                    event_name="signup",
                    anonymous_id=user_id,
                    session_id=session_id,
                    timestamp=session_time,
                    properties_json=json.dumps(props3)
                ))
                event_count += 1
                if event_count >= total_events:
                    break

                if random.random() < 0.15:
                    session_time += timedelta(minutes=random.randint(2, 10))
                    props4 = {"page": "/checkout", "source": source, "device": device, "country": country}
                    events_batch.append(EventDB(
                        site_id=site_id,
                        event_name="purchase",
                        anonymous_id=user_id,
                        session_id=session_id,
                        timestamp=session_time,
                        properties_json=json.dumps(props4)
                    ))
                    event_count += 1
                    if event_count >= total_events:
                        break

    print(f"Inserting {len(events_batch)} events into SQLite database...")
    with Session(engine) as session:
        session.add_all(events_batch)
        session.commit()
    
    print("Successfully generated and stored 100,000 synthetic events!")

if __name__ == "__main__":
    generate_events()