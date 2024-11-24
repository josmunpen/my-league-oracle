from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from . import db_models
from .db import engine
from .routers import model_manager, teams, predictions
from .dependencies import get_db

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LaLiga Oracle",
    description="LaLiga Oracle is an ML based engine to predict next fixtures results.",
    version="0.1.0",
    contact={"username": "josmunpen", "email": "josemamup@gmail.com"},
)

db: Session = Depends(get_db)

app.include_router(teams.router)
app.include_router(predictions.router)
app.include_router(model_manager.router)


@app.get("/health")
async def root():
    return {"message": "Everything looks ok 😁👌"}
