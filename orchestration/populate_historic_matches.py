from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect_sqlalchemy import DatabaseCredentials

import pandas as pd
import utils
import time
import requests
import json

import populate_tasks



@flow(log_prints=True)
def populate_matches_data(season):
    logger = get_run_logger()

    logger.info("🚀 Starting flow")

    headers = {
        'x-rapidapi-host': Secret.load("rapidapi-host").get(),
        'x-rapidapi-key': Secret.load("rapidapi-key").get()
    }
    
    db = DatabaseCredentials.load("neon-postgre-credentials").get_engine()

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/rounds"
    querystring = {"league":140, "season": season}
    response = requests.get(url, headers=headers, params=querystring)
    rounds = json.loads(response.text).get('response')

    data_fixtures = []

    for round in rounds:
        round_data = utils.get_round_info(round=round, headers=headers, season=season)
        data_fixtures.extend(round_data)

    df_fixtures = pd.DataFrame(data_fixtures, columns=["fixture", "match_date", "team_home", "team_away", "result_predict", "result_real"])

    # Persist teams data
    populate_tasks.persist_matches(db, season, df_fixtures)

# if __name__ == "__main__":
#    populate_matches_data(season=2024)
