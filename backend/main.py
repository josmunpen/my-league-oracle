from fastapi import FastAPI, Depends
import pickle
import pandas as pd
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from . import db_models
from .db import engine
from .routers import teams, predictions
from .models import classifier
import mlflow.sklearn
import dagshub

db_models.Base.metadata.create_all(bind=engine)

mlflow.set_tracking_uri("https://dagshub.com/josmunpen/laliga-oracle-dags.mlflow")
dagshub.init(repo_owner='josmunpen', repo_name='laliga-oracle-dags', mlflow=True)

@asynccontextmanager
async def lifespan(app: FastAPI):

    classifier.model = mlflow.sklearn.load_model("models:/log_reg_def/1")
    classifier.ohe = mlflow.sklearn.load_model("models:/ohe/1")
    yield

    classifier.clear()

app = FastAPI(
    lifespan=lifespan,
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

@app.get("/health")
async def root():
    return {"message": "Everything looks ok 😁👌"}
