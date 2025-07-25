from django.db import models
from django.conf import settings
from django.utils import timezone

# ###########################################################################################################
# Registro de Pontuação de cada Afiliado na Rede
# ###########################################################################################################    
class AffiliatePoints(models.Model):
    """
    Registro de Pontuação de cada Afiliado na Rede
    """
    affiliate = models.ForeignKey(
        'core.Affiliate',
        on_delete=models.CASCADE,
        related_name='points',
        verbose_name="Afiliado"
    )
    description = models.CharField(
        max_length=255,
        verbose_name="Descrição"
    )
    points = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Pontos"
    )
    reference = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name="Referência"
    )
    dtt_ref = models.DateField(verbose_name="Data Referência")
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name="Data Registro")
    status = models.CharField(
        max_length=20,
        choices=[('valid', 'Válido'), ('pending', 'Pendente'), ('canceled', 'Cancelado')],
        default='valid',
        verbose_name="Status"
    )

    class Meta:
        db_table = 'tb_AffiliatePoints'
        verbose_name = "Pontuação do Afiliado"
        verbose_name_plural = "Pontuações dos Afiliados"
        indexes = [
            models.Index(fields=['affiliate']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.affiliate} - {self.points} pts ({self.status})"  



