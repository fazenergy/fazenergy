from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Recalcula a ativação de todos os licenciados com base na regra de negócio: "
        "pagamento confirmado e documentos aprovados."
    )

    def handle(self, *args, **options):
        from core.models.Licensed import Licensed
        from core.utils_activation import ensure_licensed_activation

        updated = 0
        total = 0
        for lic in Licensed.objects.select_related('user').all().iterator():
            total += 1
            try:
                if ensure_licensed_activation(lic):
                    updated += 1
            except Exception:
                # Não interromper o processamento por registros problemáticos
                continue

        self.stdout.write(self.style.SUCCESS(f"Processados: {total} | Atualizados: {updated}"))


