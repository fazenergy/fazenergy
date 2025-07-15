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



