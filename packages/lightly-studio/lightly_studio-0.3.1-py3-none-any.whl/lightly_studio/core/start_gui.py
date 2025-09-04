"""Module to launch the GUI."""

from __future__ import annotations

from lightly_studio.api.server import Server
from lightly_studio.dataset import env


def start_gui() -> None:
    """Launch the web interface for the loaded dataset."""
    server = Server(host=env.LIGHTLY_STUDIO_HOST, port=env.LIGHTLY_STUDIO_PORT)

    print(f"Open the LightlyStudio GUI under: {env.APP_URL}")

    server.start()
