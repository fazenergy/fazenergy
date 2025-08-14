# contracts/models.py
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from core.models.Licensed import Licensed

# registra as configurações da API da Lexio Legal
class ContractConfig(models.Model):
    lexio_url = models.URLField(default="https://app.lexio.legal/api/receive_document")
    lexio_token = models.CharField(max_length=255, verbose_name="Token de API")

    # Parte da Empresa que assina o contrato
    signer_name_partner = models.CharField(max_length=255, verbose_name="Parte da Empresa") # Parte da empresa que assina o contrato
    signer_mail_partner = models.EmailField(verbose_name="E-mail Parte Empresa")

    # Testemunha parte empresa que assina o contrato
    signer_name_testmon = models.CharField(max_length=255, verbose_name="Testemunha") 
    signer_mail_testmon = models.EmailField(verbose_name="E-mail Testemunha")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ContractConfig'
        verbose_name = "Configuração Lexio"
        verbose_name_plural = "Configurações Lexio"

    def __str__(self):
        return f"Lexio API ({self.lexio_url})"



class ContractTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nome do Contrato")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    body = CKEditor5Field(config_name='contract', verbose_name="Conteúdo do Contrato (HTML)")
    mapping_info = models.TextField(
        blank=True, null=True,
        verbose_name="Instruções de Mapeamento",
        help_text="Tabela de chaves disponíveis para usar no contrato."
    )
    active = models.BooleanField(default=True, verbose_name="Ativo?")

    class Meta:
        db_table = 'ContractTemplate'
        verbose_name = "Template de Contrato"
        verbose_name_plural = "Templates de Contrato"

    def __str__(self):
        return self.name
    
    # Define o mapeamento padrão se não for fornecido
    def save(self, *args, **kwargs):
        if not self.mapping_info:
            self.mapping_info = """
            {{ licensed.original_indicator }}: ID do Indicador Original
            {{ licensed.id }}: ID do licenciado
            {{ licensed.nome }}: Nome do licenciado
            {{ licensed.person_type }}: Tipo de Pessoa PF ou PJ
            {{ licensed.cpf_cnpj }}: CPF/CNPJ
            {{ user.username }}: Nome de usuário
            {{ user.email }}: E-mail do usuário
            {{ site_url }}: URL do site
            {{ licensed.phone }}: Telefone
            {{ licensed.cep }}: CEP
            {{ licensed.address }}: Endereço
            {{ licensed.number }}: Número do Endereço
            {{ licensed.complement }}: Complemento do Endereço
            {{ licensed.district }}: Bairro
            {{ licensed.city_name }}: Cidade
            {{ licensed.state_abbr }}: UF
            {{ licensed.plan.name }}: Nome do Plano de Adesão
            {{ licensed.plan.price }}: Preço do Plano de Adesão
            {{ licensed.full_name }}: Nome completo do licenciado
            {{ licensed.dtt_record }}: Data de cadastro do licenciado
            {{ licensed.dtt_payment_received }}: Data de recebimento do pagamento
                """ 
        super().save(*args, **kwargs)

# auditoria de contrato assinado
class ContractLog(models.Model):
    licensed = models.ForeignKey(Licensed, on_delete=models.CASCADE, null=True)
    contract_template = models.ForeignKey(ContractTemplate, on_delete=models.CASCADE, null=True)
    document_token = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=50, null=True)
    response = models.JSONField(blank=True, null=True)  # opcional: salva resposta completa
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ContractLog'
        verbose_name = "Log de Contrato"
        verbose_name_plural = "Log de Contrato"

    def __str__(self):
        return f"{self.licensed} - {self.contract_template} - {self.status}"
