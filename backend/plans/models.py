# plans/models.py
from django.db import models
from django.conf import settings  # Para pegar o User do projeto


# Planos de Adesão
# #################################################################################################
class Plan(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='plans/', blank=True, null=True)  # 400x400 px
    price = models.DecimalField(max_digits=10, decimal_places=2)
    points = models.PositiveIntegerField()
    bonus_level_1 = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_level_2 = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_level_3 = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_level_4 = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_level_5 = models.DecimalField(max_digits=10, decimal_places=2)
    stt_record = models.BooleanField(default=True)
    
    usr_record = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plans_created', on_delete=models.SET_NULL, null=True, blank=True)
    usr_update = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='plans_updated', on_delete=models.SET_NULL, null=True, blank=True)
    dtt_record = models.DateTimeField(auto_now_add=True)
    dtt_update = models.DateTimeField(auto_now=True)

    contract_template = models.ForeignKey(
        'contracts.ContractTemplate',  # como string: 'app_name.ModelName'
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template de Contrato"
    )


    class Meta:
        db_table = 'tb_Plan'
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return self.name

# Dic Choices de Plano de Adesão 
# #################################################################################################
class PlanAdesion(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('pix', 'Pix'),
        ('money', 'Dinheiro'),
        ('creditCard', 'Cartão de Crédito'),
        ('debitCard', 'Cartão de Débito'),
    ]

    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('success', 'Sucesso'),
        ('canceled', 'Cancelado'),
    ]

    BONUS_STATUS_CHOICES = [
        ('notApply', 'Não Aplicável'),
        ('pendingPayment', 'Pagamento Pendente'),
        ('bonusApplied', 'Bônus Aplicado'),
        ('cancelBonus', 'Cancelar Bônus'),
        ('bonusCanceled', 'Bônus Cancelado'),
    ]

    plan = models.ForeignKey('plans.Plan', on_delete=models.PROTECT, related_name='adesions')
    affiliate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='adesions')

    ind_payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    typ_payment = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, blank=True, null=True)

    dtt_record = models.DateTimeField(auto_now_add=True)
    dtt_payment = models.DateTimeField(blank=True, null=True)
    dtt_cancel = models.DateTimeField(blank=True, null=True)
    dtt_update = models.DateTimeField(auto_now=True)

    is_courtesy = models.BooleanField(default=False)
    points_generated = models.BooleanField(default=False)

    ind_processing = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending')
    ind_bonus_status = models.CharField(max_length=20, choices=BONUS_STATUS_CHOICES, default='notApply')

    des_cancel_reason = models.CharField(max_length=500, blank=True, null=True)
    contract_status = models.CharField(max_length=50, blank=True, null=True)
    contract_token = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'tb_PlanAdesion'
        verbose_name = "Plano de Adesão"
        verbose_name_plural = "Planos de Adesão"


    def __str__(self):
        return f"Adesão {self.id} - {self.affiliate} - {self.plan.name}"
    
# Planos de Carreira
# #################################################################################################
class PlanCareer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    stage_name = models.CharField( max_length=100, verbose_name="Estágio") 
    reward_description = models.CharField( max_length=255, verbose_name="Prêmio")
    required_points = models.PositiveIntegerField(verbose_name="Pontos Necessários")
    required_directs = models.PositiveSmallIntegerField(verbose_name="Quantidade de Diretos")
    required_direct_sales = models.PositiveSmallIntegerField(verbose_name="Vendas Diretas")
    max_pml_per_line = models.PositiveIntegerField(verbose_name="Pontos Máximos por Linha (PML)")



    cover_image = models.ImageField(
        upload_to='plan_careers/',
        blank=True, null=True,
        verbose_name="Imagem de Capa"
    )

    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name="Data Criação")
    dtt_update = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")
    stt_record = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = 'tb_PlanCareers'
        verbose_name = "Plano de Carreira"
        verbose_name_plural = "Planos de Carreira"

    def __str__(self):
        return f"{self.stage_name} ({self.required_points} pts)" 