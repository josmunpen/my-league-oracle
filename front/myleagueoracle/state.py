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
    team_ids: list[int] = []

    ## Form with team id
    form_team_details: dict = {}

    ## Team details (data)
    team_details: pd.DataFrame = pd.DataFrame()
    team_details2: list = []
    map_team_id: dict = {}

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

        input_name = form_team_details["input_details_team_name"]
        input_date = form_team_details["input_details_request_date"]

        input_id = self.data_teams[self.data_teams["Name"]==input_name]["Team ID"].tolist()[0]

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

        df.columns = [["Value", "Field"]]

        self.team_details = df[["Field", "Value"]]
        self.team_details2 = [list(x) for x in df[["Field", "Value"]].to_numpy()]
        

    # Oracle (predictions) state
    ## Form data
    form_oracle: dict = {}

    ## Prediction raw
    prediction: dict = {}

    ## Prediction formatted
    prediction_winner_format: str = None
    prediction_probs_format: list = []
    ## Prediction model info
    prediction_model_name: str = None
    prediction_model_train_seasons: str = None
    prediction_model_train_ts: str = None
    prediction_model_info: str = None

    ## Teams ids
    team_home_id: int = None
    team_away_id: int = None

    ## Show when prediction is done
    show_prediction: bool = False

    screen_msg: str = ""

    def format_prediction(self, prediction) -> str:
        '''
        Returns name of winner team or Draw.
        '''
        res = None
        if prediction == 0:
            res = self.form_oracle["team_home"]
            res = "🏆 " + res + " winner 🏆" 
        if prediction == 1:
            res = "Draw"
            res = "✖️ " + res + " ✖️"
        if prediction == 2:
            res = self.form_oracle["team_away"]
            res = "🏆 " + res + " winner 🏆" 
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
        
        if response.status_code != 200:
            self.screen_msg = res_prediction["detail"]
            self.show_prediction = False
            return
        
        self.prediction = res_prediction

        self.prediction_winner_format = self.format_prediction(res_prediction["result_prediction"])
        self.prediction_probs_format = [
                {"name": "Win home", "prob": res_prediction["probs"]["home_win"]},
                {"name": "Draw", "prob": res_prediction["probs"]["draw"]},
                {"name": "Win away", "prob": res_prediction["probs"]["away_win"]}
            ]
        

        self.prediction_model_name = res_prediction["model"].get("name")
        self.prediction_model_train_seasons = res_prediction["model"].get("train_seasons")
        self.prediction_model_train_ts = res_prediction["model"].get("train_ts")

        self.prediction_model_info = f"(Model employed was {self.prediction_model_name}, trained on {self.prediction_model_train_ts} with data from seasons {self.prediction_model_train_seasons})"

        self.show_prediction = True
        self.screen_msg = ""
