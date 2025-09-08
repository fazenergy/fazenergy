from django.utils import timezone


def ensure_licensed_activation(licensed) -> bool:
    """
    Garante o status de ativação do Licensed com base nos critérios de negócio.

    Regra de negócio (idempotente):
    - Ativo quando: pagamento de adesão confirmado E documentação aprovada.
    - Caso contrário: Inativo.

    Efeitos colaterais controlados:
    - Preenche `dtt_activation` quando tornamos ativo e o campo ainda não estava setado.
    - Só persiste ao banco quando há mudança no valor de `stt_record` ou `dtt_activation`.

    Retorna True se houve alteração persistida, False caso contrário.
    """
    try:
        # 1) Documentos aprovados?
        docs_ok = getattr(licensed, 'stt_document', None) == 'approved'

        # 2) Pagamento confirmado? (usa atalho por data; se não houver, verifica no modelo de adesão)
        paid_ok = bool(getattr(licensed, 'dtt_payment_received', None))
        if not paid_ok:
            try:
                from plans.models import PlanAdesion
                paid_ok = PlanAdesion.objects.filter(
                    licensed=licensed.user,
                    ind_payment_status='confirmed'
                ).exists()
            except Exception:
                paid_ok = False

        desired_active = bool(docs_ok and paid_ok)

        # Atualiza somente se necessário
        update_fields = []
        if getattr(licensed, 'stt_record', None) != desired_active:
            licensed.stt_record = desired_active
            update_fields.append('stt_record')

        if desired_active and not getattr(licensed, 'dtt_activation', None):
            licensed.dtt_activation = timezone.now()
            update_fields.append('dtt_activation')

        if update_fields:
            licensed.save(update_fields=update_fields)
            return True
        return False
    except Exception:
        # Em caso de qualquer erro, não bloquear fluxo do chamador
        return False


