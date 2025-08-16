# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from plans.models import PlanAdesion
from .models import VirtualAccount, Transaction
from core.models.Licensed import Licensed
from django.utils import timezone


# Sempre que um novo licenciado for criado, cria uma conta virtual associada ao licenciado com o nome do usuário do licenciado.
@receiver(post_save, sender=Licensed)
def create_virtual_account(sender, instance, created, **kwargs):
    if created:
        VirtualAccount.objects.create(
            licensed=instance,
            name_licensed=instance.user.username
        )

# Sempre que um PlanAdesion for salvo, se o pagamento for confirmado e não processado,
# cria uma transação de bônus na conta virtual do afiliado. 
@receiver(post_save, sender=PlanAdesion)
def create_transaction_on_plan_payment(sender, instance, created, **kwargs):
    """Após confirmar pagamento, cria a transação e atualiza saldos somente após o commit."""
    if instance.ind_payment_status != 'confirmed' or instance.points_generated:
        return

    def process_after_commit():
        from core.models.Licensed import Licensed
        try:
            licensed = Licensed.objects.get(user=instance.licensed)
        except Licensed.DoesNotExist:
            print(f"❌ Licensed não encontrado para o usuário {instance.licensed}")
            return

        va, _ = VirtualAccount.objects.get_or_create(licensed=licensed, defaults={
            'name_licensed': licensed.user.username,
        })

        tx = Transaction.objects.create(
            virtual_account=va,
            product=f"Plano Adesão MMN: {instance.plan.id}",
            description=f"Bônus de Indicação: ID {licensed.id}",
            status='blocked',
            operation='credit',
            amount=instance.plan.bonus_level_1,
            is_processed=True,
            reference_date=timezone.now().date(),
        )

        va.balance_blocked += tx.amount
        va.save(update_fields=["balance_blocked"])

        # Evita loop de signals: atualiza flag sem disparar novas operações pesadas
        PlanAdesion.objects.filter(pk=instance.pk, points_generated=False).update(points_generated=True)

    transaction.on_commit(process_after_commit)



##############################################
from finance.models import PaymentLink

@receiver(post_save, sender=PaymentLink)
def post_save_payment_link(sender, instance: PaymentLink, created, **kwargs):
    """Executa aprovação/cancelamento do PaymentLink após commit para evitar transação quebrada."""
    if created:
        return

    def process_after_commit():
        if not instance.is_captured and not instance.is_canceled and instance.status in ("paid", "authorized"):
            try:
                instance.approve_payment()
            except Exception as e:
                print(f"Erro ao aprovar PaymentLink {instance.pk}: {e}")
            return

        if instance.status == "canceled" and not instance.is_canceled:
            instance.is_canceled = True
            if not instance.canceled_at:
                instance.canceled_at = timezone.now()
            instance.save(update_fields=["is_canceled", "canceled_at"]) 

    transaction.on_commit(process_after_commit)
