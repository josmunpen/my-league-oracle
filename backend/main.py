from fastapi import FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session

from .utils import utils
from . import db_models
from .db import SessionLocal, engine

import sklearn
import os

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI()
print(os.listdir())

loaded_model = pickle.load(open(f"backend/models/log_reg_v1.sav", "rb"))
ohe_encoder = pickle.load(open(f"backend/models/ohe_encoder.sav", "rb"))

# # Local
# loaded_model = pickle.load(open(f"../backend/models/log_reg_v1.sav", "rb"))
# ohe_encoder = pickle.load(open(f"../backend/models/ohe_encoder.sav", "rb"))


# Create a session per request, then close
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hola mundo! :)"}


@app.get("/predict")
def predict_match(team_home_id: int, team_away_id: int, db: Session = Depends(get_db)):
    df_match = utils.get_match_data(team_home_id, team_away_id, db)

    df_match = utils.fe(df_match, ohe_encoder)

    result_predict = loaded_model.predict(df_match.values)[0]
    probs = loaded_model.predict_proba(df_match.values)[0]

    return {
        "result_prediction": int(result_predict),
        "probs": {"home_win": probs[0], "draw": probs[1], "away_win": probs[2]},
    }


@app.get("/team")
async def get_team(team_id: int, db: Session = Depends(get_db)):
    res = utils.get_team_data(team_id, db)

    return res.to_dict(orient="records")


@app.get("/teams_name")
async def get_teams_names(db: Session = Depends(get_db)):
    res = utils.get_teams_names(db)

    return res.to_dict(orient="records")