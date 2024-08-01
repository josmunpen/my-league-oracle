from prefect import flow
import datetime

@flow(log_prints=True)
def hola_mundo(name: str = "world", goodbye: bool = False):
    print("Lanzando en prefect cloud")
    print(f"Hello {name} from Prefect! 🤗, {datetime.datetime.now()}")

    if goodbye:
        print(f"Goodbye {name}!")