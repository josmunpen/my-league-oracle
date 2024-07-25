# laliga-oracle
LaLiga Oracle is a prediction system for LaLiga results based on Machine Learning. It was born as a personal project with the goal of implementing MLOps techniques and tools. 

I have tried to use as many free cloud providers as possible, reaching in some cases certain limitations listed in the [[#Limitations]] section.

Data is extracted from API-FOOTBALL (https://www.api-football.com/) using RapidAPI. Prefect is responsible for making periodic calls to extract the necessary data. Currently it only inserts into PostgreSQL, but it is expected that in the future it will be responsible for retraining and generating new ML models. FastAPI is the backend used to make the PostgreSQL data available and to perform the predictions. Currently we have opted for online inference instead of batch, but this strategy could be changed in the future.


### Roadmap
- [ ] Data retrieval
- [ ] Experiments: train a v0 model
- [ ] PostgreSQL deployment
- [ ] FastAPI deployment
- [ ] Prefect deployment
- [ ] Backend CI/CD
- [ ] Prefect CI/CD
- [ ] Data drift detector and model monitoring
- [ ] MLFlow/W&B deployment

### Architecture

![[laliga-oracle.drawio.png]]

### Limitations
- Koyeb returns sometimes, on the first request, a 500 Internal Server Error. In order to fix it, a new request must be done a second later.
- Koyeb's Hobby Plan is limited to 1 web service with specs 0.1 vCPU, 512MB RAM, 1 GiB Disk.
- Neon's Free Plan is limited to 0.25 vCPU, 0.5 GiB storage.
- Databricks community edition supports MLFlow "light" version. It includes experiments tracker but excludes model storing, for example.