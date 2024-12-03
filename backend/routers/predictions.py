from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.results_model import ResultsModel
from backend.utils import utils
from backend.dependencies import get_db

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/", tags=["predictions"])
def predict_match(
    team_home_id: int,
    team_away_id: int,
    db: Session = Depends(get_db),
    model = ResultsModel(),
):
    """
    Predict a fixture result.
    """
    df_match = utils.get_match_data(team_home_id, team_away_id, db)
    df_match = utils.fe(df_match, model.get_ohe())

    classifier_name = model["tags"].get("classifier_name")
    train_seasons = model["tags"].get("train_seasons")
    train_seasons = model["tags"].get("train_seasons")

    classifier = model.get("classifier")
    result_predict = classifier.predict(df_match.values)[0]
    probs = classifier.predict_proba(df_match.values)[0]

    return {
        "result_prediction": int(result_predict),
        "probs": {"home_win": probs[0], "draw": probs[1], "away_win": probs[2]},
        "model": {
            "name": classifier_name,
            "train_seasons": train_seasons
        }
    }
