import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ScoreReference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    points_amount = models.PositiveIntegerField("Pontos")

    receiver_licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='received_scores',
        verbose_name='Licenciado Recebedor',
    )
    triggering_licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='triggered_scores',
        verbose_name='Licenciado Causador da Ação',
    )

    # Relação genérica para origem (Proposal ou PlanAdesion)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(app_label='prospect', model='proposal') | models.Q(app_label='plans', model='planadesion'),
        verbose_name='Tipo de Origem',
    )
    object_id = models.BigIntegerField('ID do Objeto de Origem')
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ScoreReference'
        verbose_name = 'Referência de Pontuação'
        verbose_name_plural = 'Referências de Pontuação'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver_licensed']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self) -> str:
        return f"{self.points_amount} pts → {self.receiver_licensed}"
