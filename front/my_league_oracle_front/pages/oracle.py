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
                label=label,
                placeholder=label
            ),
            spacing="3",
        )
    )

def oracle_component():

    child = rx.center(
        rx.vstack(
            rx.text("Enter two teams to make a prediction",
                size="7",
                weight="medium",
                high_contrast=True,),
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
                        ),
                        spacing="9",
                    ),
                    rx.flex(
                        rx.button("Submit", type="submit"),
                        align="end",
                        justify="end"
                    ),
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
                    rx.text("Oracle's prediction is...",
                            size="5"),
                    rx.center(
                        rx.vstack(
                            rx.text(State.prediction_winner_format,
                                    size="7",
                                    weight="medium",
                                    #align="center",
                                    high_contrast=True,),
                            rx.recharts.bar_chart(
                                rx.recharts.bar(
                                    data_key="prob",
                                    stroke=rx.color("accent", 9),
                                    fill=rx.color("accent", 8)
                                ),
                                rx.recharts.x_axis(data_key="name"),
                                #rx.recharts.y_axis(domain=[0,1]),
                                rx.recharts.y_axis(),
                                data=State.prediction_probs_format,
                                width="100%",
                                height=250,
                            ),
                        ),

                    ),
                    spacing="9",
                )
            ),
            on_mount=State.load_data_teams,
            background=rx.color("gray", 2),
            border=f"1.5px solid {rx.color('gray', 5)}",
            padding="28px",
            width="30%",
            border_radius="0.5rem",
            #max_width="400px",
            
            spacing="9"
        ),
    )

    return base_page(child)
