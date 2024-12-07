# laliga-oracle

<p align="center" width="100%">
    <img width="30%" src="https://github.com/user-attachments/assets/1f41135d-7ae7-4ab6-8346-1c6becfabd9b">
</p>

MyLeagueOracle is a prediction system for your favourite Spanish soccer league based on Machine Learning. It was born as a personal project with the goal of implementing MLOps techniques and tools.

Every week, new soccer stats are retrieved and inserted into a relational database. After that, a few models are trained with all the data and the best one is deployed. This model is later consumed with an standard API design pattern: backend loads last model and deploys it and send predictions to frontend.

Below you can see a kind of architecture diagram that summarizes the deployed system  
<br/>

![myleagueoracle-arch](https://github.com/user-attachments/assets/ba5a980a-42a0-4607-a9e4-775c7aee51bb)



## How it works
<br/>

![laliga-oracle-Copia de flows drawio](https://github.com/user-attachments/assets/bd8a51be-270a-479d-8dec-519eee3fcb5b)


1. Prefect flow #1: ETL. Weekly ETL that makes calls to the api-football API (through RapidAPI), in order to retrieve the latest results: weekly snapshot of each team and match results update.
2. Prefect flow #2: Train models. Weekly ETL that runs after #1. It reads updated data from DB, preprocesses it and train a list of ML models. The best one is selected and pushed to MLFlow. All of them are tracked in order to follow have access to all metrics, but only one is promoted as best weekly model.
3. Backend retrieves data from DB and loads best model from MLFlow.
4. User (frontend) sends requests about matches by selecting two teams, backend answers with predicted results.

## CI / CD
- ✅ Backend (Koyeb). Backend CI is made with koyeb utilities. A dockerfile is on the root of this repo and everytime a commit is done to main, it builds a new image and deploys it. Files listed in .koyebignore file don't trigger this build.
- ✅ ML Models (MLFlow / FastAPI). ETLs log all models to MLFlow. The best one is promoted to an specific Production model
- 🚧WIP. ETLs (Prefect Cloud).
- 🚧WIP. Frontend (Reflex Cloud)


## Folders structure
- backend/. FastAPI microservice. Exposes API to load model, read data and make predictions.
- frontend/. Reflex frontend. Sends prediction requests to backend API.
- notebooks/. Notebooks used during development time.
- orchestration/. Prefect code for ETLs.
- .gitignore
- .koyebignore. Files excluded from koyeb CI/CD deployments.
- Dockerfile. Backend dockerfile.
- db_neon_setup.py. Utils file to create, delete and export database and tables.
- prefect.yaml. Prefect deployment file.


### Limitations
I have tried to use as many free cloud providers as possible, reaching in some cases certain limitations:
- Koyeb returns sometimes, on the first request, a 500 Internal Server Error. In order to fix it, a new request must be done a second later.
- Koyeb's Hobby Plan is limited to 1 web service with specs 0.1 vCPU, 512MB RAM, 1 GiB Disk.
- Neon's Free Plan is limited to 0.25 vCPU, 0.5 GiB storage.
- Reflex Cloud is suffering a lot of changes on version 0.6.6 and deployment is not stable.
