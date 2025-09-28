from django.db import models


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

    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'WithdrawRequest'
        verbose_name = 'Solicitação de Saque'
        verbose_name_plural = 'Solicitações de Saque'
        indexes = [
            models.Index(fields=['licensed']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"Saque #{self.id} - {self.licensed_id} - {self.amount} ({self.status})"


