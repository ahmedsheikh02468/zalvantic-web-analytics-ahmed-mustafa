from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session

sqlite_file_name = "web_analytics.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

class EventDB(SQLModel, table=True):
    __tablename__ = "events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    site_id: str = Field(index=True)
    event_name: str
    anonymous_id: str
    session_id: str
    timestamp: datetime = Field(index=True)
    properties_json: str  # Storing properties dictionary as JSON string

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)