from pydantic import BaseModel


class ProgressOut(BaseModel):
    scenario_id: int
    success_rate: int
    mistakes: int

    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    scenario_id: int
    success_rate: int
    mistakes: int
