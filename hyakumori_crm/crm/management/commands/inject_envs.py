import os

from django.core.management.base import BaseCommand
from pathlib import Path
import json


class Command(BaseCommand):
    help = "Inject VUE_APP_* into static app index.html"

    def _build_inject_string(self, envs):
        """
        produce script to inject to html
        <script>
            window._env = {
                VUE_APP_GRAPHQL_HTTP: "VUE_APP_GRAPHQL_HTTP"
            }
        </script>
        """

        return f"<script>window._env = {json.dumps(envs)};</script>"

    def handle(self, *args, **kwargs):
        vue_envs = dict()
        target = Path(os.getenv("STATIC_DIR")).joinpath("index.html")

        for key, value in os.environ.items():
            if key.find("VUE_APP") >= 0:
                vue_envs[key] = value

        inject_value = self._build_inject_string(vue_envs)
        content = ""

        with open(target, "r") as file:
            content = file.readlines()
            content = "".join(content)

        content = content.replace("</head>", inject_value + "</head>")

        with open(target, "w+") as file:
            file.write(content)

        self.stdout.write("Finished!")
        self.stdout.write("====================")
        self.stdout.write(content)
        self.stdout.write("====================")
