from datetime import date
import reflex as rx
import httpx
import pandas as pd
import json

import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('BACKEND_URL')


class State(rx.State):

    # Teams data state

    ## Teams data
    data_teams: pd.DataFrame = pd.DataFrame()

    ## Team names
    team_names: list[str] = []

    ## Form with team id
    form_team_details: dict = {}

    ## Team details (data)
    team_details: pd.DataFrame = pd.DataFrame()
    team_details2: dict = {}

    def load_data_teams(self):
        '''
        Load teams names and ids
        '''
        print("Loading data...")
        url = f"{backend_url}/teams/"
        response = httpx.get(url)
        df = pd.DataFrame.from_records(json.loads(response.text))
        df.rename({"team_id": "Team ID", "name": "Name"}, axis=1, inplace=True)
        self.data_teams = df
        self.map_team_id = {key: val for key, val in df.to_dict("tight")["data"]}
        self.team_names = df["Name"].unique().tolist()
        self.team_ids = df["Team ID"].unique().tolist()

    def handle_submit_team_details(self, form_team_details: dict):
        '''
        Get input form, retrieve team details and format it
        '''

        # Get form data
        self.form_team_details = form_team_details

        input_id = form_team_details["input_details_team_id"]
        input_date = form_team_details["input_details_request_date"]


        # API call to retrieve team details
        url = f"{backend_url}/teams/{input_id}?request_date={input_date}"

        response = httpx.get(url)

        rename_cols = {
            "team_id": "Team ID",
            "query_date": "Query date",
            "name": "Name",
            "history": "Matches history",
            "total_played": "Total games played",
            "wins_home": "Wins (home)",
            "wins_away": "Wins (away)",
            "draws_home": "Draws (home)",
            "draws_away": "Draws (away)",
            "loses_home": "Loses (home)",
            "loses_away": "Loses (away)",
            "goals_for_home": "Goals for (home)",
            "goals_for_away": "Goals for (away)",
            "goals_against_home": "Goals against (home)",
            "goals_against_away": "Goals against (away)",
        }

        # Format data
        df = (
            pd.DataFrame.from_records(json.loads(response.text))
            .rename(columns=rename_cols)
            .T
        )
        df.rename({0: "Value"}, axis=1, inplace=True)
        df["Field"] = df.index
        df.columns = ["Field", "Value"]

        self.team_details = df

        dict_team_details = json.loads(response.text)[0]
        dict_team_details = { rename_cols[key]: val for key, val in dict_team_details.items() if key in rename_cols.keys()}

        self.team_details2 = dict_team_details
        

    # Oracle (predictions) state
    ## Form data
    form_oracle: dict = {}

    ## Prediction raw
    prediction: dict = {}

    ## Prediction formatted
    prediction_winner_format: str = None
    prediction_probs_format: list = []

    ## Teams ids
    team_home_id: str = None
    team_away_id: str = None

    def format_prediction(self, prediction) -> str:
        '''
        Returns name of winner team or Draw.
        '''
        res = None
        if prediction == 0:
            res = self.form_oracle["team_home"]
        if prediction == 1:
            res = "Draw"
        if prediction == 2:
            res = self.form_oracle["team_away"]            
        return res
    
    def handle_submit_oracle(self, form_oracle: dict):
        '''
        Sends input form, retrieve prediction and format it
        '''
        self.form_oracle = form_oracle

        team_home = form_oracle["team_home"]
        team_away = form_oracle["team_away"]

        self.team_home_id = self.data_teams[self.data_teams["Name"]==team_home]["Team ID"].tolist()[0]
        self.team_away_id = self.data_teams[self.data_teams["Name"]==team_away]["Team ID"].tolist()[0]

        url = f"{backend_url}/predictions/?team_home_id={self.team_home_id}&team_away_id={self.team_away_id}"

        response = httpx.get(url)

        res_prediction = json.loads(response.text)

        self.prediction = res_prediction

        self.prediction_winner_format = self.format_prediction(res_prediction["result_prediction"])
    
        self.prediction_probs_format = [
                {"name": "Win home", "prob": res_prediction["probs"]["home_win"]},
                {"name": "Draw", "prob": res_prediction["probs"]["draw"]},
                {"name": "Win away", "prob": res_prediction["probs"]["away_win"]}
            ]
    