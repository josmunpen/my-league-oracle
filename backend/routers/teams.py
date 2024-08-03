from fastapi import APIRouter, FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

from ..utils import utils
from .. import db_models
from ..dependencies import get_db

import sklearn
import os


router = APIRouter(
    prefix="/teams",
    tags=["teams"]
)

@router.get("/", tags=["data"])
async def get_teams_summary(db: Session = Depends(get_db)):
    """
    Get all teams names and ids associated
    """
    res = utils.get_teams_names(db)

    return res.to_dict(orient="records")

@router.get("/{team_id}", tags=["data"])
async def get_team_data(team_id: int, request_date: datetime | None = None, db: Session = Depends(get_db)):
    """
    Get current team info like points, number of matches played, etc.
    """
    res = utils.get_team_data(team_id, db, request_date)

    return res.to_dict(orient="records")



