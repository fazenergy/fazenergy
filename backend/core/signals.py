from core.tasks import verificar_plano_de_carreira_task

# Quando licenciado efetua compra:
#verificar_plano_de_carreira_task.delay(licensed.id)

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models.Licensed import Licensed  # ajuste para seu import real
from plans.models import PlanAdesion  
from network.models import UnilevelNetwork
from contracts.services import send_doc_adesion_to_lexio


# CRIA UM PLANO DE ADESAO PARA ESSE NOVO LICENCIADO
@receiver(post_save, sender=Licensed)
def create_plan_adesion_for_licensed(sender, instance, created, **kwargs):
    """
    Toda vez que um Licensed for criado, cria automaticamente um registro PlanAdesion relacionado.
    """
    if created:
        # 1 - Verifica se já existe uma adesão para este licenciado
        # -----------------------------
        adesion_exists = PlanAdesion.objects.filter(licensed=instance.user).exists()
        if not adesion_exists:
            PlanAdesion.objects.create(
                licensed=instance.user,  # Note: aqui é o User, pois seu FK aponta para o AUTH_USER_MODEL
                plan=instance.plan,       # Pega o plano vinculado no Licensed
                ind_payment_status='pending',  # ou o valor default que preferir
                ind_processing='pending',
                ind_bonus_status='notApply',
            )
        
        # 2 - Cria rede Unilevel
        if instance.original_indicator:
            # 1 - Liga nível 1
            UnilevelNetwork.objects.create(
                parent_licensed=instance.original_indicator,
                child_licensed=instance,
                level=1
            )
            # 2 - Liga uplines até nível 5
            parent = instance.original_indicator
            level = 2
            while parent.original_indicator and level <= 5:
                UnilevelNetwork.objects.create(
                    parent_licensed=parent.original_indicator,
                    child_licensed=instance,
                    level=level
                )
                parent = parent.original_indicator
                level += 1
        else:
            # Se não tiver indicador, é raiz na rede
            pass

# CHAMA O METODO DA API PARA LEXO LEGAL ENVIAR O CONTRATO
@receiver(post_save, sender=Licensed)
def send_contract_api_lexo(sender, instance, created, **kwargs):
    if created:
        try:
            resultado = send_doc_adesion_to_lexio(instance.pk)
            print("Enviado para Lexio:", resultado)
        except Exception as e:
            print(f"Erro ao enviar contrato Lexio: {e}")