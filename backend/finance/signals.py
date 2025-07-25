# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from plans.models import PlanAdesion
from .models import VirtualAccount, VirtualAccountTransaction
from backend.core.models.user_manager import Affiliate
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



##############################################
from finance.models import PaymentLink

@receiver(post_save, sender=PaymentLink)
def post_save_payment_link(instance, created, **kwargs):
    """
    Signal para capturar ou cancelar pagamento na nova estrutura.
    """
    if created:
        return

    # Se ainda não capturado e pago
    if not instance.is_captured and not instance.is_canceled:
        if instance.status == "paid":
            # Atualiza o Affiliate
            affiliate = instance.affiliate
            affiliate.active = True
            affiliate.activated_at = timezone.now()
            affiliate.save(update_fields=["active", "activated_at"])

            # Atualiza o Product (opcional)
            product = instance.product
            product.status = 'paid'
            product.paid_at = timezone.now()
            product.save(update_fields=["status", "paid_at"])

            # Marca PaymentLink como capturado
            instance.is_captured = True
            instance.closed_at = timezone.now()
            instance.save(update_fields=["is_captured", "closed_at"])

    # Se precisar cancelar (exemplo)
    if instance.is_captured and not instance.is_canceled:
        if instance.status == "paid" and instance.cancel_response and instance.canceled_at:
            affiliate = instance.affiliate
            affiliate.active = False
            affiliate.save(update_fields=["active"])

            product = instance.product
            product.status = 'canceled'
            product.save(update_fields=["status"])

            instance.is_canceled = True
            instance.save(update_fields=["is_canceled"])
