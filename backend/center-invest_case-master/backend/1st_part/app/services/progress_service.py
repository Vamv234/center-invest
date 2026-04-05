from sqlalchemy.orm import Session

from app.repos import progress_repo


def list_progress(db: Session, user_id: int):
    return progress_repo.list_by_user(db, user_id)


def update_progress(db: Session, user_id: int, scenario_id: int, success_rate: int, mistakes: int):
    return progress_repo.upsert(db, user_id, scenario_id, success_rate, mistakes)
