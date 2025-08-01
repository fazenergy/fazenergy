from django.db import models
from django.conf import settings
from django.utils import timezone

# Essa tabela é usada para gerenciar a rede unilevel de afiliados.
# Cada afiliado pode ter vários afiliados filhos, formando uma estrutura em árvore.
# ###########################################################################################################
class UnilevelNetwork(models.Model):
    """
    Estrutura UNILEVEL: quem indicou quem, em qual nível
    """
    upline_licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Licenciado Pai"
    )
    downline_licensed = models.ForeignKey(
        'core.Licensed',
        on_delete=models.CASCADE,
        related_name='parents',
        verbose_name="Licenciado Filho"
    )
    level = models.PositiveSmallIntegerField(
        verbose_name="Nível na Rede"
    )
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name="Data Registro")
    dtt_update = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")

    class Meta:
        db_table = 'UnilevelNetwork'
        verbose_name = "Rede Unilevel"
        verbose_name_plural = "Rede Unilevel"
        indexes = [
            models.Index(fields=['upline_licensed']),
            models.Index(fields=['downline_licensed']),
        ]

    def __str__(self):
        return f"{self.upline_licensed} => {self.downline_licensed} (Nível {self.level})"

    
