from sqlalchemy.orm import Session

from app.repos import rating_repo


def list_ratings(db: Session, limit: int = 50):
    return rating_repo.list_ratings(db, limit=limit)


def update_rating(db: Session, user_id: int, reputation: int, league: int):
    return rating_repo.upsert(db, user_id, reputation, league)
