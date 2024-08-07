from fastapi import APIRouter, FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session

from ..utils import utils
from .. import db_models
from ..dependencies import get_db
from ..models import classifier


import sklearn
import os


router = APIRouter(
    prefix="/predictions",
    tags=["predictions"]
)


@router.get("/", tags=["predictions"])
def predict_match(team_home_id: int, team_away_id: int, db: Session = Depends(get_db)):
    """
    Predict a fixture result.
    """
    
    df_match = utils.get_match_data(team_home_id, team_away_id, db)

    df_match = utils.fe(df_match, classifier.ohe)

    result_predict = classifier.model.predict(df_match.values)[0]
    probs = classifier.model.predict_proba(df_match.values)[0]

    return {
        "result_prediction": int(result_predict),
        "probs": {"home_win": probs[0], "draw": probs[1], "away_win": probs[2]},
    }


