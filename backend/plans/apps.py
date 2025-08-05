from django.apps import AppConfig


class PlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plans'
    verbose_name = 'Planos'  # Nome amigável para o admin

    def ready(self):
        import plans.signals  # importa o signal
