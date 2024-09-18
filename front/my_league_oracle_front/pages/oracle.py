import reflex as rx
import pandas as pd
import httpx
from ..state import State
from datetime import datetime
from ..ui.base import base_page


def form_field_select(
    name: str,
    label: str,
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.select(
                items=State.team_names, name=name, label=label, placeholder=label
            ),
            spacing="3",
        )
    )


def oracle_component():

    child = rx.hstack(
        rx.spacer(bg=rx.color("gray", 2)),
        rx.vstack(
            rx.text(
                "Enter two teams to make a prediction",
                size="7",
                weight="medium",
                high_contrast=True,
            ),
            rx.form(
                rx.vstack(
                    form_field_select(label="Team (home)", name="team_home"),
                    rx.text("VS", size="4", weight="bold"),
                    form_field_select(label="Team (away)", name="team_away"),
                    rx.button("Submit", type="submit"),
                    align="center",
                    justify="center",
                ),
                on_submit=State.handle_submit_oracle,
                reset_on_submit=False,
            ),
            rx.cond(
                State.show_prediction & State.form_oracle,
                rx.vstack(
                    rx.divider(),
                    rx.text("Oracle's prediction is...", size="5"),
                    rx.spacer(bg=rx.color("black", 2)),
                    rx.text(
                        State.prediction_winner_format,
                        size="7",
                        weight="medium",
                        # align="center",
                        high_contrast=True,
                    ),
                    rx.recharts.bar_chart(
                        rx.recharts.bar(
                            data_key="prob",
                            stroke=rx.color("accent", 9),
                            fill=rx.color("accent", 8),
                        ),
                        rx.recharts.x_axis(data_key="name"),
                        # rx.recharts.y_axis(domain=[0,1]),
                        rx.recharts.y_axis(),
                        data=State.prediction_probs_format,
                        width="100%",
                        height=250,
                    ),
                    spacing="9",
                    align="center",
                    justify="center",
                    width="100%",
                ),
            ),
            on_mount=State.load_data_teams,
            #                padding="28px",
            #                width="30%",
            border_radius="0.5rem",
            spacing="9",
            width="100%",
            max_width="80em",
            margin="0 auto",
            padding="1em",
        ),
        rx.spacer(bg=rx.color("gray", 2)),
        width="100%",
        height="100vh",
    )
    return base_page(child)
