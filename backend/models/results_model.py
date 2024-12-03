import threading
import mlflow.sklearn
from mlflow.client import MlflowClient


class ResultsModel:
    """
    Singleton pattern applied to have a single instance of results prediction model.
    """

    _instance = None  # Retrieves the only instance
    _lock = threading.Lock()  # Used to avoid multithread access

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ResultsModel, cls).__new__(cls)
                    cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):

        mlflow.set_tracking_uri(
            "https://dagshub.com/josmunpen/laliga-oracle-dags.mlflow"
        )
        # dagshub.init(repo_owner="josmunpen", repo_name="laliga-oracle-dags", mlflow=True)

        production_model_name = "oracle-model-production"
        self.classifier = mlflow.sklearn.load_model(
            f"models:/{production_model_name}/latest"
        )

        mlflow_client = MlflowClient(mlflow.get_tracking_uri())

        latest_version_info = mlflow_client.get_latest_versions(
            name=production_model_name
        )[0]

        self.classifier_name = latest_version_info.tags.get("model_name")
        self.train_seasons = latest_version_info.tags.get("train_seasons")
        self.train_ts = latest_version_info.tags.get("date_version")

        self.ohe = mlflow.sklearn.load_model("models:/oracle-ohe-production/latest")
        print("🚀 Model loaded successfully!")

    def get_model(self):
        return {
            "classifier": self.classifier,
            "classifier_name": self.classifier_name,
            "train_seasons": self.train_seasons,
            "train_ts": self.train_ts,
        }

    def get_ohe(self):
        return self.ohe

    def update_model(self):
        with self._lock:
            self.classifier = mlflow.sklearn.load_model(
                "models:/oracle-model-production/latest"
            )
            self.ohe = mlflow.sklearn.load_model("models:/ohe_encoder/latest")
            print("🚀 Model updated successfully!")
        return True
