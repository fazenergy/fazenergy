# finance/models.py
from django.db import models
from django.conf import settings

# Tabela de Conta Virtual
# Esta tabela armazena informações sobre as contas virtuais dos afiliados, incluindo saldo disponível 
class VirtualAccount(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    affiliate = models.OneToOneField(
        'core.Affiliate',
        on_delete=models.CASCADE,
        related_name='virtual_account',
        verbose_name='Afiliado'
    )
    name_affiliate      = models.CharField(max_length=150, verbose_name='Nome do Afiliado')
    balance_available   = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Saldo Disponível')
    balance_blocked     = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Saldo Bloqueado')
    dtt_record          = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_update          = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'tb_VirtualAccount'
        verbose_name = 'Conta Virtual'
        verbose_name_plural = 'Contas Virtuais'

    def __str__(self):
        return f"Conta Virtual de {self.name_affiliate} (R$ {self.balance_available})"






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
