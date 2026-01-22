"""Module entrypoint for `python -m docgen`."""

from .cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
