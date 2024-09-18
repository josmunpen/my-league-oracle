from prefect import flow, get_run_logger, task
from prefect.blocks.system import Secret
from prefect_sqlalchemy import DatabaseCredentials

import pandas as pd
import utils
import time

import populate_tasks

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



@flow(log_prints=True)
def populate_teams_data(season=2022):
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
    wednesdays = utils.get_all_wednesdays(season=season)

    # Get all teams ids 
    teams_id = populate_tasks.get_teams_ids(headers, season=season)

    teams = {}
    for team_id in teams_id:
        team_data = {}
        for query_date in wednesdays:

            data_retrieved = teams_db[(teams_db["team_id"]==team_id) & (teams_db["query_date"]==query_date)]
            #TODO: Concat everything to a single dataframe
            # If data is not available at db, get it
            if data_retrieved.empty:
                logger.info(f"Data not found for team {team_id} and query date {query_date}")
                team_data[query_date] = utils.get_team_info(headers=headers, team_id=team_id, season=season, query_date=query_date)
                time.sleep(5) #TODO: less time ?
        teams[team_id] = team_data

    # Persist teams data
    populate_tasks.persist_teams(db, teams)

# if __name__ == "__main__":
#    populate_teams_data(season=2022)
