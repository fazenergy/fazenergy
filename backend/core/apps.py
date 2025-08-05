from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Sistema Central'  # Nome amigável para o admin

    def ready(self):
        import finance.signals  # Importa o signals.py
        import core.signals  # ajusta conforme sua estrutura
