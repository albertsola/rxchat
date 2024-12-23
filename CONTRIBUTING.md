# RX Chat Contributing Guidelines

## Prerequisites

- Python 3.12
- Poetry

## Quality Assurance and Testing

To ensure code quality and functionality, please run the following commands:

```bash
# Linting
poetry run flake8

# Static type checking
poetry run mypy

# Running tests with coverage
poetry run pytest --cov
```

## Code Formatting

We use [Black](https://black.readthedocs.io/en/stable/) to maintain code consistency. Format your code by executing:

```bash
poetry run black [file_or_directory]
```

Replace `[file_or_directory]` with the specific file or directory you wish to format.

---

Thank you for contributing to RX Chat!
