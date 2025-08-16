from django.db import models


class Prospect(models.Model):
    # Relações principais (logo após a PK)
    product = models.ForeignKey(
        'network.Product', on_delete=models.PROTECT,
        related_name='prospects', verbose_name='Produto'
    )
    licensed = models.ForeignKey(
        'core.Licensed', on_delete=models.PROTECT,
        related_name='prospects', verbose_name='Licenciado (Indicador)'
    )

    # Identidade e contato
    lead_name = models.CharField(max_length=255, verbose_name='Nome do Lead')
    email = models.EmailField(verbose_name='E-mail')
    cellphone = models.CharField(max_length=20, verbose_name='Celular')

    # Endereço / imóvel
    zip_code = models.CharField(max_length=10, verbose_name='CEP')
    property_type = models.CharField(max_length=50, verbose_name='Tipo de Imóvel')

    # Conta / consumo
    electric_bill = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Conta de Luz (R$)')

    # Integração
    reference_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='Código de Referência')
    energy_provider_id = models.IntegerField(null=True, blank=True, verbose_name='Distribuidora (ID)')
    energy_provider_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Distribuidora (Nome)')
    owner_name = models.CharField(max_length=100, default='Outro', verbose_name='Proprietário')

    # Datas de visita técnica
    visit_1_at = models.DateTimeField(null=True, blank=True, verbose_name='Data da 1ª Visita')
    visit_2_at = models.DateTimeField(null=True, blank=True, verbose_name='Data da 2ª Visita')

    # Status
    status = models.CharField(max_length=100, default='Novo', verbose_name='Status')

    # Pessoa / documento
    person_type = models.CharField(
        max_length=2,
        choices=[('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')],
        default='PF',
        verbose_name='Tipo de Pessoa'
    )
    fiscal_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='CPF/CNPJ (sem máscara)')
    legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Razão Social (se PJ)')

    # Metadados obrigatórios
    usr_record = models.CharField(max_length=50, verbose_name='Usuário Registro')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    usr_update = models.CharField(max_length=50, null=True, blank=True, verbose_name='Usuário Atualização')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'Prospect'
        verbose_name = 'Prospect'
        verbose_name_plural = 'Prospects'
        ordering = ['-dtt_record']
        indexes = [
            models.Index(fields=['reference_code']),
            models.Index(fields=['status']),
            models.Index(fields=['person_type']),
        ]

    def __str__(self):
        return f"{self.lead_name} <{self.email}>"
