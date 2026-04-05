from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ORMSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
