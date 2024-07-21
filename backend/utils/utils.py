import sqlite3
import pandas as pd


def get_team_data(team_id: int, db):

    # Get teams data (filter by last data available before match date)
    df = pd.read_sql(
        f"""
            SELECT team_id, query_date, name, history, total_played, wins_home, wins_away, draws_home, draws_away, loses_home, loses_away, goals_for_home, goals_for_away, goals_against_home, goals_against_away
            FROM teams
            WHERE teams.query_date = (
                SELECT MAX(teams.query_date)
                FROM teams
                WHERE teams.query_date <= DATE('now')
            ) AND teams.team_id = {team_id}
        """,
        con=db.bind, #TODO: Review .bind method, use session instead engine
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

    return df_match


def fe(df, ohe_encoder):
    # Drop columns
    df = df.drop(
        columns=["home_query_date", "away_query_date", "home_name", "away_name"], axis=1
    )

    # OHE
    ohe_cols = ["team_home", "team_away"]
    ohe_encoded = ohe_encoder.transform(df[ohe_cols])
    df = pd.concat([df, ohe_encoded], axis=1).drop(columns=ohe_cols)

    # History
    df["home_history"] = df["home_history"].apply(lambda x: list(x)[:6])
    df["away_history"] = df["away_history"].apply(lambda x: list(x)[:6])
    df[
        [
            "home_last_1",
            "home_last_2",
            "home_last_3",
            "home_last_4",
            "home_last_5",
            "home_last_6",
        ]
    ] = df["home_history"].apply(pd.Series)

    df[
        [
            "away_last_1",
            "away_last_2",
            "away_last_3",
            "away_last_4",
            "away_last_5",
            "away_last_6",
        ]
    ] = df["away_history"].apply(pd.Series)

    df.drop(["home_history", "away_history"], axis=1, inplace=True)

    label_cols = [
        "home_last_1",
        "home_last_2",
        "home_last_3",
        "home_last_4",
        "home_last_5",
        "home_last_6",
        "away_last_1",
        "away_last_2",
        "away_last_3",
        "away_last_4",
        "away_last_5",
        "away_last_6",
    ]

    df.replace({"L": 0, "D": 1, "W": 2}, inplace=True)

    # History feature
    cols_home_last = [
        "home_last_1",
        "home_last_2",
        "home_last_3",
        "home_last_4",
        "home_last_5",
        "home_last_6",
    ]
    cols_away_last = [
        "away_last_1",
        "away_last_2",
        "away_last_3",
        "away_last_4",
        "away_last_5",
        "away_last_6",
    ]

    df["home_last_avg"] = df[cols_home_last].mean(axis=1, skipna=True)
    df["away_last_avg"] = df[cols_away_last].mean(axis=1, skipna=True)

    df.drop(columns=cols_home_last, axis=1, inplace=True)
    df.drop(columns=cols_away_last, axis=1, inplace=True)

    return df
