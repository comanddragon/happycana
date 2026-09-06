"""Development ``runserver`` command backed by Gunicorn instead of Daphne."""

import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Run the ASGI application with Gunicorn and a Uvicorn worker."

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport",
            nargs="?",
            default="127.0.0.1:8000",
            help="Optional port number, or ipaddr:port (default: 127.0.0.1:8000).",
        )
        parser.add_argument(
            "--workers", "-w", type=int, default=2,
            help="Number of Gunicorn worker processes (default: 2).",
        )
        parser.add_argument(
            "--noreload", "--no-reload", action="store_false", dest="reload",
            help="Disable Gunicorn's development file reloader.",
        )
        parser.set_defaults(reload=True)

    def handle(self, *args, **options):
        addrport = options["addrport"]
        if addrport.isdigit():
            addrport = f"127.0.0.1:{addrport}"
        if ":" not in addrport:
            raise CommandError("Address must be a port or an ipaddr:port pair.")
        if options["workers"] < 1:
            raise CommandError("--workers must be at least 1.")

        command = [
            sys.executable,
            "-m", "gunicorn",
            "config.asgi:application",
            "--chdir", str(settings.BASE_DIR),
            "--worker-class", "uvicorn.workers.UvicornWorker",
            "--workers", str(options["workers"]),
            "--bind", addrport,
        ]
        if options["reload"]:
            command.append("--reload")

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Gunicorn ASGI server at http://{addrport}/ "
                f"with {options['workers']} workers"
            )
        )
        os.execv(sys.executable, command)
