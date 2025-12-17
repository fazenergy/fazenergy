from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from finance.models import WithdrawRequest, VirtualAccount, Transaction, PixConfig, WithdrawRequestLog
from .sicoob_pix import SicoobPixClient


@dataclass
class WithdrawProcessResult:
    ok: bool
    status: str
    message: str
    provider_payload: Optional[Dict] = None


def _is_withdraw_allowed_now(now=None) -> bool:
    """Valida se estamos dentro da janela permitida para solicitar/processar saques.

    Regras configuráveis (opcionais) em settings.py:
    - WITHDRAW_ALLOWED_DAY_RANGE: string "start-end" de dias do mês (ex.: "1-5").
      Se ausente, permite qualquer dia.
    - WITHDRAW_ALLOWED_DAYS: lista/tupla de inteiros [1..31] permitidos. Opcional.
    - WITHDRAW_ALLOWED_WEEKDAYS: lista/tupla de inteiros [0..6] (segunda=0) permitidos. Opcional.
    """
    from datetime import datetime

    now = now or timezone.localtime()

    # Dia do mês por intervalo
    day_range = getattr(settings, "WITHDRAW_ALLOWED_DAY_RANGE", None)
    if isinstance(day_range, str) and "-" in day_range:
        try:
            start_s, end_s = day_range.split("-", 1)
            start, end = int(start_s), int(end_s)
            if not (start <= now.day <= end):
                return False
        except Exception:
            pass

    # Dias específicos do mês
    allowed_days = getattr(settings, "WITHDRAW_ALLOWED_DAYS", None)
    if allowed_days:
        try:
            if now.day not in set(int(x) for x in allowed_days):
                return False
        except Exception:
            pass

    # Dias da semana
    allowed_weekdays = getattr(settings, "WITHDRAW_ALLOWED_WEEKDAYS", None)
    if allowed_weekdays:
        try:
            if now.weekday() not in set(int(x) for x in allowed_weekdays):
                return False
        except Exception:
            pass

    return True


def process_withdraw_request(req: WithdrawRequest, *, actor_username: str = "system", bypass_window: bool = False) -> WithdrawProcessResult:
    """Processa a solicitação de saque via PIX Sicoob, debitando saldo e atualizando status.

    Fluxo:
    1) Valida status pendente e janela de saque permitida.
    2) Debita saldo disponível (amount + fee + tax) e cria Transaction (débit).
    3) Dispara pagamento PIX (chave = CPF/CNPJ do titular da conta bancária).
    4) Atualiza status para paid ou rejected conforme retorno do provedor.
    """
    if req.status != "pending":
        return WithdrawProcessResult(False, req.status, "Solicitação não está pendente.")

    if not bypass_window and not _is_withdraw_allowed_now():
        return WithdrawProcessResult(False, req.status, "Fora do período permitido para saque.")

    # Dados necessários
    bank = req.bank_account
    if not bank:
        return WithdrawProcessResult(False, req.status, "Conta bancária não encontrada.")

    # Total debitado do saldo disponível: valor solicitado + taxas + impostos estimados
    total = (req.amount or Decimal("0")) + (req.fee_amount or Decimal("0")) + (req.tax_amount or Decimal("0"))

    with transaction.atomic():
        # Bloqueio e débito em conta virtual
        va = VirtualAccount.objects.select_for_update().filter(licensed=req.licensed).first()
        if not va:
            return WithdrawProcessResult(False, req.status, "Conta virtual inexistente.")

        if (va.balance_available or Decimal("0")) < total:
            return WithdrawProcessResult(False, req.status, "Saldo insuficiente no momento do processamento.")

        # Marca processing antes da chamada externa
        req.status = "processing"
        req.note = (req.note or "") + f"\nProcessado por {actor_username} em {timezone.localtime().strftime('%d/%m/%Y %H:%M')}"
        req.processed_at = None
        req.save(update_fields=["status", "note"])

        # Debita saldo e registra transação (saída da conta virtual)
        va.balance_available = (va.balance_available or Decimal("0")) - total
        va.save(update_fields=["balance_available", "dtt_update"])

        tx = Transaction.objects.create(
            virtual_account=va,
            product="Solicitação de Saque",
            description=f"Saque #{req.id} via PIX (total inclui taxas/impostos).",
            status="released",
            operation="debit",
            amount=total,
            is_processed=True,
            reference_date=timezone.localdate(),
        )

        # Chamada ao provedor PIX (Sicoob)
        # Carrega configuração PIX (overrides de env)
        pix_cfg = PixConfig.objects.filter(active=True).first()
        overrides = {}
        if pix_cfg:
            overrides = {
                'api_base_url': pix_cfg.api_base_url,
                'oauth_url': pix_cfg.oauth_url,
                'client_id': pix_cfg.client_id,
                'client_secret': pix_cfg.client_secret,
                'access_token': pix_cfg.access_token,
                'cert_path': pix_cfg.cert_path,
                'key_path': pix_cfg.key_path,
            }
        client = SicoobPixClient(overrides=overrides)
        # Usamos CPF/CNPJ do titular como chave PIX
        key = (bank.account_holder_cpf_cnpj or "").replace(".", "").replace("-", "").replace("/", "")
        name = bank.account_holder_name or "Recebedor"
        result = client.pay_pix_by_cpf_cnpj(amount=str(req.amount), cpf_cnpj=key, name=name)

        if not result.get("ok"):
            # Reversão lógica: recredita o saldo disponível e marca como rejected
            va.balance_available = (va.balance_available or Decimal("0")) + total
            va.save(update_fields=["balance_available", "dtt_update"])
            req.status = "rejected"
            req.processed_at = timezone.now()
            err = result.get("error") or {}
            req.note = (req.note or "") + f"\nFalha PIX: {err}"
            req.save(update_fields=["status", "processed_at", "note"])
            try:
                WithdrawRequestLog.objects.create(
                    withdraw_request=req,
                    action='processed_rejected',
                    note=f"Falha PIX: {err}",
                )
            except Exception:
                pass
            return WithdrawProcessResult(False, req.status, "Falha no pagamento PIX.", provider_payload=err)

        # Sucesso
        req.status = "paid"
        req.processed_at = timezone.now()
        req.note = (req.note or "") + f"\nPIX efetuado com sucesso."
        req.save(update_fields=["status", "processed_at", "note"])
        try:
            WithdrawRequestLog.objects.create(
                withdraw_request=req,
                action='processed_paid',
                note="PIX efetuado com sucesso.",
            )
        except Exception:
            pass

        return WithdrawProcessResult(True, req.status, "Saque pago com sucesso.", provider_payload=result.get("data"))


