from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..utils import utils
from ..dependencies import get_db

from backend.services.config import settings

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/", tags=["data"])
async def get_teams_summary(db: Session = Depends(get_db)):
    """
    Get all teams names and ids associated for a given season.
    """
    res = utils.get_teams_names(db, settings.current_season)

    return res.to_dict(orient="records")


@router.get("/{team_id}", tags=["data"])
async def get_team_data(
    team_id: int,
    request_date: datetime = datetime.now().strftime("%Y-%m-%d"),
    db: Session = Depends(get_db),
):
    """
    Get current team info like points, number of matches played, etc.
    """
    res = utils.get_team_data(team_id, db, request_date)

    return res.to_dict(orient="records")
