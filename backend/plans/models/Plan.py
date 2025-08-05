from django.db import models
from django.conf import settings  # Para pegar o User do projeto
#from finance.models.gateway_link_service import create_payment_link


# Configuração de Planos de Adesão ( podemos dizer que é uma tabela mestre )
# #################################################################################################
class Plan(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome do Plano")
    image = models.ImageField(upload_to='plans/', blank=True, null=True, verbose_name="Capa")  # 400x400 px
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    points = models.PositiveIntegerField(verbose_name="Pontos")
    bonus_level_1 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bônus Nível 1")
    bonus_level_2 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bônus Nível 2")
    bonus_level_3 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bônus Nível 3")
    bonus_level_4 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bônus Nível 4")
    bonus_level_5 = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bônus Nível 5")
    stt_record = models.BooleanField(default=True, verbose_name="Ativo?")
    
    usr_record = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plans_created', on_delete=models.SET_NULL, 
                                   null=True, blank=True, verbose_name="User Record")
    usr_update = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plans_updated', on_delete=models.SET_NULL, 
                                   null=True, blank=True, verbose_name="User Update")
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name="Data Criação")
    dtt_update = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")

    contract_template = models.ForeignKey(
        'contracts.ContractTemplate',  # como string: 'app_name.ModelName'
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template de Contrato"
    )


    class Meta:
        db_table = 'Plan'
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return self.name