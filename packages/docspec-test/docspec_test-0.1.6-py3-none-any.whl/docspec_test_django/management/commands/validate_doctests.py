from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand

from docspec_test.runtime import collect_results_for_module, print_pytest_like


class Command(BaseCommand):
    help = (
        "Validate docstring tests across configured Django packages or INSTALLED_APPS"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "packages",
            nargs="*",
            help="Optional dotted packages to scan; defaults to DOCSPEC_PACKAGES or INSTALLED_APPS",
        )

    def handle(self, *args, **options):
        pkgs = options["packages"] or getattr(settings, "DOCSPEC_PACKAGES", None)
        if not pkgs:
            pkgs = getattr(settings, "INSTALLED_APPS", [])

        results = []
        for pkg in pkgs:
            try:
                mod = import_module(pkg)
            except Exception as e:  # pragma: no cover
                self.stderr.write(self.style.ERROR(f"Cannot import {pkg}: {e}"))
                return 1
            results.extend(collect_results_for_module(mod))

        return print_pytest_like(results)
