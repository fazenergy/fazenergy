from django.apps import AppConfig


class ProposalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proposal'
    verbose_name = 'Propostas'  # Nome amigável para o admin
