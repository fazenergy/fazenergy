from django.apps import AppConfig


class NetworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'network'
    verbose_name = "Rede de Licenciados"

    def ready(self):
        # Importa os sinais aqui para garantir que sejam registrados quando o app for carregado
        import network.signals  # Importa o arquivo de sinais
