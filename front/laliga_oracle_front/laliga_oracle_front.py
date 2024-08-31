import reflex as rx
from rxconfig import config
from .pages.teams import teams_table_component
from .pages.team_detail import team_details_component
from .pages.oracle import oracle_component
from .state import State
from .ui.base import base_page
from .pages.about import about_page

def navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(rx.text(text, size="4", weight="medium"), href=url)


def navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.image(
                        src="/logo.jpg",
                        width="2.25em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading("Reflex", size="7", weight="bold"),
                    align_items="center",
                ),
                rx.hstack(
                    navbar_link("Home", "/#"),
                    navbar_link("About", "/#"),
                    navbar_link("Pricing", "/#"),
                    navbar_link("Contact", "/#"),
                    justify="end",
                    spacing="5",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        rx.mobile_and_tablet(
            rx.hstack(
                rx.hstack(
                    rx.image(
                        src="/logo.jpg",
                        width="2em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading("Reflex", size="6", weight="bold"),
                    align_items="center",
                ),
                rx.menu.root(
                    rx.menu.trigger(rx.icon("menu", size=30)),
                    rx.menu.content(
                        rx.menu.item("Home"),
                        rx.menu.item("About"),
                        rx.menu.item("Pricing"),
                        rx.menu.item("Contact"),
                    ),
                    justify="end",
                ),
                justify="between",
                align_items="center",
            ),
        ),
        bg=rx.color("accent", 3),
        padding="1em",
        # position="fixed",
        # top="0px",
        # z_index="5",
        width="100%",
    )


def index() -> rx.Component:
    # Welcome Page (Index)
    child = rx.container(
        rx.vstack(
            rx.heading("Welcome to laliga-oracle!", size="9"),
            rx.text(
                "Your favourite AI based predictions app.",
                size="5",
            ),
            rx.link(
                rx.button("Predict a result!"),
                href="/oracle",
                is_external=False,
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        )
    )
    return base_page(child)



app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="large", accent_color="ruby"
    )
)
app.add_page(index, route="/")
app.add_page(about_page, route="/about")
app.add_page(teams_table_component, route="/teams_data")
app.add_page(team_details_component, route="/team_details")
app.add_page(oracle_component, route="/oracle")
