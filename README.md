# laliga-oracle

<p align="center" width="100%">
    <img width="30%" src="https://github.com/user-attachments/assets/1f41135d-7ae7-4ab6-8346-1c6becfabd9b">
</p>

MyLeagueOracle is a prediction system for your favourite league results based on Machine Learning. It was born as a personal project with the goal of implementing MLOps techniques and tools. 

I have tried to use as many free cloud providers as possible, reaching in some cases certain limitations listed in the [Limitations](#limitations) section.

Data is extracted from API-FOOTBALL (https://www.api-football.com/) via RapidAPI. Prefect is responsible for making periodic calls to extract the necessary data. Currently it only inserts into PostgreSQL, but it is expected that in the future it will be responsible for retraining and generating new ML models. FastAPI is the backend used to make the PostgreSQL data available and to perform the predictions. Currently we have opted for online inference instead of batch, but this strategy could be changed in the future.

### Architecture
![myleagueoracle-arch](https://github.com/user-attachments/assets/8d1c1c33-15a7-49e6-b20d-c820ea6c1d1f)


### Roadmap
- [x] Sample data retrieval
- [x] Experiments: train a v0 model
- [x] PostgreSQL deployment
- [x] FastAPI deployment
- [x] Backend CI/CD
- [x] Automate data retrieval
- [x] Prefect deployment
- [x] Prefect CI/CD
- [x] MLFlow/W&B deployment
- [ ] Data drift detector and model monitoring


### Limitations
- Koyeb returns sometimes, on the first request, a 500 Internal Server Error. In order to fix it, a new request must be done a second later.
- Koyeb's Hobby Plan is limited to 1 web service with specs 0.1 vCPU, 512MB RAM, 1 GiB Disk.
- Neon's Free Plan is limited to 0.25 vCPU, 0.5 GiB storage.
- Databricks community edition supports MLFlow "light" version. It includes experiments tracker but excludes model storing, for example.
