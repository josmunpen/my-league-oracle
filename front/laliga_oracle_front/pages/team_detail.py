import reflex as rx
import pandas as pd
import httpx
from ..state import State
from datetime import datetime
from ..ui.base import base_page


def render_item(item: list):
    return rx.box(rx.text(rx.text.strong(item[0]), " :", rx.text(item[1]), as_="p"))


def form_field(
    label: str,
    placeholder: str,
    type: str,
    name: str,
    required=False,
    default_value: str | None = None,
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(
                    placeholder=placeholder,
                    type=type,
                    name=name,
                    default_value=default_value,
                    required=required,
                ),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        width="100%",
    )


def team_details_component():

    child = rx.center(
        rx.vstack(
            rx.form(
                rx.vstack(
                    form_field(
                        label="Team ID *",
                        placeholder="E.g.: 531",
                        type="number",
                        name="input_details_team_id",
                        required=True
                    ),
                    form_field(
                        label="Query date",
                        placeholder="E.g.: 2022-10-10",
                        type="date",
                        name="input_details_request_date",
                        default_value=datetime.today().strftime("%Y-%m-%d"),
                        required=True
                    ),
                    rx.text("* Required fields"),
                    rx.button("Submit", type="submit"),
                ),
                on_submit=State.handle_submit_team_details,
                reset_on_submit=True,
            ),
            rx.divider(),
            rx.heading("Results"),
            rx.text(State.form_team_details.to_string()),
            rx.divider(),
            rx.heading("Results clean"),
            rx.data_table(
                data=State.team_details,
                pagination=True,
                search=True,
                sort=True,
                # on_mount=State.load_data,
            ),
            rx.divider(),
            rx.heading("Results clean 2"),
            rx.box(
                "Radix Color",
                background_color="var(--plum-3)",
                border_radius="10px",
                width="80%",
                margin="16px",
                padding="16px",
            ),
            rx.divider(),
            rx.heading("Results clean 3"),
            rx.markdown(State.team_details2),
            rx.box(
                rx.grid(
                    rx.foreach(
                        State.team_details2,
                        render_item,
                    ),
                    columns="2",
                ),
                background_color="var(--plum-3)",
                # background_color="lightgray",
                border_radius="10px",
                width="80%",
                margin="16px",
                padding="16px",
            ),
        )
    )

    return base_page(child)
