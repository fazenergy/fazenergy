# contracts/models.py
from django.db import models
from ckeditor.fields import RichTextField
from core.models import Affiliate

# registra as configurações da API da Lexio Legal
class ContractConfig(models.Model):
    lexio_url = models.URLField(default="https://app.lexio.legal/api/receive_document")
    lexio_token = models.CharField(max_length=255, verbose_name="Token de API")

    signer_company_name = models.CharField(max_length=255, verbose_name="Nome Parte Contratante")
    signer_company_email = models.EmailField(verbose_name="E-mail Parte Contratante")
    signer_company_function = models.CharField(max_length=255, default="Parte Contratante")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Configuração Lexio"
        verbose_name_plural = "Configurações Lexio"

    def __str__(self):
        return f"Lexio API ({self.lexio_url})"



class ContractTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nome do Contrato")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    body = RichTextField(verbose_name="Conteúdo do Contrato (HTML)")
    mapping_info = models.TextField(
        blank=True, null=True,
        verbose_name="Instruções de Mapeamento",
        help_text="Tabela de chaves disponíveis para usar no contrato."
    )
    active = models.BooleanField(default=True, verbose_name="Ativo?")

    class Meta:
        verbose_name = "Template de Contrato"
        verbose_name_plural = "Templates de Contrato"

    def __str__(self):
        return self.name
    
    # Define o mapeamento padrão se não for fornecido
    def save(self, *args, **kwargs):
        if not self.mapping_info:
            self.mapping_info = """
                {{ affiliate.id }}: ID do afiliado
                {{ affiliate.nome }}: Nome do afiliado
                {{ affiliate.cpf_cnpj }}: CPF/CNPJ
                {{ affiliate.phone }}: Telefone
                {{ affiliate.address }}: Endereço
                {{ user.username }}: Nome de usuário
                {{ user.email }}: E-mail do usuário
                {{ site_url }}: URL do site
                """
        super().save(*args, **kwargs)

# auditoria de contrato assinado
class ContractLog(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    contract_template = models.ForeignKey(ContractTemplate, on_delete=models.CASCADE)
    document_token = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    response = models.JSONField(blank=True, null=True)  # opcional: salva resposta completa
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.affiliate} - {self.contract_template} - {self.status}"
