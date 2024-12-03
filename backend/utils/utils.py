from fastapi import HTTPException
import pandas as pd
from datetime import datetime

from backend.services.config import settings


def get_team_data(
    team_id: int,
    db,
    request_date: datetime = datetime.now(),
    current_season: int = settings.current_season,
):
    # Get teams data (filter by last data available before match date)
    df = pd.read_sql(
        f"""
            SELECT team_id, query_date, name, history, total_played, wins_home, wins_away, draws_home,
                    draws_away, loses_home, loses_away, goals_for_home, goals_for_away, goals_against_home,
                    goals_against_away, season
            FROM teams
            WHERE teams.query_date = (
                SELECT MAX(teams.query_date)
                FROM teams
                WHERE teams.query_date <= DATE('{request_date}')
                  AND teams.team_id = {team_id}
                  AND teams.season <= {current_season}
            ) AND teams.team_id = {team_id}
            AND teams.history IS NOT NULL
        """,
        con=db.bind,  # TODO: Review .bind method, use session instead engine
    )
    return df


def get_match_data(team_home_id: int, team_away_id: int, db):

    df_match = pd.DataFrame.from_dict(
        {"row_1": [team_home_id, team_away_id]},
        orient="index",
        columns=["team_home", "team_away"],
    )

    df_team_home = get_team_data(team_home_id, db)
    df_team_away = get_team_data(team_away_id, db)

    df_match = df_match.merge(
        df_team_home,
        left_on="team_home",
        right_on="team_id",
        how="left",
        suffixes=(None, "_index_home"),
    )
    df_match.drop(columns=["team_id"], axis=1, inplace=True)
    df_match.columns = [
        "home_" + col if ((col in df_team_home.columns) and (col != "id")) else col
        for col in df_match.columns
    ]

    df_match = df_match.merge(
        df_team_away,
        left_on="team_away",
        right_on="team_id",
        how="left",
        suffixes=(None, "_index_away"),
    )

    df_match.drop(columns=["team_id"], axis=1, inplace=True)

    df_match.columns = [
        "away_" + col if ((col in df_team_away.columns) and (col != "id")) else col
        for col in df_match.columns
    ]
    if df_match["home_season"].values[0] != df_match["away_season"].values[0]:
        raise HTTPException(
            500,
            "An error occurred while processing data. Data retrieved for both teams are not in the same season",
        )
    else:
        df_match.rename({"home_season": "season"}, axis=1, inplace=True)

    df_match.drop(columns=["away_season"], axis=1, inplace=True)
    return df_match


def fe(df, ohe_encoder):

    # TODO: Review
    if df.shape[0] > 0:
        df = df.head(1)
    # Drop columns
    df = df.drop(
        columns=["home_query_date", "away_query_date", "home_name", "away_name"], axis=1
    )

    # If any value is null, raise exception
    if df.isnull().any().any():
        raise HTTPException(status_code=500, detail="Wrong data retrieved")
    df.to_csv("before_ohe.csv")

    # OHE
    ohe_cols = ["team_home", "team_away", "season"]
    try:
        ohe_encoded = ohe_encoder.transform(df[ohe_cols])
    except ValueError:
        print("OHE issue")
        raise HTTPException(
            204,
            "Data not found. Please note that newly promoted teams could address some issues.",
        )
    df = pd.concat([df, ohe_encoded], axis=1).drop(columns=ohe_cols)

    # History feature
    # Get last 6 matches
    df["home_history"] = df["home_history"].apply(lambda x: list(x)[:6])
    df["away_history"] = df["away_history"].apply(lambda x: list(x)[:6])

    # If data retrieved is smaller than 6, get as matches as possible
    len_home_history = len(df["home_history"].iloc[0])
    len_away_history = len(df["away_history"].iloc[0])

    cols_home_last = [
        "home_last_1",
        "home_last_2",
        "home_last_3",
        "home_last_4",
        "home_last_5",
        "home_last_6",
    ][:len_home_history]

    cols_away_last = [
        "away_last_1",
        "away_last_2",
        "away_last_3",
        "away_last_4",
        "away_last_5",
        "away_last_6",
    ][:len_away_history]

    # Create one column per match
    df[cols_home_last] = df["home_history"].apply(pd.Series)
    df[cols_away_last] = df["away_history"].apply(pd.Series)

    df.drop(["home_history", "away_history"], axis=1, inplace=True)

    # Replace values
    df.replace({"L": 0, "D": 1, "W": 2}, inplace=True)

    # Get mean
    df["home_last_avg"] = df[cols_home_last].mean(axis=1, skipna=True)
    df["away_last_avg"] = df[cols_away_last].mean(axis=1, skipna=True)

    # Drop extra columns
    df.drop(columns=cols_home_last, axis=1, inplace=True)
    df.drop(columns=cols_away_last, axis=1, inplace=True)

    return df


def get_teams_names(db, season):
    df = pd.read_sql(
        f"""
            SELECT team_id, name
            FROM teams
            WHERE season = {season}
            GROUP BY team_id, name
        """,
        con=db.bind,
    )
    return df
