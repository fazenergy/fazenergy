# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from plans.models import PlanAdesion
from .models import VirtualAccount, VirtualAccountTransaction
from core.models import Affiliate
from django.utils import timezone


# Sempre que um novo afiliado for criado, cria uma conta virtual associada ao afiliado com o nome do usuário do afiliado.
@receiver(post_save, sender=Affiliate)
def create_virtual_account(sender, instance, created, **kwargs):
    if created:
        VirtualAccount.objects.create(
            affiliate=instance,
            name_affiliate=instance.user.username
        )

# Sempre que um PlanAdesion for salvo, se o pagamento for confirmado e não processado,
# cria uma transação de bônus na conta virtual do afiliado. 
@receiver(post_save, sender=PlanAdesion)
def create_transaction_on_plan_payment(sender, instance, created, **kwargs):
    """
    Quando um PlanAdesion for salvo, se o pagamento for confirmado e não processado,
    cria a transação de bônus na conta virtual.
    """
    if instance.ind_payment_status == 'confirmed' and not instance.points_generated:
        # Pega o afiliado
        affiliate = instance.affiliate
        virtual_account, _ = VirtualAccount.objects.get_or_create(affiliate=affiliate)

        # Cria transação
        transaction = VirtualAccountTransaction.objects.create(
            virtual_account=virtual_account,
            product=f"Plano Adesão MMN: {instance.plan.id}",
            description=f"Bônus de Indicação: ID {affiliate.id}",
            status='blocked',
            operation='credit',
            amount=instance.plan.bonus_level_1,
            is_processed=True,
            reference_date=timezone.now().date()
        )

        # Atualiza saldos
        virtual_account.blocked_balance += transaction.amount
        virtual_account.save()

        # Marca como processado
        instance.points_generated = True
        instance.save()

