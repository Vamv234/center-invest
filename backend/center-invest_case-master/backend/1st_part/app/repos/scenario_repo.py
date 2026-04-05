from sqlalchemy.orm import Session

from app.models.scenario import Attack, Choice, Mission, Scenario


def list_scenarios(db: Session) -> list[Scenario]:
    return db.query(Scenario).all()


def get_scenario(db: Session, scenario_id: int) -> Scenario | None:
    return db.query(Scenario).filter(Scenario.id == scenario_id).first()


def list_missions(db: Session, scenario_id: int) -> list[Mission]:
    return (
        db.query(Mission)
        .filter(Mission.scenario_id == scenario_id)
        .order_by(Mission.order_index.asc())
        .all()
    )


def list_choices(db: Session, mission_id: int) -> list[Choice]:
    attack_ids = (
        db.query(Attack.id).filter(Attack.mission_id == mission_id).subquery()
    )
    return db.query(Choice).filter(Choice.attack_id.in_(attack_ids)).all()
