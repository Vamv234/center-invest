from sqlalchemy.orm import Session

from app.models.progress import Rating


def list_ratings(db: Session, limit: int = 50) -> list[Rating]:
    return db.query(Rating).order_by(Rating.reputation.desc()).limit(limit).all()


def get_by_user(db: Session, user_id: int) -> Rating | None:
    return db.query(Rating).filter(Rating.user_id == user_id).first()


def upsert(db: Session, user_id: int, reputation: int, league: int) -> Rating:
    row = get_by_user(db, user_id)
    if row:
        row.reputation = reputation
        row.league = league
        db.commit()
        db.refresh(row)
        return row
    row = Rating(user_id=user_id, reputation=reputation, league=league)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
