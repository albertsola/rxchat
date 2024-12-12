"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxchat.server.api import router


def index() -> rx.Component:
    from rxchat.component.ui import chat
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        chat(),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
app.api.include_router(router)
