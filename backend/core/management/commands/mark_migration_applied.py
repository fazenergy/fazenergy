from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

class Command(BaseCommand):
    help = "Marca uma migração como aplicada no django_migrations sem executá-la (uso: app_label migration_name)."

    def add_arguments(self, parser):
        parser.add_argument('app_label', type=str, help='App da migração (ex.: location)')
        parser.add_argument('migration_name', type=str, help='Nome da migração (ex.: 0001_initial)')

    def handle(self, *args, **options):
        app = options['app_label']
        name = options['migration_name']

        with connection.cursor() as cursor:
            # Verifica se já existe registro
            cursor.execute(
                "SELECT 1 FROM django_migrations WHERE app=%s AND name=%s",
                [app, name]
            )
            if cursor.fetchone():
                self.stdout.write(self.style.WARNING(f"Migração {app}.{name} já estava marcada como aplicada."))
                return

            applied = timezone.now()
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                [app, name, applied]
            )
        self.stdout.write(self.style.SUCCESS(f"Migração {app}.{name} marcada como aplicada."))
