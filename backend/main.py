from fastapi import FastAPI
import pickle
import pandas as pd

from utils.utils import get_match_data, fe

app = FastAPI()
loaded_model = pickle.load(open(f"./models/log_reg_v1.sav", "rb"))
ohe_encoder = pickle.load(open(f"./models/ohe_encoder.sav", "rb"))


@app.get("/")
async def root():
    return {"message": "Hola mundo! :)"}


@app.get("/predict")
def predict_match(team_home_id: int, team_away_id: int):

    df_match = get_match_data(team_home_id, team_away_id)

    df_match = fe(df_match, ohe_encoder)

    result_predict = loaded_model.predict(df_match.values)

    return {"result_prediction": int(result_predict[0])}
