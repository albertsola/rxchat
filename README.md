# Reflex Chat (rxchat)
[![Tests](https://github.com/albertsola/rxchat/actions/workflows/tests.yml/badge.svg)](https://github.com/albertsola/rxchat/actions/workflows/tests.yml)

Reflex Chat (rxchat) is a versatile and efficient chat interface designed to seamlessly integrate into Reflex projects. Built with the Reflex framework for the frontend and FastAPI for the backend, rxchat offers developers a ready-to-use chat solution that combines simplicity, flexibility, and performance.

![RxChat preview](preview.png "RxChat preview")

## Features

- **Frontend Integration**: Easily integrates with Reflex-based projects for a smooth UI experience.
- **Backend Support**: Powered by FastAPI for fast, reliable, and scalable backend operations.
- **Customizable**: Modify and extend the chat interface to suit your specific needs.
- **Real-Time Communication**: Support for real-time messaging using WebSockets.

## Installation

```bash
pip install reflex_rxchat
```

## Register ChatServer with FastAPI

```python
import reflex as rx
from reflex_rxchat.server.api import router

app = rx.App()
# Add your other configurations here
app.api.include_router(router)
```

## Add the conversation component into a page

```python
def index() -> rx.Component:
    from reflex_rxchat import conversation
    return rx.container(
        rx.color_mode.button(position="top-right"),
        conversation(),
        rx.logo(),
    )
```

## Demo projects

```python
# File: rxchat_demo/rxchat_demo.py

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
```

# Contributing

Issues: [Issues](https://github.com/albertsola/rxchat/issues)
Contributing: [CONTRIBUTING.md](https://github.com/albertsola/rxchat/blob/main/CONTRIBUTING.md)
