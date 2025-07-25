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
    parent_affiliate = models.ForeignKey(
        'core.Affiliate',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Afiliado Pai"
    )
    child_affiliate = models.ForeignKey(
        'core.Affiliate',
        on_delete=models.CASCADE,
        related_name='parents',
        verbose_name="Afiliado Filho"
    )
    level = models.PositiveSmallIntegerField(
        verbose_name="Nível na Rede"
    )
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name="Data Registro")
    dtt_update = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")

    class Meta:
        db_table = 'tb_UnilevelNetwork'
        verbose_name = "Rede Unilevel"
        verbose_name_plural = "Rede Unilevel"
        indexes = [
            models.Index(fields=['parent_affiliate']),
            models.Index(fields=['child_affiliate']),
        ]

    def __str__(self):
        return f"{self.parent_affiliate} => {self.child_affiliate} (Nível {self.level})"
    
    
