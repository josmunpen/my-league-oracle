import pandas as pd
import datetime
from functools import wraps
import requests
import json
from prefect import flow, get_run_logger, task
from prefect_sqlalchemy import DatabaseCredentials


def check_requests(func):

    db = DatabaseCredentials.load("neon-postgre-credentials").get_engine()

    @wraps(func)
    def wrapper_check_req(*args, **kwargs):
        today = datetime.datetime.today()

        with db.connect() as conn:
            df = pd.read_sql(f"""
                        SELECT *
                        FROM requests
                        WHERE DATE(requests.date) = DATE('{today}')
                        """, con=conn)
        
        # First call of the day
        if df.empty:
            print(f"First call of the day :)")
            updated_num_req = 0
        else:
            updated_num_req = df["num_requests"].values[0]

        print(f" = Today {updated_num_req} requests were done")

        # If number of requests exceeded limit, raise exception
        if updated_num_req < 98:
            updated_num_req = updated_num_req + 1
            new_row = pd.DataFrame(data={"date": [today],"num_requests": [updated_num_req]})

            
            with db.connect() as conn:
                new_row.to_sql(name="requests", con=conn, if_exists="replace", index=False)

        # Else (more than 98 requests today), raise exception
        else:
            print(f" !!!!! Reached requests limit by day !!!!!")
            raise Exception("Reached requests limit by day")

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

def get_all_wednesdays(year):
    """
    Get all wednesdays of a year
    """

    first_match_date = datetime.date(year,8,1)
    last_match_date =  datetime.date(year+1,6,30)

    diff_to_wednesday = (7 - 5 - first_match_date.weekday()) % 7

    if diff_to_wednesday > 0 :
        first_wednesday = first_match_date + datetime.timedelta(diff_to_wednesday)
    else:
        first_wednesday = first_match_date - datetime.timedelta(diff_to_wednesday)

    new_date = first_wednesday
    wednesdays = []
    while new_date < last_match_date:
        wednesdays.append(new_date)
        new_date = new_date + datetime.timedelta(7)
    
    return wednesdays

