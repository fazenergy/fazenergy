from django.db import models


class LicensedCompany(models.Model):
    """Cadastro de empresas (PJ) vinculadas a um `core.Licensed`.

    Um licenciado pode ter várias empresas (N:1). Cada empresa possui
    status de validação independente e documentos próprios (Cartão CNPJ e
    Contrato Social).
    """

    licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='companies',
        verbose_name='Licenciado',
    )

    cnpj = models.CharField(max_length=20, unique=True, verbose_name='CNPJ')
    razao_social = models.CharField(max_length=255, verbose_name='Razão Social')
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name='Nome Fantasia')

    insc_estadual = models.CharField(max_length=50, blank=True, null=True, verbose_name='Inscrição Estadual')
    insc_municipal = models.CharField(max_length=50, blank=True, null=True, verbose_name='Inscrição Municipal')

    cep = models.CharField(max_length=8, blank=True, null=True, verbose_name='CEP')
    city_lookup = models.ForeignKey('location.City', on_delete=models.SET_NULL, null=True, blank=True)
    endereco = models.CharField(max_length=300, blank=True, null=True, verbose_name='Endereço')
    numero = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=255, blank=True, null=True, verbose_name='Bairro')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')

    observacao = models.TextField(blank=True, null=True, verbose_name='Observação')

    stt_validate = models.CharField(
        max_length=10,
        choices=[('pending', 'Pendente'), ('rejected', 'Reprovado'), ('approved', 'Aprovado')],
        default='pending',
        verbose_name='Status de Validação',
    )
    rejection_reason = models.TextField(blank=True, null=True, verbose_name='Motivo da Reprovação')

    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'LicensedCompany'
        verbose_name = 'Empresa do Licenciado'
        verbose_name_plural = 'Empresas dos Licenciados'
        indexes = [
            models.Index(fields=['licensed']),
            models.Index(fields=['cnpj']),
            models.Index(fields=['stt_validate']),
        ]

    def __str__(self) -> str:
        return f"{self.cnpj} - {self.razao_social}"













