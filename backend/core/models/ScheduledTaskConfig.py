from django.db import models


class ScheduledTaskConfig(models.Model):
    """Configuração de rotina agendada (Celery Beat).

    Armazena se a rotina está ativa e, quando desativada, o motivo.
    A chave deve corresponder à chave do CELERY_BEAT_SCHEDULE (ex.: 'finance.process_scheduled_withdraws_daily').
    """

    key = models.CharField(max_length=150, unique=True)
    task = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    disabled_reason = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ScheduledTaskConfig'
        verbose_name = 'Rotina Agendada (Config)'
        verbose_name_plural = 'Rotinas Agendadas (Config)'

    def __str__(self) -> str:
        return f"{self.key} ({'ativa' if self.active else 'inativa'})"


class ScheduledTaskLog(models.Model):
    """Log de ações sobre rotinas (ativar/desativar/executar)."""

    ACTIONS = (
        ('enable', 'Ativar'),
        ('disable', 'Desativar'),
        ('run_now', 'Executar Agora'),
    )

    config = models.ForeignKey(ScheduledTaskConfig, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTIONS)
    actor_username = models.CharField(max_length=150, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ScheduledTaskLog'
        verbose_name = 'Rotina Agendada (Log)'
        verbose_name_plural = 'Rotinas Agendadas (Logs)'
        indexes = [
            models.Index(fields=['config']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.config.key} - {self.action} por {self.actor_username or '-'}"


