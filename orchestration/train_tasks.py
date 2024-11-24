from prefect import get_run_logger, task
import pandas as pd

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn import metrics
from sklearn.model_selection import (
    train_test_split,
    cross_val_predict,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import mlflow

import time
import secrets
from datetime import datetime

def track_run(classifier, classifier_name, X, mlflow_client, log_model=True,  **kwargs):
    model_metrics = kwargs.get("model_metrics")
    model_metrics.pop("confusion_matrix")
    params = kwargs.get("params")
    tags = kwargs.get("tags")
    model_data = kwargs.get("model_data")
    figures = kwargs.get("figures")

    # Start an MLflow run
    with mlflow.start_run():
        mlflow.set_tag("mlflow.runName", f"{classifier_name}_{secrets.token_hex(16)}")

        # Log metrics
        if model_metrics:
            mlflow.log_metrics(model_metrics)

        # Log params
        if params:
            mlflow.log_params(params)
        # size, scale, history

        if figures:
            for name, fig in figures.items():
                mlflow.log_figure(fig, "confusion_matrix.png")

        # Infer the model signature
        # signature = infer_signature(X, classifier.predict(X))

        # Log the model
        if log_model:
            model_info = mlflow.sklearn.log_model(
                sk_model=classifier,
                artifact_path=classifier_name,
                # signature=signature,
                input_example=X,
                registered_model_name=classifier_name,
            )
            model_info = mlflow_client.get_latest_versions(classifier_name)[0]
            for key, value in tags.items():
                mlflow_client.set_model_version_tag(
                    name=classifier_name,
                    version=model_info.version,
                    key=key,
                    value=value
                )

        return mlflow.active_run().info.run_id

def get_year_fixtures(season, db):
    available_fixtures = pd.read_sql(
        f"""
                            SELECT DISTINCT(fixture)
                            FROM matches
                            WHERE season={season}
                            """,
        con=db,
    )

    res = [value[0] for value in available_fixtures.values]
    return res


def evaluate_classifier(classifier, X, y):
    start = time.time()
    y_pred = cross_val_predict(classifier, X, y, cv=10)
    y_pred_proba = cross_val_predict(classifier, X, y, cv=10, method="predict_proba")
    acc = metrics.accuracy_score(y, y_pred)
    precision = metrics.precision_score(y, y_pred, average="macro")
    recall = metrics.recall_score(y, y_pred, average="macro")
    f1 = metrics.f1_score(y, y_pred, average="macro")
    # roc = metrics.roc_auc_score(y, y_pred_proba[:,1], average="macro", multi_class="ovo")
    cm = metrics.confusion_matrix(y, y_pred)

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2024)
    trained_model = classifier.fit(X_train, y_train)
    
    end = time.time()

    model_metrics = {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm,
        "elapsed_time": end - start,
    }

    return trained_model, model_metrics

@task
def get_train_data(seasons_to_train, db):
    """
    Get historic data from PostgreSQL.
    """
    logger = get_run_logger()

    dfs = []
    for season in seasons_to_train:
        available_fixtures = get_year_fixtures(season, db)
        for fixture in available_fixtures:  # Get fixture matches data
            df_matches = pd.read_sql(
                f"""
                                        SELECT *
                                        FROM matches
                                        WHERE fixture={fixture} 
                                            AND season={season}
                                        """,
                con=db,
            )

            # Get teams data (filter by last data available before match date)
            df_teams = pd.read_sql(
                f"""
                                        SELECT *
                                        FROM teams
                                        WHERE teams.query_date = (
                                            SELECT MAX(teams.query_date)
                                            FROM teams
                                            WHERE teams.query_date <= (
                                                SELECT MAX(matches.match_date)
                                                FROM matches
                                                WHERE fixture = {fixture}
                                            )
                                            AND teams.season = {season}
                                        )
                                    """,
                con=db,
            )

            df_aux = df_matches.merge(
                df_teams,
                left_on="team_home",
                right_on="team_id",
                how="left",
                suffixes=(None, "_index_home"),
            )
            df_aux.drop(columns=["team_id", "id_index_home"], axis=1, inplace=True)
            df_aux.columns = [
                "home_" + col if ((col in df_teams.columns) and (col != "id")) else col
                for col in df_aux.columns
            ]

            df_aux = df_aux.merge(
                df_teams,
                left_on="team_away",
                right_on="team_id",
                how="left",
                suffixes=(None, "_index_away"),
            )
            df_aux.drop(columns=["team_id", "id_index_away"], axis=1, inplace=True)
            df_aux.columns = [
                "away_" + col if ((col in df_teams.columns) and (col != "id")) else col
                for col in df_aux.columns
            ]

            dfs.append(df_aux)

        df = pd.concat(dfs)

        df = df[
            df["home_name"].notnull()
            & df["away_name"].notnull()
            & df["home_history"].notnull()
            & df["away_history"].notnull()
        ]

        df["match_date"] = pd.to_datetime(df["match_date"])

        # with db.connect() as conn:

        logger.info("✅ Teams ids retrieved correctly from DB")

        return df


@task
def preprocess_data(df):
    # Drop unnecesary features for model
    df.drop(
        columns=[
            "id",
            "fixture",
            "result_predict",
            "home_query_date",
            "away_query_date",
            "home_name",
            "away_name",
            "match_date",
            "away_season",
            "season_index_home",
        ],
        axis=1,
        inplace=True,
    )

    df.rename({"home_season": "season"}, axis=1, inplace=True)

    # One hot encoding
    ohe_cols = ["team_home", "team_away", "season"]
    ohe_encoder = OneHotEncoder(sparse_output=False).set_output(transform="pandas")

    ohe_encoder = ohe_encoder.fit(df[ohe_cols])

    ohe_encoded = ohe_encoder.transform(df[ohe_cols])

    df = pd.concat([df, ohe_encoded], axis=1).drop(columns=ohe_cols)

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

    #TODO: Label Encoder?
    # from sklearn.preprocessing import LabelEncoder

    # le = LabelEncoder()
    # le.fit(df["result_real"])
    # df["result_real"] = le.transform(df["result_real"])

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

    dict_features = {}

    dict_features["history_feature"] = "Avg last 6 matches"

    return df, ohe_encoder, dict_features


@task
def train_models(df, dict_features, mlflow_client, scale=False):
    # Split by target variable
    target_variable = "result_real"

    X, y = df.loc[:, df.columns != target_variable], df[target_variable]

    # Scale
    if scale == True:
        scaler = StandardScaler()
        X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

    num_samples = len(X)

    classifiers = {
        "logistic_regression": LogisticRegression(
            max_iter=10000,
        ),
        "knn_1": KNeighborsClassifier(1),

        "knn_3": KNeighborsClassifier(3),

        "knn_5": KNeighborsClassifier(5),

        "knn_15": KNeighborsClassifier(15),

        "knn_25": KNeighborsClassifier(25),

        "knn_50": KNeighborsClassifier(50),
        "knn_50": KNeighborsClassifier(100),

        "decision_tree": DecisionTreeClassifier(),

        "rfc_10": RandomForestClassifier(n_estimators=10),

        "rfc_100": RandomForestClassifier(n_estimators=100),

        "rfc_1000": RandomForestClassifier(n_estimators=1000),

        "gbr": GradientBoostingClassifier(),

        # (xgb.XGBClassifier(), "xgb"),

        # TODO: EXTREME GRADIENT BOOSTING
        }

    runs = pd.DataFrame(columns=["run_id", "accuracy", "precision", "recall", "f1", "confusion_matrix", "elapsed_time"])

    for name, classifier in classifiers.items():
        print(f"Training {name}")
        trained_model, model_metrics = evaluate_classifier(classifier, X, y)

        # cm = metrics.ConfusionMatrixDisplay(
        #     confusion_matrix=model_metrics["confusion_matrix"]
        # ).plot()
        run_id = track_run(
            trained_model,
            name,
            X=X,
            log_model=True,
            model_metrics=model_metrics,
            mlflow_client=mlflow_client,
            params={
                "dataset_size": num_samples,
                "scaled": scale,
                "history_feature": dict_features.get("history_feature"),
            },
            tags = {
                "date_version": datetime.now().strftime("%Y-%m-%d")
            }
            # figures={"confusion_matrix": cm.figure_},
        )
        row_dict = model_metrics.copy()
        row_dict["run_id"] = run_id
        runs.loc[name] = row_dict
        
        print(runs)

        best_model_name = runs["f1"].idxmax()
        best_model_run_id = runs.loc[runs["f1"].idxmax(), "run_id"]
    return best_model_name, best_model_run_id
    


@task
def promote_best_model(mlflow_client, best_model_run_id, ohe_encoder):

        best_model = mlflow_client.search_model_versions(f"run_id='{best_model_run_id}'")[0]

        mlflow_client.set_model_version_tag(
            name=best_model.name,
            version=best_model.version,
            key="weekly_best",
            value=True
        )

        mlflow_client.copy_model_version(
            src_model_uri=f"models:/{best_model.name}/{best_model.version}",
            dst_name="oracle-model-production",
        )

        mlflow.sklearn.log_model(
            sk_model=ohe_encoder,
            artifact_path="ohe_encoder",
            registered_model_name="ohe_encoder",
        )

        ohe_info = mlflow_client.get_latest_versions("ohe_encoder")[0]

        mlflow_client.copy_model_version(
            src_model_uri=f"models:/ohe_encoder/{ohe_info.version}",
            dst_name="oracle-ohe-production",
        )
        
        return True