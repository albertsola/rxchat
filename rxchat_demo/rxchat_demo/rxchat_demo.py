"""Welcome to Reflex! This file showcases the custom component in a basic app."""

from rxconfig import config
import reflex as rx
from reflex_rxchat.server.api import router

filename = f"{config.app_name}/{config.app_name}.py"


def index() -> rx.Component:
    from reflex_rxchat import conversation
    return rx.container(
        rx.color_mode.button(position="top-right"),
        conversation(),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
app.api.include_router(router)
