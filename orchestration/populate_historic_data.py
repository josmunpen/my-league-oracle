from prefect import flow, get_run_logger, task
import datetime
from prefect.blocks.system import Secret
import requests
import json
from prefect_sqlalchemy import SqlAlchemyConnector, DatabaseCredentials
from sqlalchemy import URL, create_engine
import pandas as pd
import logging
import utils
import time

@task
def get_loaded_teams(db):
    """
    Retrieve currently loaded data. 
    """
    logger = get_run_logger()

    with db.connect() as conn:
        teams_db = pd.read_sql('select * from teams', conn)

    logger.info("✅ Teams current data retrieved correctly from API")

    return teams_db

@task
def get_teams_ids(headers: dict, year: int):
    """
    Get a list of teams ids for a season and league
    """
    logger = get_run_logger()
    query_params = {"country": "Spain", "league": 140, "season": year}
    response = requests.get("https://api-football-v1.p.rapidapi.com/v3/teams", headers=headers, params=query_params)
    teams = json.loads(response.text).get('response')
    teams_id = [team['team']['id'] for team in teams]

    logger.info("✅ Teams ids retrieved correctly from DB")

    return teams_id

@task
def persist_teams(db, teams):
    """
    Persist a list of teams data (at a datetime query each)
    """
    logger = get_run_logger()
    for team, team_data in teams.items():
        df_teams = pd.DataFrame.from_dict(
            team_data,
            orient="index",
            columns=[
                "team_id",
                "query_date",
                "name",
                "history",
                "total_played",
                "wins_home",
                "wins_away",
                "draws_home",
                "draws_away",
                "loses_home",
                "loses_away",
                "goals_for_home",
                "goals_for_away",
                "goals_against_home",
                "goals_against_away",
            ],
        )

        with db.connect() as conn:
            df_teams.to_sql(name="teams", con=conn, if_exists="append", index=False)

    
    logger.info(f"✅ Persisted {df_teams.shape[0]} teams sucessfully")

    return True

@flow(log_prints=True)
def populate_teams_data():
    logger = get_run_logger()

    logger.info("🚀 Starting flow")

    headers = {
        'x-rapidapi-host': Secret.load("rapidapi-host").get(),
        'x-rapidapi-key': Secret.load("rapidapi-key").get()
    }
    
    db = DatabaseCredentials.load("neon-postgre-credentials").get_engine()

    # Get current db data
    teams_db = get_loaded_teams(db)

    # Get all wednesdays (query dates)
    wednesdays = utils.get_all_wednesdays(year=2023)

    # Get all teams ids 
    teams_id = get_teams_ids(headers, year=2023)

    teams = {}
    for team_id in teams_id[:1]:
        team_data = {}
        for query_date in wednesdays[:1]:

            data_retrieved = teams_db[(teams_db["team_id"]==team_id) & (teams_db["query_date"]==query_date)]

            # If data is not available at db, get it
            if data_retrieved.empty:
                logger.info(f"Data not found for team {team_id} and query date {query_date}")
                team_data[query_date] = utils.get_team_info(headers=headers, team_id=team_id, season=2023, query_date=query_date)
                time.sleep(5) #TODO: less time ?
        teams[team_id] = team_data

    # Persist teams data
    persist_teams(db, teams)

# if __name__ == "__main__":
#     populate_teams_data()
