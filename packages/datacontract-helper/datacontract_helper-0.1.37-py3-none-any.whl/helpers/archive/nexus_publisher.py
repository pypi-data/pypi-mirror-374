import io
import os
import subprocess
import sys

import requests
from requests.auth import HTTPBasicAuth
from twine.commands.upload import upload

NEXUS_URL: str = os.environ["NEXUS_URL"]
NEXUS_USERNAME: str = os.environ["NEXUS_USERNAME"]
NEXUS_PASSWORD: str = os.environ["NEXUS_PASSWORD"]


class NexusPublisher:
    def __init__(self, package_path: str):
        result: subprocess.CompletedProcess = subprocess.run(
            args=[
                "uv",
                "run",
                "twine",
                "upload",
                "--repository-url",
                os.environ["NEXUS_URL"],
                "--username",
                os.environ["NEXUS_USERNAME"],
                "--password",
                os.environ["NEXUS_PASSWORD"],
                "dist/*",
            ],
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        # uv run python -m twine upload dist/*
        # uv run twine upload --repository-url repository_url --username username --password password  dist/*
