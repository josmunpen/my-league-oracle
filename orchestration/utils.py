import pandas as pd
import datetime
from functools import wraps
import requests
import json
from prefect_sqlalchemy import DatabaseCredentials
import re
import time
from sqlalchemy.types import String, Integer, Date
from sqlalchemy import text

class NumRequestException(Exception):
    def __init__(self, message="Max number of requests done."):
        self.message = message
        super().__init__(self.message)

def check_requests(func):

    db = DatabaseCredentials.load("neon-postgre-credentials").get_engine()

    @wraps(func)
    def wrapper_check_req(*args, **kwargs):
        today = datetime.datetime.today()

        with db.connect() as conn:
            df = pd.read_sql(
                f"""
                        SELECT *
                        FROM requests
                        WHERE DATE(requests.date) = DATE('{today}')
                        """,
                con=conn,
            )


        # First call of the day
        if df.empty:
            print(f"First call of the day 🤓")
            updated_num_req = 0

            insert_query = text(
                """
                INSERT INTO requests (date, num_requests)
                VALUES (:date, :num_requests)
                """
            )

            with db.connect() as conn:
                conn.execute(
                    insert_query,
                    {
                        "date": today,
                        "num_requests": updated_num_req,
                    },
                )
                conn.commit()

        elif df["num_requests"].values[0] < 98:
            updated_num_req = df["num_requests"].values[0] + 1
            id = df["id"].values[0]

            update_query = text(
                """
                UPDATE requests
                SET num_requests = :updated_num_req
                WHERE id = :id
                """
            )

            query_params =                  {
                        "id": int(id),
                        "date": today,
                        "updated_num_req": int(updated_num_req),
                    },
            
            with db.connect() as conn:
                conn.execute(
                    update_query, query_params,
                )
                conn.commit()


        # Else (more than 98 requests today), raise exception
        else:
            raise NumRequestException("!!!!! Reached requests limit by day !!!!!")


        print(f" = Today {updated_num_req} requests were done")
        


        return func(*args, **kwargs)

    return wrapper_check_req


@check_requests
def get_team_info(headers, team_id, season, query_date):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"

    querystring = {"league": 140, "season": season, "team": team_id, "date": query_date}

    response = requests.get(url, headers=headers, params=querystring)

    response_content = json.loads(response.text)["response"]

    team_id = response_content["team"]["id"]
    name = response_content["team"]["name"]

    history = response_content["form"]

    total_played = response_content["fixtures"]["played"]["total"]

    wins_home = response_content["fixtures"]["wins"]["home"]
    wins_away = response_content["fixtures"]["wins"]["away"]

    draws_home = response_content["fixtures"]["draws"]["home"]
    draws_away = response_content["fixtures"]["draws"]["away"]

    loses_home = response_content["fixtures"]["loses"]["home"]
    loses_away = response_content["fixtures"]["loses"]["away"]

    goals_for_home = response_content["goals"]["for"]["total"]["home"]
    goals_for_away = response_content["goals"]["for"]["total"]["away"]

    goals_against_home = response_content["goals"]["against"]["total"]["home"]
    goals_against_away = response_content["goals"]["against"]["total"]["away"]

    return (
        team_id,
        query_date,
        name,
        history,
        total_played,
        wins_home,
        wins_away,
        draws_home,
        draws_away,
        loses_home,
        loses_away,
        goals_for_home,
        goals_for_away,
        goals_against_home,
        goals_against_away,
    )


def get_all_wednesdays(season: int):
    """
    Get all wednesdays of a season
    """

    first_match_date = datetime.date(season, 8, 1)
    last_match_date = datetime.date(season + 1, 6, 30)

    diff_to_wednesday = (7 - 5 - first_match_date.weekday()) % 7

    if diff_to_wednesday > 0:
        first_wednesday = first_match_date + datetime.timedelta(diff_to_wednesday)
    else:
        first_wednesday = first_match_date - datetime.timedelta(diff_to_wednesday)

    new_date = first_wednesday
    wednesdays = []
    while new_date < last_match_date:
        wednesdays.append(new_date)
        new_date = new_date + datetime.timedelta(7)

    return wednesdays


def check_run_date(season: int, run_date: datetime):
    """
    Check if a run date is in date range.
    """

    first_match_date = datetime.date(season, 8, 1)
    last_match_date = datetime.date(season + 1, 6, 30)

    if first_match_date < run_date.date() < last_match_date:
        return True
    else:
        raise Exception("Run date is out of range.")


@check_requests
def get_round_info(round, headers, season, league=140):
    querystring = {"league": league, "season": season, "round": round}
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    response = requests.get(url, headers=headers, params=querystring)
    fixtures_round = json.loads(response.text).get("response")

    round_format = re.search("Regular Season - (\d+)", round).group(1)

    print(f" = Loading round {round_format}")

    data_fixtures_round = []
    # For each home, get both teams id
    for fixture in fixtures_round:
        match_datetime = fixture["fixture"]["date"]

        home_id = fixture["teams"]["home"]["id"]
        away_id = fixture["teams"]["away"]["id"]

        home_win = fixture["teams"]["home"]["winner"]
        away_win = fixture["teams"]["away"]["winner"]

        finished = True if fixture["score"]["fulltime"]["home"] != None else False

        result = ""
        if finished == False:
            result = None
        elif home_win == True:
            result = "home_win"
        elif away_win == True:
            result = "away_win"
        else:
            result = "draw"
        data_fixtures_round.append(
            [round_format, match_datetime, home_id, away_id, None, result]
        )

    time.sleep(3)
    return data_fixtures_round
