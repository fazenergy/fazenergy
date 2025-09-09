from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Remove todos os registros da tabela django_admin_log (uso em DEV para corrigir FKs durante migrações)."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_admin_log")
        self.stdout.write(self.style.SUCCESS("django_admin_log limpo."))
