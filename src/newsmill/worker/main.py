"""Entry point for the NewsMill Worker service."""

from __future__ import annotations

from newsmill.common.config import Settings
from newsmill.worker.app import create_app


def main() -> None:
    """Run the FastStream Worker application."""
    settings = Settings()
    app = create_app(settings)
    app.run()


if __name__ == "__main__":
    main()
