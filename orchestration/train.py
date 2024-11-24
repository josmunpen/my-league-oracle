from typing import List
from prefect import flow, get_run_logger
from prefect_sqlalchemy import DatabaseCredentials
from prefect.blocks.system import Secret

import pandas as pd
import os

from mlflow.client import MlflowClient
import mlflow

import train_tasks
import dagshub

from datetime import datetime

@flow(log_prints=True)
def train_model(seasons_to_train: List[int]):
    logger = get_run_logger()

    logger.info("🚀 Starting flow")

    db = DatabaseCredentials.load("neon-postgre-credentials").get_engine()
    mlflow_tracking_username= Secret.load("mlflow-tracking-username").get()

    # print("env variables before assignment")
    # print(os.environ["MLFLOW_TRACKING_USERNAME"])
    # print(os.environ["DAGSHUB_USER_TOKEN"])
    
    os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_tracking_username
    os.environ["DAGSHUB_USER_TOKEN"] = mlflow_tracking_username
    
    print("env variables after assignment")
    print(os.environ["MLFLOW_TRACKING_USERNAME"])
    print(os.environ["DAGSHUB_USER_TOKEN"])

    dagshub.auth.add_app_token(token=mlflow_tracking_username)
    mlflow.set_tracking_uri("https://dagshub.com/josmunpen/laliga-oracle-dags.mlflow")
    dagshub.init(repo_owner="josmunpen", repo_name="laliga-oracle-dags", mlflow=True)

    date_version = datetime.now().strftime("%Y-%m-%d")
    mlflow.set_experiment(f"LaLigaOracle_{date_version}")
    mlflow_client = MlflowClient(mlflow.get_tracking_uri())

    # 1. Leer dato
    train_data = train_tasks.get_train_data(seasons_to_train, db)
    logger.info("✅ Retrieved data succesfully")

    # 2. Preprocessing and Feature Engineering
    preprocessed_data, ohe_encoder, dict_features = train_tasks.preprocess_data(train_data)
    logger.info("✅ Preprocessed data succesfully")

    # 3. Train
    best_model, best_model_run_id = train_tasks.train_models(
        preprocessed_data,
        dict_features=dict_features,
        mlflow_client=mlflow_client,
        scale=False,
    )   
    logger.info("✅ Trained models succesfully")
    
    # 4. Promote best model to PRO
    success: bool = train_tasks.promote_best_model(mlflow_client, best_model_run_id, ohe_encoder)
    logger.info("✅ Promoted model + OHE succesfully")

    return success


# if __name__ == "__main__":
#     train_model(seasons_to_train=[2022, 2023])
