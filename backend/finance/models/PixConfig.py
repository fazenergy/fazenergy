from django.db import models


class PixConfig(models.Model):
    """Configuração do provedor PIX (Sicoob), separada do Gateway (Pagar.me).

    Mantém URLs, credenciais e parâmetros de mTLS quando aplicável.
    """

    provider_name = models.CharField(max_length=50, default='Sicoob')
    api_base_url = models.URLField(blank=True, null=True)
    oauth_url = models.URLField(blank=True, null=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=1024, blank=True, null=True, help_text="Opcional (dev)")
    cert_path = models.CharField(max_length=512, blank=True, null=True)
    key_path = models.CharField(max_length=512, blank=True, null=True)

    # Webhook/Segurança
    webhook_url = models.URLField(blank=True, null=True)
    webhook_token = models.CharField(max_length=255, blank=True, null=True)
    webhook_user = models.CharField(max_length=100, blank=True, null=True)
    webhook_password = models.CharField(max_length=255, blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)

    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PixConfig'
        verbose_name = 'Configuração PIX'
        verbose_name_plural = 'Configurações PIX'

    def __str__(self) -> str:
        return f"{self.provider_name or 'PIX'} (ativo={self.active})"


