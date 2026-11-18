from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management import BaseCommand, call_command
from flags.models import FlagState


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Starting configuring development environment", self.style.WARNING)
        if not settings.DEBUG:
            self.stdout.write("This command can be used only if DEBUG is True", self.style.ERROR)
            return

        call_command("upgrade")

        self.stdout.write("Configuring site settings")
        Site.objects.update_or_create(pk=settings.SITE_ID, defaults={"domain": "localhost:8000", "name": "localhost"})
        Site.objects.clear_cache()

        self.stdout.write("Setting up flags")
        flag_states = [
            FlagState(name=flag, condition="hostname", value="127.0.0.1,localhost") for flag in settings.FLAGS
        ]
        FlagState.objects.bulk_create(flag_states, ignore_conflicts=True)
