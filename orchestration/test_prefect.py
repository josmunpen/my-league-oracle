from prefect import flow
import datetime

@flow(log_prints=True)
def hello_world(name: str = "world", goodbye: bool = False):
    print(f"Hello {name} from Prefect! 🤗, {datetime.datetime.now()}")

    if goodbye:
        print(f"Goodbye {name}!")


if __name__ == "__main__":
    # hello_world.serve(name="hola-mundo",
    #                   tags=["onboarding"],
    #                   parameters={"goodbye": True},
    #                   cron="* * * * *",
    #                   )
    hello_world.deploy(
                    name="hola-mundo",
                    tags=["onboarding"],
                    parameters={"goodbye": True},
                    cron="* * * * *",
                    work_pool_name="work-pool-2"
    )