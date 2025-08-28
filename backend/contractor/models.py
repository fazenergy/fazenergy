from django.db import models


class Contractor(models.Model):
    licensed = models.ForeignKey('core.Licensed', on_delete=models.PROTECT, related_name='contractors', verbose_name='Licenciado (Indicador)')
    lead_name = models.CharField(max_length=255, verbose_name='Nome do Lead')
    email = models.EmailField(verbose_name='E-mail')
    cellphone = models.CharField(max_length=20, verbose_name='Celular')
    zip_code = models.CharField(max_length=10, verbose_name='CEP')
    # Dados do contratante
    person_type = models.CharField(max_length=2, choices=[('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')], default='PF', verbose_name='Tipo de Pessoa')
    fiscal_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='CPF/CNPJ (sem máscara)')
    legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Razão Social (se PJ)')
    contractor_zip_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='CEP (Contratante)')
    contractor_address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Endereço (Contratante)')
    contractor_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Número (Contratante)')
    contractor_complement = models.CharField(max_length=255, null=True, blank=True, verbose_name='Complemento (Contratante)')
    contractor_neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name='Bairro (Contratante)')
    contractor_city = models.CharField(max_length=255, null=True, blank=True, verbose_name='Cidade (Contratante)')
    contractor_st = models.CharField(max_length=2, null=True, blank=True, verbose_name='UF (Contratante)')
    # Preferências/últimos
    preferred_property_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='Tipo de Imóvel Preferido')
    last_electric_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Última Conta de Luz (R$)')
    last_energy_provider_id = models.IntegerField(null=True, blank=True, verbose_name='Última Distribuidora (ID)')
    last_energy_provider_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Última Distribuidora (Nome)')
    reference_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='Código de Referência')
    # Status
    status = models.CharField(max_length=100, default='Novo', verbose_name='Status')
    # Metadados
    usr_record = models.CharField(max_length=50, verbose_name='Usuário Registro')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    usr_update = models.CharField(max_length=50, null=True, blank=True, verbose_name='Usuário Atualização')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'Contractor'
        managed = False
        ordering = ['-dtt_record']


class Proposal(models.Model):
    contractor = models.ForeignKey('contractor.Contractor', on_delete=models.CASCADE, related_name='proposals', verbose_name='Contractor', db_column='contractor_id')
    product = models.ForeignKey('network.Product', on_delete=models.PROTECT, related_name='proposals', verbose_name='Produto', null=True, blank=True)
    reference_code = models.CharField(max_length=50, verbose_name='Código de Referência')
    zip_code = models.CharField(max_length=10, verbose_name='CEP')
    address = models.CharField(max_length=255, verbose_name='Endereço')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=255, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=255, verbose_name='Cidade')
    state = models.CharField(max_length=2, verbose_name='UF')
    contract_person = models.CharField(max_length=100, choices=[('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')], verbose_name='Tipo de Contratante')
    property_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='Tipo de Imóvel')
    owner = models.CharField(max_length=100, verbose_name='Proprietário')
    is_owner_self = models.BooleanField(default=True, verbose_name='Imóvel Próprio?')
    seller_email = models.EmailField(null=True, blank=True, verbose_name='E-mail do Vendedor')
    nsu = models.CharField(max_length=100, null=True, blank=True, verbose_name='NSU')
    cpf_cnpj = models.CharField(max_length=20, null=True, blank=True, verbose_name='CPF/CNPJ')
    legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Razão Social')
    email = models.EmailField(null=True, blank=True, verbose_name='E-mail do Cliente')
    electric_bill_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Conta de Luz (R$)')
    consumer_unit = models.CharField(max_length=100, null=True, blank=True, verbose_name='Unidade Consumidora')
    consumer_group = models.CharField(max_length=100, null=True, blank=True, verbose_name='Grupo de Consumo')
    monthly_consumption = models.JSONField(null=True, blank=True, verbose_name='Consumo Mensal (kWh)')
    energy_provider_id = models.IntegerField(null=True, blank=True, verbose_name='Distribuidora (ID)')
    energy_provider_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Distribuidora (Nome)')
    status = models.CharField(max_length=100, default='Aguardando', verbose_name='Status')
    usr_record = models.CharField(max_length=50, verbose_name='Usuário Registro')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_expired = models.DateTimeField(null=True, blank=True, verbose_name='Data Expiração')
    usr_update = models.CharField(max_length=50, null=True, blank=True, verbose_name='Usuário Atualização')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'ContractorProposal'
        managed = False


class ProposalLeadActor(models.Model):
    ACTOR_CHOICES = [
        ('owner', 'Proprietário'),
        ('legal_responsible', 'Responsável Legal'),
    ]
    proposal = models.ForeignKey('contractor.Proposal', on_delete=models.CASCADE, related_name='lead_actors', verbose_name='Proposta')
    actor = models.CharField(max_length=20, choices=ACTOR_CHOICES, verbose_name='Ator')
    legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Razão Social')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nome')
    cpf_cnpj = models.CharField(max_length=20, null=True, blank=True, verbose_name='CPF/CNPJ')
    cellphone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Celular')
    email = models.EmailField(null=True, blank=True, verbose_name='E-mail')
    zip_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='CEP')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Endereço')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=255, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=255, null=True, blank=True, verbose_name='Cidade')
    st = models.CharField(max_length=2, null=True, blank=True, verbose_name='UF')

    class Meta:
        db_table = 'ContractorProposalLeadActor'
        managed = False


class ProposalResult(models.Model):
    proposal = models.ForeignKey('contractor.Proposal', on_delete=models.CASCADE, related_name='results', verbose_name='Proposta')
    contract_type = models.CharField(max_length=100, verbose_name='Tipo de Contrato')
    contract_duration_months = models.IntegerField(null=True, blank=True, verbose_name='Duração (meses)')
    discount_percentage = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Desconto (%)')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Desconto (R$)')
    annual_economy = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='Economia Anual (R$)')
    economy_in_three_years = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name='Economia em 3 Anos (R$)')
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Parcela (R$)')
    total_installments = models.IntegerField(verbose_name='Total de Parcelas')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor Total (R$)')
    kwp = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='kWp')
    kwh_annual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='kWh Anual')
    required_area = models.IntegerField(null=True, blank=True, verbose_name='Área Necessária (m²)')
    qty_modules = models.IntegerField(null=True, blank=True, verbose_name='Qtd Módulos')
    energy_provider_id = models.IntegerField(null=True, blank=True, verbose_name='Distribuidora (ID)')
    energy_provider_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Distribuidora (Nome)')
    provider_costs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Custos Distribuidora (R$)')
    revo_costs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Custos REVO (R$)')
    electric_bill_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Conta de Luz (R$)')
    consumer_unit = models.CharField(max_length=50, null=True, blank=True, verbose_name='Unidade Consumidora')
    consumer_group = models.CharField(max_length=100, null=True, blank=True, verbose_name='Grupo de Consumo')
    proposal_expiration_at = models.DateTimeField(verbose_name='Expiração da Proposta')
    status = models.CharField(max_length=50, default='Ativo', verbose_name='Status')
    usr_record = models.CharField(max_length=50, verbose_name='Usuário Registro')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')

    class Meta:
        db_table = 'ContractorProposalResult'
        managed = False


