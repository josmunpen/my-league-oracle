from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect_sqlalchemy import DatabaseCredentials

from datetime import datetime
import requests
import json
import pandas as pd
import logging
import utils
import time

import populate_tasks

@task
def get_loaded_teams(db, run_date):
    """
    Retrieve currently loaded data. 
    """
    logger = get_run_logger()

    with db.connect() as conn:
        teams_db = pd.read_sql(f"""SELECT *
                                 FROM teams
                                 WHERE query_date='{run_date.strftime("%Y-%m-%d")}'""",
                                conn)

    logger.info("✅ Teams current data retrieved correctly from API")

    return teams_db


@flow(log_prints=True)
def populate_new_data(season, run_date):
    logger = get_run_logger()

    logger.info("🚀 Starting flow")

    headers = {
        'x-rapidapi-host': Secret.load("rapidapi-host").get(),
        'x-rapidapi-key': Secret.load("rapidapi-key").get()
    }
    
    db = DatabaseCredentials.load("neon-postgre-credentials").get_engine()

    # Get current db data
    teams_db = get_loaded_teams(db, run_date=run_date)

    # Check if run date is in date range
    utils.check_run_date(season, run_date)

    # Get all teams ids 
    teams_id = populate_tasks.get_teams_ids(headers, season=season)

    teams = {}
    for team_id in teams_id:
        team_data = {}

        data_retrieved = teams_db[(teams_db["team_id"]==team_id)]
                                #    & (teams_db["query_date"]==run_date)]

        # If data is not available at db, get it
        if data_retrieved.empty:
            logger.info(f"Data not found for team {team_id} and run date {run_date}")
            team_data[run_date] = utils.get_team_info(headers=headers, team_id=team_id, season=season, query_date=run_date.strftime("%Y-%m-%d"))
            time.sleep(5) #TODO: less time ?
        teams[team_id] = team_data

    # Persist teams data
    populate_tasks.persist_teams(db, teams)

if __name__ == "__main__":
    populate_new_data(season=2024, run_date=datetime.today())
