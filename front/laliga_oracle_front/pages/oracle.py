import reflex as rx
import pandas as pd
import httpx
from ..state import State
from datetime import datetime
from ..ui.base import base_page



def form_field_select(
    name:str,
    label: str,
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.select(
                items=State.team_names,
                name=name,
                label=label
            ),
            direction="column",
            spacing="1",
        ),
        width="100%",
    )



def oracle_component():

    child = rx.center(
        rx.vstack(
            rx.form(
                rx.vstack(
                    rx.hstack(
                        form_field_select(
                            label="Team (home)",
                            name="team_home"
                        ),
                        form_field_select(
                            label="Team (away)",
                            name="team_away"
                        )
                    ),
                    rx.button("Submit", type="submit"),
                ),
                on_submit=State.handle_submit_oracle,
                reset_on_submit=False,
            ),
            rx.divider(),
            rx.heading("Oracle's winner prediction is..."),
            rx.text(State.prediction_winner_format),
            rx.recharts.bar_chart(
                rx.recharts.bar(
                    data_key="prob",
                    stroke=rx.color("accent", 9),
                    fill=rx.color("accent", 8)
                ),
                rx.recharts.x_axis(data_key="name"),
                rx.recharts.y_axis(),
                data=State.prediction_probs_format,
                width="100%",
                height=250
            ),
            on_mount=State.load_data_teams
        ),
    )

    return base_page(child)
