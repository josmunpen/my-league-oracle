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


def team_details_component():

    child = rx.hstack(
        rx.spacer(bg=rx.color("gray", 2)),
        rx.vstack(
            rx.form(
                rx.vstack(
                    form_field_select(name="input_details_team_name", label="Team"),
                    form_field(
                        label="Query date",
                        placeholder="E.g.: 2022-10-10",
                        type="date",
                        name="input_details_request_date",
                        default_value=datetime.today().strftime("%Y-%m-%d"),
                        required=True,
                    ),
                    #                    rx.text("* Required fields"),
                    rx.button("Submit", type="submit"),
                ),
                on_submit=State.handle_submit_team_details,
                reset_on_submit=True,
            ),
            rx.divider(),
            rx.heading("Results"),
            rx.data_table(
                data=State.team_details2,
                pagination=True,
                search=True,
                sort=True,
                columns=["Field", "Value"],
                # on_mount=State.load_data,
            ),
            on_mount=State.load_data_teams,
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
