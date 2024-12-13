# Reflex Chat (rxchat)
[![Tests](https://github.com/albertsola/rxchat/actions/workflows/tests.yml/badge.svg)](https://github.com/albertsola/rxchat/actions/workflows/tests.yml)

Reflex Chat (rxchat) is a versatile and efficient chat interface designed to seamlessly integrate into Reflex projects. Built with the Reflex framework for the frontend and FastAPI for the backend, rxchat offers developers a ready-to-use chat solution that combines simplicity, flexibility, and performance.

![RxChat preview](preview.png "RxChat preview")

## Features

- **Frontend Integration**: Easily integrates with Reflex-based projects for a smooth UI experience.
- **Backend Support**: Powered by FastAPI for fast, reliable, and scalable backend operations.
- **Customizable**: Modify and extend the chat interface to suit your specific needs.
- **Real-Time Communication**: Support for real-time messaging using WebSockets.

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.13
- poetry

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/albertsola/rxchat.git
   cd rxchat
   ```

2. Install Python dependencies:
   ```bash
   poetry install
   poetry run reflex init
   ```
3. Run the project:
   ```bash
   poetry run reflex run
   ```

5. Project running:
   App running at: http://localhost:3000
   Backend running at: http://0.0.0.0:8000/api/docs


### Testing

```
poetry run flake8 rxchat

poetry run mypy rxchat

poetry run pytest

poetry run coverage run

poetry run tox
```
