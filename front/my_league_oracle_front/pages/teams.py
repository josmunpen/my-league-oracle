import reflex as rx
import pandas as pd
import httpx
from ..state import State
from ..ui.base import base_page

def teams_table_component():

    return base_page(
        rx.center(
            rx.data_table(
                data=State.data_teams,
                pagination=True,
                search=True,
                sort=True,
                on_mount=State.load_data_teams
            )
        )
    )