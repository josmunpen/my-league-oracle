from fastapi import FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session

from . import db_models
from .db import engine
from .routers import teams, predictions


db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "LaLiga Oracle",
    description = "LaLiga Oracle is an ML based engine to predict next fixtures results.",
    version = "0.1.0",
    contact = {
        "username" : "josmunpen",
        "email": "josemamup@gmail.com"
    }

)

app.include_router(teams.router)
app.include_router(predictions.router)

@app.get("/")
async def root():
    return {"message": "Hola mundo! :)"}



