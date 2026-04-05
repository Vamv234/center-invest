from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.progress import ProgressOut, ProgressUpdate
from app.services import progress_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=list[ProgressOut])
def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return progress_service.list_progress(db, current_user.id)


@router.post("", response_model=ProgressOut)
def update_progress(
    payload: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return progress_service.update_progress(
        db,
        current_user.id,
        payload.scenario_id,
        payload.success_rate,
        payload.mistakes,
    )
