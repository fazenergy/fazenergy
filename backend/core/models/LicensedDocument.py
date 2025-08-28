from django.db import models
from core.choices import DOCUMENT_TYPE_CHOICES, DOCUMENT_STATUS_CHOICES
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
    return os.path.join('licensed', cpf_digits, filename_sanitized)


class LicensedDocument(models.Model):
    licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Licenciado'
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
            models.UniqueConstraint(
                fields=['licensed', 'document_type'],
                name='uq_licensed_document_unique_type_per_licensed'
            )
        ]

    def __str__(self) -> str:
        return f"{self.licensed_id} - {self.document_type} ({self.stt_validate})"


