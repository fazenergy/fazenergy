from django.db import models


class BankAccount(models.Model):
    """Conta bancária cadastrada para saque de um `core.Licensed`.

    Observações de domínio:
    - O titular pode ser Pessoa Física (PF) ou Jurídica (PJ).
    - Para PJ, a conta deve estar vinculada a uma empresa (`core.LicensedCompany`) do próprio licenciado
      e a empresa precisa estar com validação 'approved'.
    - Apenas contas do próprio licenciado podem ser usadas em solicitações de saque.
    """

    OWNER_TYPES = (
        ("pf", "Pessoa Física"),
        ("pj", "Pessoa Jurídica"),
    )

    ACCOUNT_TYPES = (
        ("corrente", "Conta Corrente"),
        ("poupanca", "Poupança"),
        ("pagamento", "Conta de Pagamento"),
    )

    licensed = models.ForeignKey(
        'core.Licensed', on_delete=models.CASCADE, related_name='bank_accounts', verbose_name='Licenciado'
    )
    owner_type = models.CharField(max_length=2, choices=OWNER_TYPES, default='pf')
    # Para PJ, company é obrigatório; para PF deve ser nulo
    company = models.ForeignKey(
        'core.LicensedCompany', on_delete=models.CASCADE, null=True, blank=True, related_name='bank_accounts'
    )

    # Identificação do banco e tipo de conta
    bank_code = models.CharField(max_length=10, verbose_name='Código do Banco')
    bank_name = models.CharField(max_length=80, blank=True, null=True, verbose_name='Nome do Banco')
    account_type = models.CharField(max_length=12, choices=ACCOUNT_TYPES, default='corrente')

    # Agência e conta com dígitos
    agency_number = models.CharField(max_length=10)
    agency_digit = models.CharField(max_length=5, blank=True, null=True)
    account_number = models.CharField(max_length=20)
    account_digit = models.CharField(max_length=5, blank=True, null=True)

    # Dados do titular (recomendado para conciliações/pagamentos)
    account_holder_name = models.CharField(max_length=120)
    account_holder_cpf_cnpj = models.CharField(max_length=20)

    is_default = models.BooleanField(default=False)

    dtt_record = models.DateTimeField(auto_now_add=True)
    dtt_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'BankAccount'
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        indexes = [
            models.Index(fields=['licensed']),
            models.Index(fields=['owner_type']),
            models.Index(fields=['bank_code']),
        ]

    def __str__(self) -> str:
        return f"{self.bank_code}-{self.account_number}-{self.account_digit} ({self.get_owner_type_display()})"


