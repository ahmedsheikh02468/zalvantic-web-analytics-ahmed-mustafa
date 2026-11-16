from typing import Optional
from sqlmodel import Session, select, func
from wa.db import engine, EventDB


def compute_summary_metrics(
    site_id: Optional[str] = None,
    session: Optional[Session] = None,
) -> dict:
    def _run_queries(db: Session) -> dict:
        base_filter = []
        if site_id:
            base_filter.append(EventDB.site_id == site_id)

        # 1. Visits: Total unique session_id
        visits_stmt = select(func.count(func.distinct(EventDB.session_id))).where(*base_filter)
        visits = db.exec(visits_stmt).one() or 0

        # 2. Unique Users: Total unique anonymous_id
        users_stmt = select(func.count(func.distinct(EventDB.anonymous_id))).where(*base_filter)
        unique_users = db.exec(users_stmt).one() or 0

        if visits == 0:
            return {
                "site_id": site_id or "all",
                "visits": 0,
                "unique_users": 0,
                "bounce_rate": 0.0,
                "conversion_rate": 0.0,
            }

        # 3. Bounce Rate: Single-event sessions / total visits
        session_counts_subq = (
            select(EventDB.session_id, func.count(EventDB.id).label("event_count"))
            .where(*base_filter)
            .group_by(EventDB.session_id)
            .subquery()
        )
        bounced_stmt = select(func.count()).select_from(session_counts_subq).where(
            session_counts_subq.c.event_count == 1
        )
        bounced_sessions = db.exec(bounced_stmt).one() or 0
        bounce_rate = round(bounced_sessions / visits, 4)

        # 4. Conversion Rate: Sessions with signup or purchase / total visits
        converted_stmt = select(func.count(func.distinct(EventDB.session_id))).where(
            *base_filter,
            EventDB.event_name.in_(["signup", "purchase"]),
        )
        converted_sessions = db.exec(converted_stmt).one() or 0
        conversion_rate = round(converted_sessions / visits, 4)

        return {
            "site_id": site_id or "all",
            "visits": visits,
            "unique_users": unique_users,
            "bounce_rate": bounce_rate,
            "conversion_rate": conversion_rate,
        }

    if session is not None:
        return _run_queries(session)

    with Session(engine) as new_session:
        return _run_queries(new_session)
