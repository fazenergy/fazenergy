from django.db import models
from django.conf import settings  # Para pegar o User do projeto

# Planos de Carreira
# #################################################################################################
class PlanCareer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Id")
    stage_name = models.CharField( max_length=100, verbose_name="Estágio") 
    reward_description = models.CharField( max_length=255, verbose_name="Prêmio")
    required_points = models.PositiveIntegerField(verbose_name="Pontos Necessários")
    required_directs = models.PositiveSmallIntegerField(verbose_name="Qtd de Diretos")
    required_direct_sales = models.PositiveSmallIntegerField(verbose_name="Vendas Diretas")
    max_pml_per_line = models.PositiveIntegerField(verbose_name="Pontos Máx por Linha (PML)")

    cover_image = models.ImageField(
        upload_to='plan_careers/',
        blank=True, null=True,
        verbose_name="Imagem de Capa"
    )

    usr_record = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plan_careers_created', on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name="User Record")
    usr_update = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plan_careers_updated', on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name="User Update")
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name="Data Criação")
    dtt_update = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")
    stt_record = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = 'PlanCareers'
        verbose_name = "Plano de Carreira"
        verbose_name_plural = "Planos de Carreira"

    def __str__(self):
        return f"{self.stage_name} ({self.required_points} pts)" 
    
    def data_criacao_formatada(self):
        """Retorna a data de criação no formato dd/mm/yyyy hh:mm:ss"""
        if self.dtt_record:
            return self.dtt_record.strftime("%d/%m/%Y %H:%M:%S")
        return "-"
    data_criacao_formatada.short_description = "Data Criação"
    
    def data_atualizacao_formatada(self):
        """Retorna a data de atualização no formato dd/mm/yyyy hh:mm:ss"""
        if self.dtt_update:
            return self.dtt_update.strftime("%d/%m/%Y %H:%M:%S")
        return "-"
    data_atualizacao_formatada.short_description = "Data Atualização" 