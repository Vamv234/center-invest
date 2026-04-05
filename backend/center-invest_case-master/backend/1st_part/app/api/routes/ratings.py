from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ratings import RatingOut
from app.services import rating_service

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("", response_model=list[RatingOut])
def get_ratings(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return rating_service.list_ratings(db, limit=limit)
