from sqlalchemy.orm import Session

from app.models.progress import Progress


def get_by_user_and_scenario(db: Session, user_id: int, scenario_id: int) -> Progress | None:
    return (
        db.query(Progress)
        .filter(Progress.user_id == user_id, Progress.scenario_id == scenario_id)
        .first()
    )


def upsert(db: Session, user_id: int, scenario_id: int, success_rate: int, mistakes: int) -> Progress:
    row = get_by_user_and_scenario(db, user_id, scenario_id)
    if row:
        row.success_rate = success_rate
        row.mistakes = mistakes
        db.commit()
        db.refresh(row)
        return row
    row = Progress(
        user_id=user_id,
        scenario_id=scenario_id,
        success_rate=success_rate,
        mistakes=mistakes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_by_user(db: Session, user_id: int) -> list[Progress]:
    return db.query(Progress).filter(Progress.user_id == user_id).all()
