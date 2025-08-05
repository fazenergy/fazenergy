from django.db import models
from django.conf import settings  # Para pegar o User do projeto

# Planos de Adesão Cadastros
# #################################################################################################
class PlanAdesion(models.Model):

    # Dicionário: Choices de Plano de Adesão 
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

    plan = models.ForeignKey('plans.Plan', on_delete=models.PROTECT, related_name='adesions', verbose_name="Plano de Adesão")
    licensed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='adesions', verbose_name="Licenciado")

    ind_payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Stt Pagamento")
    typ_payment = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, blank=True, null=True, verbose_name="Tipo")

    dtt_record = models.DateTimeField(auto_now_add=True)
    dtt_payment = models.DateTimeField(blank=True, null=True)
    dtt_cancel = models.DateTimeField(blank=True, null=True)
    dtt_update = models.DateTimeField(auto_now=True)

    is_courtesy = models.BooleanField(default=False, verbose_name="Cortesia?")
    points_generated = models.BooleanField(default=False, verbose_name="Pontos")

    ind_processing = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending', verbose_name="Stt Process")
    ind_bonus_status = models.CharField(max_length=20, choices=BONUS_STATUS_CHOICES, default='notApply', verbose_name="Stt Bônus")

    des_cancel_reason = models.CharField(max_length=500, blank=True, null=True, verbose_name="Motivo Cancelamento")
    contract_status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Status Contrato")
    contract_token = models.CharField(max_length=500, blank=True, null=True, verbose_name="Token Contrato")

    class Meta:
        db_table = 'PlanAdesion'
        verbose_name = "Plano de Adesão"
        verbose_name_plural = "Planos de Adesão"


    def __str__(self):
        return f"Adesão {self.id} - {self.licensed} - {self.plan.name}"

    # chama o metodo que cria o link de pagamento
    def create_payment_link(self):
        # Verifica se o licenciado é um usuário "raiz"
        if getattr(self.licensed, 'is_root', False):
            print("✅ Licenciado raiz — não será criado link de pagamento.")
            return None, None

        from finance.services.CreatePaymentLink import create_payment_link  # lazy import!
        return create_payment_link(self)
