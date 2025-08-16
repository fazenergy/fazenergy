from django.db import models


class Qualification(models.Model):
    licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='qualifications',
        verbose_name='Licenciado'
    )
    plan_career = models.ForeignKey(
        'plans.PlanCareer',
        on_delete=models.CASCADE,
        related_name='qualifications',
        verbose_name='Plano de Carreira'
    )
    dtt_qualification = models.DateTimeField(auto_now_add=True, verbose_name='Data Qualificação')

    class Meta:
        db_table = 'Qualification'
        verbose_name = 'Qualificação'
        verbose_name_plural = 'Qualificações'
        constraints = [
            models.UniqueConstraint(fields=['licensed', 'plan_career'], name='uq_qualification_licensed_career'),
        ]
        indexes = [
            models.Index(fields=['licensed']),
            models.Index(fields=['plan_career']),
        ]

    def __str__(self) -> str:
        return f"{self.licensed} -> {self.plan_career} em {self.dtt_qualification:%d/%m/%Y %H:%M}"
