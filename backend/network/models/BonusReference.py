import uuid
from django.db import models


class BonusReference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relaciona com o produto (ex.: plano/usina) que originou o bônus
    product = models.ForeignKey(
        'network.Product',
        on_delete=models.PROTECT,
        related_name='bonus_references',
        verbose_name='Produto Origem',
    )

    # Licenciado recebedor do bônus
    receiver_licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='received_bonus',
        verbose_name='Licenciado Recebedor',
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor do Bônus')

    STATUS_CHOICES = [
        ('blocked', 'Bloqueado'),
        ('released', 'Liberado'),
        ('canceled', 'Cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='blocked', verbose_name='Status')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'BonusReference'
        verbose_name = 'Referência de Bônus'
        verbose_name_plural = 'Referências de Bônus'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver_licensed']),
            models.Index(fields=['product']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"{self.amount} → {self.receiver_licensed} ({self.get_status_display()})"


