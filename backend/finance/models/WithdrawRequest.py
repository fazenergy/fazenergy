from django.db import models
from django.conf import settings


class WithdrawRequest(models.Model):
    """Solicitação de saque da conta virtual para uma conta bancária cadastrada.

    Regras principais:
    - Uma solicitação fica com status 'pending' até processamento manual/automatizado.
    - Enquanto houver uma solicitação 'pending' do licenciado, uma nova não pode ser criada.
    - O valor solicitado deve respeitar valor mínimo configurado e saldo disponível.
    - Taxas e impostos: armazenados para transparência do histórico (podem ser 0).
    """

    STATUS = (
        ("pending", "Pendente"),
        ("scheduled", "Agendado"),
        ("processing", "Processando"),
        ("paid", "Pago"),
        ("canceled", "Cancelado"),
        ("rejected", "Rejeitado"),
    )

    licensed = models.ForeignKey('core.Licensed', on_delete=models.CASCADE, related_name='withdraw_requests')
    bank_account = models.ForeignKey('finance.BankAccount', on_delete=models.PROTECT, related_name='withdraw_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    note = models.TextField(blank=True, null=True)

    # Aprovação/Agendamento
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_withdraw_requests'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    scheduled_for = models.DateTimeField(blank=True, null=True)
    scheduled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scheduled_withdraw_requests'
    )
    expected_payout_date = models.DateField(blank=True, null=True)
    emergency_reason = models.TextField(blank=True, null=True)

    # Cancelamento
    canceled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='canceled_withdraw_requests'
    )
    canceled_at = models.DateTimeField(blank=True, null=True)
    cancel_reason = models.TextField(blank=True, null=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'WithdrawRequest'
        verbose_name = 'Solicitação de Saque'
        verbose_name_plural = 'Solicitações de Saque'
        indexes = [
            models.Index(fields=['licensed']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_for']),
        ]

    def __str__(self) -> str:
        return f"Saque #{self.id} - {self.licensed_id} - {self.amount} ({self.status})"


