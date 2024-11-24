import threading
import mlflow.sklearn

class ResultsModel:
    """
    Singleton pattern applied to have a single instance of results prediction model.
    """
    _instance = None         # Retrieves the only instance
    _lock = threading.Lock() # Used to avoid multithread access

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ResultsModel, cls).__new__(cls)
                    cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        
        mlflow.set_tracking_uri("https://dagshub.com/josmunpen/laliga-oracle-dags.mlflow")
        # dagshub.init(repo_owner="josmunpen", repo_name="laliga-oracle-dags", mlflow=True)
        self.classifier = mlflow.sklearn.load_model("models:/oracle-model-production/latest")
        self.ohe = mlflow.sklearn.load_model("models:/oracle-ohe-production/latest")
        print("🚀 Model loaded successfully!")

    def get_model(self):
        return self.classifier
    
    def get_ohe(self):
        return self.ohe
    
    def update_model(self):
        with self._lock:  
            self.classifier = mlflow.sklearn.load_model("models:/oracle-model-production/latest")
            self.ohe = mlflow.sklearn.load_model("models:/ohe_encoder/latest")
            print("🚀 Model updated successfully!")
        return True