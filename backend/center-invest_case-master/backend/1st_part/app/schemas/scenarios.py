from pydantic import BaseModel


class ScenarioOut(BaseModel):
    id: int
    title: str
    description: str | None = None

    class Config:
        from_attributes = True


class MissionOut(BaseModel):
    id: int
    scenario_id: int
    title: str
    order_index: int

    class Config:
        from_attributes = True


class ChoiceOut(BaseModel):
    id: int
    attack_id: int
    label: str
    hint: str | None = None

    class Config:
        from_attributes = True
