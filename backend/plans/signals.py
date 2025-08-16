from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from plans.models.PlanAdesion import PlanAdesion
from core.models.Licensed import Licensed
from network.models import UnilevelNetwork
from network.models.LicensedPoints import LicensedPoints

# CHAMA O METODO QUE CRIA O LINK DE PAGAMENTO NA PAGARME E GRAVA NO BANCO NO 
# MOMENTO EM QUE É INSERIDO UM NOVO PLANO DE ADESÃO PARA AQUELE AFILIADO
@receiver(post_save, sender=PlanAdesion)
def generate_payment_link_on_create(sender, instance, created, **kwargs):
    """
    Dispara automaticamente a criação do PaymentLink ao criar PlanAdesion.
    """
    if created:
        payment_link, error = instance.create_payment_link()
        if error:
            print(f"❌ Erro ao gerar Payment Link: {error}")
        else:
            print(f"✅ Payment Link criado automaticamente: {payment_link.url}")


# Quando pagamento for confirmado (via admin ou webhook), garante inclusão na rede e pontuação
@receiver(post_save, sender=PlanAdesion)
def ensure_network_and_points_on_confirmation(sender, instance: PlanAdesion, created, **kwargs):
    # Só age quando status confirmado
    if instance.ind_payment_status != 'confirmed':
        return

    def process_after_commit():
        try:
            # Resolve Licensed a partir do User da adesão
            try:
                licensed = Licensed.objects.get(user=instance.licensed)
            except Licensed.DoesNotExist:
                print(f"❌ Licensed não encontrado para o usuário {instance.licensed}")
                return

            # Marca entrada na rede (flag e data de pagamento)
            updates = []
            if not licensed.is_in_network:
                licensed.is_in_network = True
                updates.append("is_in_network")
            if not licensed.dtt_payment_received:
                licensed.dtt_payment_received = instance.dtt_payment or timezone.now()
                updates.append("dtt_payment_received")
            if updates:
                licensed.save(update_fields=updates)

            # Conecta na Unilevel (idempotente via get_or_create)
            if licensed.original_indicator:
                upline = licensed.original_indicator
                lvl = 1
                current = upline
                while current and lvl <= 5:
                    UnilevelNetwork.objects.get_or_create(
                        upline_licensed=current,
                        downline_licensed=licensed,
                        level=lvl,
                    )
                    current = current.original_indicator
                    lvl += 1

            # Pontuação (idempotente)
            ref = f"ADES-{instance.id}"
            LicensedPoints.objects.get_or_create(
                licensed=licensed,
                reference=ref,
                defaults={
                    'description': f"Pontos de adesão do plano {instance.plan.name}",
                    'points': instance.plan.points,
                    'dtt_ref': timezone.now().date(),
                    'status': 'valid',
                }
            )

            # Sincroniza PaymentLink (se houver) para paid/captured
            try:
                from decimal import Decimal
                from finance.models.PaymentLink import PaymentLink
                pl = PaymentLink.objects.filter(adesion=instance).order_by('-created_at').first()
                if pl and pl.status != 'paid':
                    pl.status = 'paid'
                    pl.is_captured = True
                    if not pl.closed_at:
                        pl.closed_at = timezone.now()
                    pl.amount = Decimal(instance.plan.price)
                    if not pl.observation:
                        pl.observation = "Pagamento manual via edição de plano de adesão"
                    pl.save(update_fields=['status', 'is_captured', 'closed_at', 'amount', 'observation'])
            except Exception as e:
                print(f"Aviso: não foi possível sincronizar PaymentLink da adesão {instance.id}: {e}")
        except Exception as e:
            print(f"Erro em ensure_network_and_points_on_confirmation (post-commit): {e}")

    # executa somente após o commit da edição no admin
    transaction.on_commit(process_after_commit)