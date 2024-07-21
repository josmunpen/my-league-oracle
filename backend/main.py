from fastapi import FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session

from utils.utils import get_match_data, fe, get_team_data
import db_models
from  db import SessionLocal, engine

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI()
loaded_model = pickle.load(open(f"./models/log_reg_v1.sav", "rb"))
ohe_encoder = pickle.load(open(f"./models/ohe_encoder.sav", "rb"))

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
    df_match = get_match_data(team_home_id, team_away_id, db)

    df_match = fe(df_match, ohe_encoder)

    result_predict = loaded_model.predict(df_match.values)

    return {"result_prediction": int(result_predict[0])}


@app.get("/team")
async def get_team(team_id:int, db: Session = Depends(get_db)):
    res = get_team_data(team_id, db)

    return res.to_dict()