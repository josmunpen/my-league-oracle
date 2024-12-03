from fastapi import APIRouter, Depends, HTTPException
from backend.models.results_model import ResultsModel

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", tags=["models"])
def refresh_model(version: str | None = None, model=ResultsModel()):
    """
    Reloads current inference model with latest or with given version
    """
    try:
        if not version:
            version = "latest"
        model.update_model()
        updated_model = model.get_model()
        model_name = updated_model["classifier_name"]
        model_train_season = updated_model["train_ts"]
        model_train_ts = updated_model["train_seasons"]
    except:
        raise HTTPException(status_code=400, detail="Unable to load model")

    return {
        "msg": f"✅ Model updated correctly to {model_name} (trained on {model_train_season} with seasons {model_train_ts})"
    }
