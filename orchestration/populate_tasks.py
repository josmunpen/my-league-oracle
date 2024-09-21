from prefect import get_run_logger, task

import requests
import json
import pandas as pd

from sqlalchemy import text


@task
def get_teams_ids(headers: dict, season: int):
    """
    Get a list of teams ids for a season and league
    """
    logger = get_run_logger()
    query_params = {"country": "Spain", "league": 140, "season": season}
    response = requests.get(
        "https://api-football-v1.p.rapidapi.com/v3/teams",
        headers=headers,
        params=query_params,
    )
    teams = json.loads(response.text).get("response")
    teams_id = [team["team"]["id"] for team in teams]

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


@task
def persist_matches(db, season, matches):
    """
    Persist a list of matches data
    """
    logger = get_run_logger()

    matches["season"] = season
    matches["match_date"] = pd.to_datetime(matches["match_date"]).dt.strftime("%Y-%m-%d")

    with db.connect() as conn:

        # Drop last matches version
        conn.execute(text("""
                          DELETE
                          FROM matches
                          WHERE season=:season
                          """), {"season": season})
        
        conn.commit()

        # Insert new matches version
        matches.to_sql(name="matches", con=conn, if_exists="append", index=False)

    
    logger.info(f"✅ Persisted {matches.shape[0]} matches sucessfully")

    return True