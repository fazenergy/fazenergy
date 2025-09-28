from django.db import models
from core.choices import DOCUMENT_TYPE_CHOICES, DOCUMENT_STATUS_CHOICES, DOCUMENT_OWNER_TYPE_CHOICES
import os
import re
import uuid


def licensed_document_upload_to(instance, filename):
    # Extensão preservada
    _, ext = os.path.splitext(filename)
    ext = ext or '.bin'

    # Pasta por CPF/CNPJ (apenas dígitos)
    cpf_cnpj = getattr(getattr(instance, 'licensed', None), 'cpf_cnpj', '') or ''
    cpf_digits = re.sub(r'\D', '', str(cpf_cnpj)) or 'unknown'

    # Prefixo pelo tipo do documento
    doc_type = (getattr(instance, 'document_type', 'document') or 'document').lower()
    doc_type = re.sub(r'[^a-z0-9_-]', '', doc_type)

    # Chave curta para evitar colisões
    key = uuid.uuid4().hex[:12]

    filename_sanitized = f"{doc_type}_{key}{ext}"
    base = ['licensed', cpf_digits]
    try:
        if getattr(instance, 'owner_type', 'pf') == 'pj' and getattr(instance, 'company_id', None):
            cnpj = getattr(getattr(instance, 'company', None), 'cnpj', '') or ''
            cnpj_digits = re.sub(r'\D', '', str(cnpj)) or 'company'
            base.extend(['company', cnpj_digits])
    except Exception:
        pass
    return os.path.join(*base, filename_sanitized)


class LicensedDocument(models.Model):
    licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Licenciado'
    )

    # Quando documento for de empresa (PJ), referenciar a empresa específica
    owner_type = models.CharField(
        max_length=2,
        choices=DOCUMENT_OWNER_TYPE_CHOICES,
        default='pf',
        verbose_name='Tipo do Dono do Documento (PF/PJ)'
    )
    company = models.ForeignKey(
        'core.LicensedCompany',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='documents',
        verbose_name='Empresa (quando PJ)'
    )

    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Tipo de Documento'
    )

    file = models.FileField(
        upload_to=licensed_document_upload_to,
        verbose_name='Arquivo do Documento'
    )

    observation = models.TextField(blank=True, null=True, verbose_name='Observação')

    stt_validate = models.CharField(
        max_length=10,
        choices=DOCUMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Status de Validação'
    )

    rejection_reason = models.TextField(blank=True, null=True, verbose_name='Motivo da Reprovação')

    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'LicensedDocument'
        verbose_name = 'Documento do Licenciado'
        verbose_name_plural = 'Documentos dos Licenciados'
        constraints = [
            # Unicidade por tipo para PF (sem company)
            models.UniqueConstraint(
                fields=['licensed', 'owner_type', 'document_type'],
                condition=models.Q(owner_type='pf'),
                name='uq_doc_unique_type_per_licensed_pf'
            ),
            # Unicidade por tipo para PJ (por empresa)
            models.UniqueConstraint(
                fields=['company', 'document_type'],
                condition=models.Q(owner_type='pj'),
                name='uq_doc_unique_type_per_company_pj'
            ),
        ]

    def __str__(self) -> str:
        return f"{self.licensed_id} - {self.document_type} ({self.stt_validate})"


