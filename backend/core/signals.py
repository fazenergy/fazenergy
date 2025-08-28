from core.tasks import verificar_plano_de_carreira_task

# Quando licenciado efetua compra:
#verificar_plano_de_carreira_task.delay(licensed.id)

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models.Licensed import Licensed  # ajuste para seu import real
from core.models.LicensedDocument import LicensedDocument
from notifications.utils import send_email
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
                upline_licensed=instance.original_indicator,
                downline_licensed=instance,
                level=1
            )
            # 2 - Liga uplines até nível 5
            parent = instance.original_indicator
            level = 2
            while parent.original_indicator and level <= 5:
                UnilevelNetwork.objects.create(
                    upline_licensed=parent.original_indicator,
                    downline_licensed=instance,
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


# ------------------------------------------------------------------------------------
# Recalcular status geral de documentação do Licensed quando documentos mudarem
# Regra:
# - pending se qualquer documento estiver pendente ou se faltar algum tipo exigido
# - rejected se algum estiver reprovado e nenhum pendente
# - approved somente se todos os tipos exigidos existirem e estiverem aprovados
# ------------------------------------------------------------------------------------
REQUIRED_DOC_TYPES = { 'cpf', 'rg', 'comprovante_endereco', 'pis' }

def _recalculate_licensed_document_status(licensed: Licensed):
    docs = list(LicensedDocument.objects.filter(licensed=licensed))
    existing_types = {d.document_type for d in docs}

    # Faltando algum obrigatório => pendente
    complete_set = REQUIRED_DOC_TYPES.issubset(existing_types)
    if not complete_set:
        new_status = 'pending'
    else:
        statuses = {d.stt_validate for d in docs if d.document_type in REQUIRED_DOC_TYPES}
        if 'pending' in statuses:
            new_status = 'pending'
        elif 'rejected' in statuses:
            new_status = 'rejected'
        else:
            new_status = 'approved'

    status_changed = (licensed.stt_document != new_status)
    if status_changed:
        licensed.stt_document = new_status
        licensed.save(update_fields=['stt_document'])

    # Notificar operadores quando conjunto completo está aguardando validação
    if complete_set and new_status == 'pending':
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            operators = User.objects.filter(groups__name='Operador').values_list('email', flat=True)
            recipients = [e for e in operators if e]
            if recipients:
                send_email(
                    'LicensedDocsSubmitted',
                    {
                        'nome': licensed.user.get_full_name() or licensed.user.username,
                        'username': licensed.user.username,
                    },
                    recipients
                )
        except Exception:
            pass


@receiver(post_save, sender=LicensedDocument)
def on_document_saved(sender, instance: LicensedDocument, created, **kwargs):
    # Sempre que documento é salvo, volta Licensed para pendente se houve edição
    lic = instance.licensed
    # Caso operador altere status manualmente, recalcular pelo conjunto
    _recalculate_licensed_document_status(lic)


@receiver(post_delete, sender=LicensedDocument)
def on_document_deleted(sender, instance: LicensedDocument, **kwargs):
    _recalculate_licensed_document_status(instance.licensed)