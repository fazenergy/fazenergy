# Isola as transações da conta virtual.
from django.db import models

# # Tabela de Transações da Conta Virtual
# Esta tabela armazena as transações realizadas nas contas virtuais, incluindo créditos e débitos
# e o status de cada transação.
class VirtualAccountTransaction(models.Model):
    STATUS_CHOICES = [
        ('blocked', 'Bloqueado'),
        ('released', 'Liberado'),
        ('canceled', 'Cancelado'),
    ]

    OPERATION_CHOICES = [
        ('credit', 'Crédito'),
        ('debit', 'Débito'),
    ]

    virtual_account = models.ForeignKey(
        'finance.VirtualAccount', 
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Conta Virtual"
    )

    product = models.CharField(
        max_length=255,
        verbose_name="Produto"
    )

    description = models.TextField(
        blank=True, null=True,
        verbose_name="Descrição"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='blocked',
        verbose_name="Status"
    )

    operation = models.CharField(
        max_length=10,
        choices=OPERATION_CHOICES,
        verbose_name="Operação"
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Valor"
    )

    is_processed = models.BooleanField(
        default=False,
        verbose_name="Processado?"
    )

    reference_date = models.DateField(
        verbose_name="Data de Referência"
    )

    dtt_record = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    def __str__(self):
        return f"{self.product} - {self.operation} - {self.amount}"

    class Meta:
        db_table = 'tb_Transaction'
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

