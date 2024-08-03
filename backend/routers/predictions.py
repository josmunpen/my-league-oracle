from fastapi import APIRouter, FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session

from ..utils import utils
from .. import db_models
from ..dependencies import get_db

import sklearn
import os


router = APIRouter(
    prefix="/predictions",
    tags=["predictions"]
)


# loaded_model = pickle.load(open(f"backend/models/log_reg_v1.sav", "rb"))
# ohe_encoder = pickle.load(open(f"backend/models/ohe_encoder.sav", "rb"))

# Local
loaded_model = pickle.load(open(f"../backend/models/log_reg_v1.sav", "rb"))
ohe_encoder = pickle.load(open(f"../backend/models/ohe_encoder.sav", "rb"))



@router.get("/", tags=["predictions"])
def predict_match(team_home_id: int, team_away_id: int, db: Session = Depends(get_db)):
    """
    Predict a fixture result.
    """
    
    df_match = utils.get_match_data(team_home_id, team_away_id, db)

    df_match = utils.fe(df_match, ohe_encoder)

    result_predict = loaded_model.predict(df_match.values)[0]
    probs = loaded_model.predict_proba(df_match.values)[0]

    return {
        "result_prediction": int(result_predict),
        "probs": {"home_win": probs[0], "draw": probs[1], "away_win": probs[2]},
    }


