from sqlalchemy.orm import Session

from app.repos import scenario_repo


def list_scenarios(db: Session):
    return scenario_repo.list_scenarios(db)


def get_scenario(db: Session, scenario_id: int):
    return scenario_repo.get_scenario(db, scenario_id)


def list_missions(db: Session, scenario_id: int):
    return scenario_repo.list_missions(db, scenario_id)


def list_choices(db: Session, mission_id: int):
    return scenario_repo.list_choices(db, mission_id)
