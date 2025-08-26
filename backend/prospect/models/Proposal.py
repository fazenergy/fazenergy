from django.db import models


class Proposal(models.Model):
    prospect = models.ForeignKey('contractor.Contractor', on_delete=models.CASCADE, related_name='proposals', verbose_name='Contractor')
    product = models.ForeignKey('network.Product', on_delete=models.PROTECT, related_name='proposals', verbose_name='Produto', null=True, blank=True)

    # Referência (REVO360)
    reference_code = models.CharField(max_length=50, verbose_name='Código de Referência')

    # Endereço de instalação
    zip_code = models.CharField(max_length=10, verbose_name='CEP')
    address = models.CharField(max_length=255, verbose_name='Endereço')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=255, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=255, verbose_name='Cidade')
    state = models.CharField(max_length=2, verbose_name='UF')

    # Dados para simulação
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

    # Status
    status = models.CharField(max_length=100, default='Aguardando', verbose_name='Status')

    # Metadados
    usr_record = models.CharField(max_length=50, verbose_name='Usuário Registro')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_expired = models.DateTimeField(null=True, blank=True, verbose_name='Data Expiração')
    usr_update = models.CharField(max_length=50, null=True, blank=True, verbose_name='Usuário Atualização')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'ContractorProposal'
        verbose_name = 'Proposta (Contractor)'
        verbose_name_plural = 'Propostas (Contractor)'

    def __str__(self):
        return f"Proposta #{self.pk} para {self.prospect.lead_name}"
