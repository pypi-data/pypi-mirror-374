from pydantic import BaseModel, Field


class ConnectionCheck(BaseModel):
    is_connected: bool = Field(..., description="Whether database is connected")
    duration: float = Field(..., ge=0.0, description="Duration")
