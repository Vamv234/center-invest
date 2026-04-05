from pydantic import BaseModel


class RatingOut(BaseModel):
    user_id: int
    reputation: int
    league: int

    class Config:
        from_attributes = True
