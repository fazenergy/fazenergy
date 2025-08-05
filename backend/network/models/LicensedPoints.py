from django.db import models
from django.conf import settings
from django.utils import timezone

# ###########################################################################################################
# Registro de Pontuação de cada Afiliado na Rede
# ###########################################################################################################    
class LicensedPoints(models.Model):
    """
    Registro de Pontuação de cada Afiliado na Rede
    """
    licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='points',
        verbose_name="Licenciado",
        null=True, blank=True
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
        db_table = 'LicensedPoints'
        verbose_name = "Pontuação"
        verbose_name_plural = "Pontuações"
        indexes = [
            models.Index(fields=['licensed']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.licensed} - {self.points} pts ({self.status})"
    
    def data_referencia_formatada(self):
        """Retorna a data de referência no formato dd/mm/yyyy"""
        if self.dtt_ref:
            return self.dtt_ref.strftime("%d/%m/%Y")
        return "-"
    data_referencia_formatada.short_description = "Data Referência"
    
    def data_registro_formatada(self):
        """Retorna a data de registro no formato dd/mm/yyyy hh:mm:ss"""
        if self.dtt_record:
            return self.dtt_record.strftime("%d/%m/%Y %H:%M:%S")
        return "-"
    data_registro_formatada.short_description = "Data Criação"



