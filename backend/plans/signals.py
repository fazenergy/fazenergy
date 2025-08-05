from django.db.models.signals import post_save
from django.dispatch import receiver
from plans.models.PlanAdesion import PlanAdesion

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