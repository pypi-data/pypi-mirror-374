"""
Django management commands to handle backup and restore learning packages (WIP)
"""
import logging

from django.core.management import CommandError
from django.core.management.base import BaseCommand

from openedx_learning.apps.authoring.backup_restore.api import create_zip_file
from openedx_learning.apps.authoring.publishing.api import LearningPackage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command to export a learning package to a zip file.
    """
    help = 'Export a learning package to a zip file.'

    def add_arguments(self, parser):
        parser.add_argument('lp_key', type=str, help='The key of the LearningPackage to dump')
        parser.add_argument('file_name', type=str, help='The name of the output zip file')

    def handle(self, *args, **options):
        lp_key = options['lp_key']
        file_name = options['file_name']
        if not file_name.endswith(".zip"):
            raise CommandError("Output file name must end with .zip")
        try:
            create_zip_file(lp_key, file_name)
            message = f'{lp_key} written to {file_name}'
            self.stdout.write(self.style.SUCCESS(message))
        except LearningPackage.DoesNotExist as exc:
            message = f"Learning package with key {lp_key} not found"
            raise CommandError(message) from exc
        except Exception as e:
            message = f"Failed to export learning package '{lp_key}': {e}"
            logger.exception(
                "Failed to create zip file %s (learning‑package key %s)",
                file_name,
                lp_key,
            )
            raise CommandError(message) from e
