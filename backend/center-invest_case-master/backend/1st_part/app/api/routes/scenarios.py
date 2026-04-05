from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.scenarios import ChoiceOut, MissionOut, ScenarioOut
from app.services import scenario_service

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("", response_model=list[ScenarioOut])
def list_scenarios(db: Session = Depends(get_db)):
    return scenario_service.list_scenarios(db)


@router.get("/{scenario_id}", response_model=ScenarioOut)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    scenario = scenario_service.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found"
        )
    return scenario


@router.get("/{scenario_id}/missions", response_model=list[MissionOut])
def list_missions(scenario_id: int, db: Session = Depends(get_db)):
    return scenario_service.list_missions(db, scenario_id)


@router.get("/missions/{mission_id}/choices", response_model=list[ChoiceOut])
def list_choices(mission_id: int, db: Session = Depends(get_db)):
    return scenario_service.list_choices(db, mission_id)
