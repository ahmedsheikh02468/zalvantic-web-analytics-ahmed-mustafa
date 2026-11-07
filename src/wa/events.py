from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field

class Event(BaseModel):
    site_id: str = Field(..., description="Unique identifier for the website")
    event_name: str = Field(..., description="Name of the event (page_view, signup, purchase)")
    anonymous_id: str = Field(..., description="Hashed privacy-friendly anonymous user identifier")
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: datetime = Field(..., description="UTC timestamp of the event")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata")