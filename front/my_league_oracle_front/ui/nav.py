import reflex as rx
def navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.text(text, size="4", weight="medium"), href=url
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.image(
                        src="/league-oracle.png",
                        width="2.25em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading("My League Oracle", size="7", weight="bold"),
                    align_items="center",
                ),
                rx.hstack(
                    navbar_link("Home", "/#"),
                    navbar_link("Oracle", "/oracle"),
                    navbar_link("Team details", "/team_details"),
                    navbar_link("About", "/about"),
                    # navbar_link("Teams", "/teams_data"),
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
                        src="/league-oracle.png",
                        width="2em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading("My League Oracle", size="6", weight="bold"),
                    align_items="center",
                ),
                rx.menu.root(
                    rx.menu.trigger(rx.icon("menu", size=30)),
                    rx.menu.content(
                        rx.menu.item("Home", on_click=rx.redirect("/")),
                        rx.menu.item("Oracle", on_click=rx.redirect("/oracle")),
                        rx.menu.item("Team details", on_click=rx.redirect("/team_details")),
                        rx.menu.item("About", on_click=rx.redirect("/about")),
                        # rx.menu.item("Teams", on_click=rx.redirect("/teams_data")),
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