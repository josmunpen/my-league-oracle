import reflex as rx
from ..ui.base import base_page


def about_page() -> rx.Component:
    child = rx.box(
        
        rx.center(
            rx.container(
                rx.vstack(
                    rx.markdown(
            """
            <div style="text-align: justify">

            # MyLeagueOracle
            
            </div>
            """
                    ),
                    rx.image(src="https://github.com/user-attachments/assets/1f41135d-7ae7-4ab6-8346-1c6becfabd9b",
                             width="30%"),
                    rx.markdown(
            """
            <div style="text-align: justify">

            MyLeagueOracle is a prediction system for your favourite league results based on Machine Learning. It was born as a personal project with the goal of implementing MLOps techniques and tools. 

            ## About MyLeagueOracle
            MyLeagueOracle is a free platform to predict your favourite league matches results. 

            </div>
            """
                    ),
                    rx.blockquote(
                        rx.markdown(
            """
            The focus is on the deployment of the various components and the connectivity between them, as well as the CI/CD cycles. This is **not** a project to develop the ML model with best metrics. I have tried to keep things simple in that regard.
            """
                        ),
                    ),
                    rx.markdown(
            """
            
            <div style="text-align: justify">
            Since I usually find weaknesses on these kind of tasks on data scienctist profiles, I decided to learn current best practices and (maybe) this will help somebody to start his/her journey

            Data is extracted from API-FOOTBALL (https://www.api-football.com/) via RapidAPI. Prefect is responsible for making periodic calls to extract the necessary data. Currently it only inserts into PostgreSQL, but it is expected that in the future it will be responsible for retraining and generating new ML models. FastAPI is the backend used to make the PostgreSQL data available and to perform the predictions. MLFlow hosts machine learning models.

            Following image shows a kind of simplified architecture diagram

            ![myleagueoracle](https://github.com/user-attachments/assets/8d1c1c33-15a7-49e6-b20d-c820ea6c1d1f)

            CI/CD is configured to automatically publish new Prefect flows when they're pushed to Git main branch. Backend code is also automatically pushed to Koyeb when a Pull Request is commited to main branch. If this deployment fails, it automatically rollbacks to last stable version. 

            No automation is added to database. It would make sense to add a migration tool like alembic but right now I want to keep things as simple as possible. I developed a simple tool (available at [db_neon_setup.py](https://github.com/josmunpen/laliga-oracle/blob/main/db_neon_setup.py "db_neon_setup.py")) to drop tables, create new schemas, etc.
            
            </div>

            """),
                    rx.blockquote(
                    """
                        Right now, I push manually ML models to MLFlow. Next step: this will be automated and Prefect will push the best model every week.
                    """),
                    rx.blockquote(
                    """

                        Currently I have opted for online inference instead of batch, but this strategy could be changed in the future.

                    """),
                    rx.blockquote(
                    """
                        I have tried to use as many free cloud providers as possible, reaching in some cases certain limitations listed in the next section.
                    """),
                    rx.markdown(
            """

            <div style="text-align: justify">
            
            ### Limitations
            - Koyeb returns sometimes, on the first request, a 500 Internal Server Error. In order to fix it, a new request must be done a second later.
            - Koyeb's Hobby Plan is limited to 1 web service with specs 0.1 vCPU, 512MB RAM, 1 GiB Disk.
            - Neon's Free Plan is limited to 0.25 vCPU, 0.5 GiB storage.

            ## About me
            I'm a Machine Learning Engineer that tries to put together Software Engineering and Machine Learning as much as possible. With these kind of projects I try to put on practice things that I can't develop on my current jobs, and try to help others start their ML journey.

            You can find me on [LinkedIn](https://www.linkedin.com/in/jmmunizpena/) or [send me a mail](mailto:josemamup@gmail.com)

            Check out [code on Git](https://github.com/josmunpen/laliga-oracle)

            This tool does not include advertising and is not for profit.


            </div>
            """
            )
                , 
                align="center",
                justify="center"
                ),
            width="30%",
            background_color="white",

            )
        ),
    width="100%",
    background_color=rx.color("gray", 2),
    )
    return base_page(child)