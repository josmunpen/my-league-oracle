from typing import List
from prefect import flow, get_run_logger
from prefect_sqlalchemy import DatabaseCredentials
from prefect.blocks.system import Secret

import pandas as pd
import os

from mlflow.client import MlflowClient
import mlflow

from orchestration.populate_new_teams import populate_new_teams_data
from orchestration.train import train_model
from orchestration.populate_matches import populate_matches_data
import train_tasks
import dagshub

from datetime import datetime

@flow(log_prints=True)
def weekly_populate_train_flow(season, run_date, seasons_to_train: List[int]):
    logger = get_run_logger()

    logger.info("🚀 Starting flow")

    # Execute nested flow 1: populate matches
    populate_matches_data(season=season)
    logger.info("1️⃣ Finished matches populate")

    # Execute nested flow 2: populate teams data
    populate_new_teams_data(season=season, run_date=run_date)
    logger.info("2️⃣ Finished teams populate")
    
    # Execute nested flow 3: train models
    train_model(seasons_to_train)
    logger.info("3️⃣ Finished models train")

    return True