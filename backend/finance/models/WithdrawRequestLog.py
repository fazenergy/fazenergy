from django.db import models
from django.conf import settings


class WithdrawRequestLog(models.Model):
    """Histórico de eventos de uma solicitação de saque.

    Armazena ações relevantes: requested, approved, scheduled, emergency_released,
    canceled, processed_paid, processed_rejected.
    """

    ACTIONS = (
        ("requested", "Solicitado"),
        ("approved", "Aprovado"),
        ("scheduled", "Agendado"),
        ("emergency_released", "Liberação Emergencial"),
        ("canceled", "Cancelado"),
        ("processed_paid", "Pago"),
        ("processed_rejected", "Rejeitado"),
    )

    withdraw_request = models.ForeignKey(
        'finance.WithdrawRequest', on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=32, choices=ACTIONS)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='withdraw_logs'
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'WithdrawRequestLog'
        verbose_name = 'Histórico de Saque'
        verbose_name_plural = 'Históricos de Saque'
        indexes = [
            models.Index(fields=['withdraw_request']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"WR#{self.withdraw_request_id} {self.action} por {getattr(self.actor, 'username', '-') if self.actor_id else '-'}"


