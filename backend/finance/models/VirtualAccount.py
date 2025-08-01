# finance/models.py
from django.db import models
from django.conf import settings

# Tabela de Conta Virtual
# Esta tabela armazena informações sobre as contas virtuais dos afiliados, incluindo saldo disponível 
class VirtualAccount(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='ID')
    licensed = models.OneToOneField(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='virtual_account',
        verbose_name='Licenciado'
    )
    name_licensed      = models.CharField(max_length=150, verbose_name='Nome do Licenciado')
    balance_available   = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Saldo Disponível')
    balance_blocked     = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Saldo Bloqueado')
    dtt_record          = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_update          = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'VirtualAccount'
        verbose_name = 'Conta Virtual'
        verbose_name_plural = 'Contas Virtuais'

    def __str__(self):
        return f"Conta Virtual de {self.name_licensed} (R$ {self.balance_available})"
