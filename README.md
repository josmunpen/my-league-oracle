# laliga-oracle

<p align="center" width="100%">
    <img width="30%" src="https://github.com/user-attachments/assets/1f41135d-7ae7-4ab6-8346-1c6becfabd9b">
</p>

MyLeagueOracle is a prediction system for your favorite Spanish soccer league powered by Machine Learning. It started as a personal project aimed at implementing MLOps techniques and tools.

Every week, new soccer statistics are retrieved and stored in a relational database. After that, multiple models are trained using all available data and the best-performing one is deployed. This model is accessed via a standard API design pattern: the backend loads the latest model, deploys it, and provides predictions to the frontend.

Below is an architectural diagram summarizing the deployed system  
<br/>

![myleagueoracle-arch](https://github.com/user-attachments/assets/ba5a980a-42a0-4607-a9e4-775c7aee51bb)



## How it works
<br/>

![laliga-oracle-Copia de flows drawio](https://github.com/user-attachments/assets/bd8a51be-270a-479d-8dec-519eee3fcb5b)


**1. Prefect flow #1: ETL**. A weekly ETL process calls the API-Football API (via RapidAPI) to retrieve the latest results, including a weekly snapshot of each team and updated match results.

<details> 
    <summary> <em>More details</em> </summary>
    
Once a week, a snapshot is retrieved for each team. This is scheduled on Wednesday to ensure the team has played its match (some matches take place on Monday, so Tuesday provides a margin to ensure the API-Football data has been updated). Match data is also updated, primarily with the result of each match. These API calls populate the _matches_ and _teams_ tables.

An additional table, requests, tracks the number of requests made each day. Since Prefect has a limit of 100 requests per day, exceeding this would incur additional costs. To avoid this, a handler is used as a decorator for functions that call RapidAPI.

![image](https://github.com/user-attachments/assets/18c015c4-17b8-4148-b38f-ef1fb3265131)
<div align="center">
  <em>Prefect flows overview</em>
</div>

</details>

**2. Prefect flow #2: Train models**. A weekly ETL process that runs after flow #1. It reads updated data from the database, preprocesses it, and trains a list of ML models. The best-performing model is selected and pushed to MLFlow. All models are tracked to ensure access to their metrics, but only one is promoted as the best weekly model.

<details> 
         <summary> <em>More details</em> </summary>
         
If ETL #1 succeeds, this flow is triggered. It processes database data to create a row for each match, describing both teams (using their latest snapshot before the match) and the result. This data is used to train several supervised models with scikit-learn. All models are logged to MLFlow to track their metrics, but only the best-performing one is promoted to the Production model.

Additionally, if other types of transformers are used during data preprocessing, they are also pushed to MLFlow. For example, the One-Hot Encoder (OHE) used for team IDs is always promoted to production to ensure that the same encoder is used during inference. If the input contains a team ID that the OHE has not encountered before, it will raise an exception.

Once the process is complete, it makes a GET request to the backend API to refresh the loaded model used for predictions. This refresh can also be done manually if needed.

![image](https://github.com/user-attachments/assets/d44177ce-6548-4787-b5ed-022b9c02da47)
<div align="center">
  <em>Example of executions in MLflow </em>
</div>

</details>

**3. Backend retrieves data from database and loads the best model from MLFlow.**

<details> 
         <summary> <em>More details</em> </summary>
         
The backend exposes an API that handles basic use cases: refreshing the loaded ML model, retrieving a snapshot of a team (win streak, points, position, etc.), and making predictions by sending two team IDs.

It implements the singleton pattern to ensure that only a single instance of the model is loaded. While this is not a concern for small models (e.g., k-NN, logistic regression), the implementation is designed to support larger models, such as deep learning neural networks.

![image](https://github.com/user-attachments/assets/6d348fe3-2e73-43ec-bb9e-e222995bbd21)
<div align="center">
  <em>API documentation (following OpenAPI standard)</em>
</div>

</details>

**4. The user (frontend) sends requests about matches by selecting two teams, and the backend responds with the predicted results.**
<details> 
         <summary> <em>More details</em> </summary>
         
At the start, I didn’t want to build a frontend, but everyone was telling me to create one so that there was something to see (I still think that seeing an API is prettier 😜). I decided to use Reflex because it seemed powerful enough and easy to develop and deploy. Please don’t judge the code; the focus of this project is not on learning any frontend framework, and I tried not to spend too much time on it.

There are three main views: the welcome page, the oracle (predictions), and the team details.

![image](https://github.com/user-attachments/assets/8cbe0be9-c1a4-4702-9875-57e46ba907d2)
![image](https://github.com/user-attachments/assets/c8bdcfd7-a9d9-4981-9068-b63d5205b601)
<div align="center">
  <em>Frontend screenshots (oracle and team details view)</em>
</div>

</details>

    
## CI / CD
- ✅ Backend (Koyeb): Backend CI is managed with Koyeb utilities. A Dockerfile is located at the root of this repo, and every time a commit is made to the main branch, it builds a new image and deploys it. Files listed in the .koyebignore file do not trigger this build.
- ✅ ML Models (MLFlow / FastAPI): ETLs log all models to MLFlow. The best one is promoted to a specific Production model.
- 🚧 WIP: ETLs (Prefect Cloud).
- 🚧 WIP: Frontend (Reflex Cloud).


## Folder structure
- backend/: FastAPI microservice. Exposes an API to load the model, read data, and make predictions.
- frontend/: Reflex frontend. Sends prediction requests to the backend API.
- notebooks/: Notebooks used during development.
- orchestration/: Prefect code for ETLs.
- .gitignore: Specifies files to be ignored by Git.
- .koyebignore: Specifies files excluded from Koyeb CI/CD deployments.
- Dockerfile: Backend Dockerfile.
- db_neon_setup.py: Utility file to create, delete, and export databases and tables.
- prefect.yaml: Prefect deployment file.


### Limitations
I have tried to use as many free cloud providers as possible, but in some cases, I have encountered certain limitations:
- Koyeb sometimes returns a 500 Internal Server Error on the first request. To resolve this, a new request must be made a second later.
- Koyeb's Hobby Plan is limited to 1 web service with the following specs: 0.1 vCPU, 512MB RAM, and 1 GiB Disk.
- Neon's Free Plan is limited to 0.25 vCPU and 0.5 GiB of storage.
- Reflex Cloud is undergoing many changes in version 0.6.6, and deployment is not stable.

