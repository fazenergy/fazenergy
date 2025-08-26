from django.db import models


class ProposalResult(models.Model):
    proposal = models.ForeignKey('contractor.Proposal', on_delete=models.CASCADE, related_name='results', verbose_name='Proposta')

    # Dados principais
    contract_type = models.CharField(max_length=100, verbose_name='Tipo de Contrato')
    contract_duration_months = models.IntegerField(null=True, blank=True, verbose_name='Duração (meses)')
    discount_percentage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Desconto (%)')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Desconto (R$)')
    annual_economy = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='Economia Anual (R$)')
    economy_in_three_years = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='Economia em 3 Anos (R$)')
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Parcela (R$)')
    total_installments = models.IntegerField(verbose_name='Total de Parcelas')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor Total (R$)')

    # Dados técnicos
    kwp = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='kWp')
    kwh_annual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='kWh Anual')
    required_area = models.IntegerField(null=True, blank=True, verbose_name='Área Necessária (m²)')
    qty_modules = models.IntegerField(null=True, blank=True, verbose_name='Qtd Módulos')

    # Distribuidora
    energy_provider_id = models.IntegerField(null=True, blank=True, verbose_name='Distribuidora (ID)')
    energy_provider_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Distribuidora (Nome)')
    provider_costs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Custos Distribuidora (R$)')
    revo_costs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Custos REVO (R$)')

    # Conta de luz
    electric_bill_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Conta de Luz (R$)')
    consumer_unit = models.CharField(max_length=50, null=True, blank=True, verbose_name='Unidade Consumidora')
    consumer_group = models.CharField(max_length=100, null=True, blank=True, verbose_name='Grupo de Consumo')

    # Datas
    proposal_expiration_at = models.DateTimeField(verbose_name='Expiração da Proposta')

    # Comuns
    status = models.CharField(max_length=50, default='Ativo', verbose_name='Status')
    usr_record = models.CharField(max_length=50, verbose_name='Usuário Registro')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')

    class Meta:
        db_table = 'ContractorProposalResult'
        verbose_name = 'Resultado de Proposta (Contractor)'
        verbose_name_plural = 'Resultados de Proposta (Contractor)'

    def __str__(self):
        return f"Resultado #{self.pk} - Proposta {self.proposal_id}"
