from django.db import models
from core.choices import DOCUMENT_TYPE_CHOICES, DOCUMENT_STATUS_CHOICES


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
        upload_to='licensed_documents/',
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


